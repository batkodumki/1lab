import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'zakarpattia-villages-2024-secret')

DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    token = request.form.get('token', '').strip()
    if not token:
        flash('Будь ласка, введіть токен доступу.', 'error')
        return redirect(url_for('index'))

    expert = query_db('SELECT * FROM experts WHERE token = ?', [token], one=True)
    if not expert:
        flash('Невірний токен. Перевірте та спробуйте знову.', 'error')
        return redirect(url_for('index'))

    session['expert_id'] = expert['id']
    session['expert_name'] = expert['name']
    session['is_teacher'] = bool(expert['is_teacher'])

    if expert['is_teacher']:
        return redirect(url_for('admin'))

    if expert['voted']:
        flash('Ви вже проголосували. Дякуємо за участь!', 'info')
        return redirect(url_for('results'))

    return redirect(url_for('vote'))


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'expert_id' not in session:
        flash('Спочатку увійдіть за допомогою токена.', 'error')
        return redirect(url_for('index'))

    expert_id = session['expert_id']
    expert = query_db('SELECT * FROM experts WHERE id = ?', [expert_id], one=True)

    if expert['voted']:
        flash('Ви вже проголосували.', 'info')
        return redirect(url_for('results'))

    if session.get('is_teacher'):
        return redirect(url_for('admin'))

    objects = query_db('SELECT * FROM objects ORDER BY name')

    if request.method == 'POST':
        selections = []
        for rank in range(1, 4):
            obj_id = request.form.get(f'rank_{rank}')
            if obj_id:
                selections.append((int(obj_id), rank))

        if len(selections) < 3:
            flash('Будь ласка, оберіть рівно 3 об\'єкти та розставте їх за пріоритетом.', 'error')
            return render_template('vote.html', objects=objects)

        ids = [s[0] for s in selections]
        if len(ids) != len(set(ids)):
            flash('Не можна обирати одне село кілька разів.', 'error')
            return render_template('vote.html', objects=objects)

        for obj_id, rank in selections:
            execute_db(
                'INSERT INTO votes (expert_id, object_id, rank) VALUES (?, ?, ?)',
                [expert_id, obj_id, rank]
            )

        execute_db('UPDATE experts SET voted = 1 WHERE id = ?', [expert_id])
        flash('Дякуємо! Ваш голос збережено анонімно.', 'success')
        return redirect(url_for('results'))

    return render_template('vote.html', objects=objects)


@app.route('/results')
def results():
    objects = query_db('SELECT * FROM objects ORDER BY name')
    total_experts = query_db(
        'SELECT COUNT(*) as cnt FROM experts WHERE is_teacher = 0', one=True
    )['cnt']
    voted_count = query_db(
        'SELECT COUNT(*) as cnt FROM experts WHERE voted = 1 AND is_teacher = 0', one=True
    )['cnt']

    # Aggregate scores: rank 1 = 3 pts, rank 2 = 2 pts, rank 3 = 1 pt
    scores = query_db('''
        SELECT o.id, o.name, o.description,
               SUM(CASE WHEN v.rank = 1 THEN 3
                        WHEN v.rank = 2 THEN 2
                        WHEN v.rank = 3 THEN 1
                        ELSE 0 END) as score,
               COUNT(v.id) as mention_count,
               SUM(CASE WHEN v.rank = 1 THEN 1 ELSE 0 END) as first_place,
               SUM(CASE WHEN v.rank = 2 THEN 1 ELSE 0 END) as second_place,
               SUM(CASE WHEN v.rank = 3 THEN 1 ELSE 0 END) as third_place
        FROM objects o
        LEFT JOIN votes v ON o.id = v.object_id
        GROUP BY o.id
        ORDER BY score DESC, mention_count DESC
    ''')

    # Core A^2: objects that were selected by at least one expert
    core = [s for s in scores if s['mention_count'] > 0]

    return render_template(
        'results.html',
        scores=scores,
        core=core,
        total_experts=total_experts,
        voted_count=voted_count,
        objects=objects
    )


@app.route('/admin')
def admin():
    if 'expert_id' not in session or not session.get('is_teacher'):
        flash('Доступ лише для викладача.', 'error')
        return redirect(url_for('index'))

    experts = query_db(
        'SELECT * FROM experts WHERE is_teacher = 0 ORDER BY name'
    )
    total_experts = len(experts)
    voted_count = sum(1 for e in experts if e['voted'])

    # Full protocol: each expert's votes (anonymous display — show expert number, not name)
    protocol = query_db('''
        SELECT e.id as expert_id, e.name as expert_name,
               v.rank, o.name as object_name
        FROM experts e
        JOIN votes v ON e.id = v.expert_id
        JOIN objects o ON v.object_id = o.id
        WHERE e.is_teacher = 0
        ORDER BY e.id, v.rank
    ''')

    # Group protocol by expert
    protocol_by_expert = {}
    for row in protocol:
        eid = row['expert_id']
        if eid not in protocol_by_expert:
            protocol_by_expert[eid] = {
                'name': row['expert_name'],
                'votes': []
            }
        protocol_by_expert[eid]['votes'].append({
            'rank': row['rank'],
            'object_name': row['object_name']
        })

    # Aggregate results
    scores = query_db('''
        SELECT o.id, o.name, o.description,
               SUM(CASE WHEN v.rank = 1 THEN 3
                        WHEN v.rank = 2 THEN 2
                        WHEN v.rank = 3 THEN 1
                        ELSE 0 END) as score,
               COUNT(v.id) as mention_count,
               SUM(CASE WHEN v.rank = 1 THEN 1 ELSE 0 END) as first_place,
               SUM(CASE WHEN v.rank = 2 THEN 1 ELSE 0 END) as second_place,
               SUM(CASE WHEN v.rank = 3 THEN 1 ELSE 0 END) as third_place
        FROM objects o
        LEFT JOIN votes v ON o.id = v.object_id
        GROUP BY o.id
        ORDER BY score DESC, mention_count DESC
    ''')

    core = [s for s in scores if s['mention_count'] > 0]

    # Expert tokens for distribution (only teacher can see this)
    expert_tokens = query_db(
        'SELECT id, name, token, voted FROM experts WHERE is_teacher = 0 ORDER BY name'
    )

    return render_template(
        'admin.html',
        experts=experts,
        total_experts=total_experts,
        voted_count=voted_count,
        protocol_by_expert=protocol_by_expert,
        scores=scores,
        core=core,
        expert_tokens=expert_tokens
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
