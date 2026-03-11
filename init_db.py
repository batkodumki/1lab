"""
Ініціалізація бази даних.
Створює таблиці та заповнює початковими даними:
  - 20 сіл Закарпаття (об'єкти)
  - 20 експертів + 1 викладач
"""
import sqlite3
import os
import secrets

DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS objects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS experts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    token      TEXT NOT NULL UNIQUE,
    is_teacher INTEGER NOT NULL DEFAULT 0,
    voted      INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS votes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    expert_id INTEGER NOT NULL REFERENCES experts(id),
    object_id INTEGER NOT NULL REFERENCES objects(id),
    rank      INTEGER NOT NULL CHECK(rank BETWEEN 1 AND 3),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

# 20 найкращих сіл Закарпаття
VILLAGES = [
    ("Синевирська Поляна",
     "Мальовниче гірське село біля озера Синевир у Міжгірському районі"),
    ("Колочава",
     "Унікальне село з дев'ятьма музеями просто неба, відоме своїм самобутнім укладом"),
    ("Ужок",
     "Старовинне бойківське село на перевалі Ужоцький, з фортецею та дерев'яною церквою"),
    ("Лумшори",
     "Курортне село з термальними та сірководневими джерелами у Перечинському районі"),
    ("Шаян",
     "Бальнеологічний курорт з мінеральними джерелами поблизу Хуста"),
    ("Поляна",
     "Відомий санаторно-курортний центр з мінеральними водами типу «Нафтуся»"),
    ("Лазещина",
     "Гірськолижний курорт у верхів'ях Чорної Тиси, ворота до Чорногірського хребта"),
    ("Солотвино",
     "Унікальне село з соляними озерами та старовинними соляними шахтами"),
    ("Ділове",
     "Географічний центр Європи, розташований на березі Тиси"),
    ("Великий Бичків",
     "Мальовниче село в долині Тиси, відправна точка для сплавів річкою"),
    ("Кобилецька Поляна",
     "Гірське село в Рахівському районі з традиційним гуцульським побутом"),
    ("Усть-Чорна",
     "Тихе лісове село в долині Чорної Тиси, популярне серед любителів екотуризму"),
    ("Тур'я Пасіка",
     "Унікальне село з термальним озером — природним басейном серед Карпатських гір"),
    ("Вишково",
     "Поліетнічне село на Хустщині з самобутньою архітектурою і традиціями"),
    ("Дубове",
     "Мальовниче гуцульське село на річці Тересва з багатою фольклорною спадщиною"),
    ("Нижній Бистрий",
     "Тихе закарпатське село біля Хуста з збереженою народною архітектурою"),
    ("Мирча",
     "Невелике виноградарське село в передгір'ях Закарпаття, відоме домашніми винами"),
    ("Широкий Луг",
     "Мальовниче село в долині Тересви, точка старту для походів у Свидовецький масив"),
    ("Квасово",
     "Курортне село з мінеральними джерелами типу «Боржомі» в Берегівському районі"),
    ("Іршавська Поляна",
     "Мальовниче лісове передгірське село з розвиненим зеленим туризмом"),
]

# 20 експертів + 1 викладач
EXPERT_NAMES = [
    "Іванченко Олексій",
    "Петренко Марія",
    "Коваленко Дмитро",
    "Бондаренко Ольга",
    "Мельник Василь",
    "Шевченко Наталія",
    "Кравченко Андрій",
    "Лисенко Тетяна",
    "Морозенко Ігор",
    "Гончаренко Людмила",
    "Тимошенко Роман",
    "Захаренко Ірина",
    "Павленко Сергій",
    "Романенко Оксана",
    "Савченко Микола",
    "Олійник Вікторія",
    "Яременко Богдан",
    "Клименко Анна",
    "Ткаченко Юрій",
    "Пилипенко Галина",
]


def init_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print(f"Видалено стару базу: {DATABASE}")

    conn = sqlite3.connect(DATABASE)
    conn.executescript(SCHEMA)

    # Вставка сіл
    conn.executemany(
        'INSERT INTO objects (name, description) VALUES (?, ?)',
        VILLAGES
    )

    # Вставка експертів
    tokens_info = []
    for name in EXPERT_NAMES:
        token = secrets.token_hex(4).upper()
        conn.execute(
            'INSERT INTO experts (name, token, is_teacher) VALUES (?, ?, 0)',
            (name, token)
        )
        tokens_info.append((name, token))

    # Викладач
    teacher_token = "TEACHER-" + secrets.token_hex(4).upper()
    conn.execute(
        'INSERT INTO experts (name, token, is_teacher) VALUES (?, ?, 1)',
        ("Викладач", teacher_token)
    )

    conn.commit()
    conn.close()

    print("=" * 55)
    print("База даних ініціалізована успішно!")
    print("=" * 55)
    print(f"\nТокен ВИКЛАДАЧА (зберігайте конфіденційно):")
    print(f"  {teacher_token}")
    print(f"\nТокени ЕКСПЕРТІВ (роздати кожному особисто):")
    for name, token in tokens_info:
        print(f"  {name:30s}  →  {token}")
    print("=" * 55)
    print(f"\nЗапустіть сервер:  python app.py")
    print(f"Відкрийте браузер: http://localhost:5000")


if __name__ == '__main__':
    init_db()
