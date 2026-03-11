// ===== Firebase init =====
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// Root reference for the survey
const SURVEY = db.collection('surveys').doc('main');

// ===== Name normalization =====
function normalizeName(raw) {
  return raw.trim().toLowerCase().replace(/\s+/g, ' ');
}

// ===== Session helpers =====
// After name submit, we store the display name and its normalized form.
// No tokens, no isTeacher — admin access is handled separately via ADMIN_PASSWORD.
const Session = {
  set(name) {
    sessionStorage.setItem('name',           name);
    sessionStorage.setItem('normalizedName', normalizeName(name));
  },
  get name()           { return sessionStorage.getItem('name'); },
  get normalizedName() { return sessionStorage.getItem('normalizedName'); },
  setAdmin()           { sessionStorage.setItem('isAdmin', '1'); },
  get isAdmin()        { return sessionStorage.getItem('isAdmin') === '1'; },
  clear()              { sessionStorage.clear(); },
  require() {
    if (!this.name) { window.location.href = 'index.html'; return false; }
    return true;
  }
};

// ===== UI helpers =====
function showAlert(msg, type = 'info') {
  const box = document.getElementById('alerts');
  if (!box) return;
  const el = document.createElement('div');
  el.className = `alert alert-${type}`;
  el.textContent = msg;
  box.appendChild(el);
  setTimeout(() => el.remove(), 5000);
}

function loading(show, btnId) {
  const btn = btnId ? document.getElementById(btnId) : null;
  if (btn) btn.disabled = show;
  const spinner = document.getElementById('spinner');
  if (spinner) spinner.style.display = show ? 'block' : 'none';
}

// ===== Villages data =====
// Exactly 20 entries. "Село Колочава" is pinned first.
const VILLAGES = [
  { name: "Село Колочава",       desc: "Туристична перлина Закарпаття з дев'ятьма музеями просто неба, батьківщина легендарного Миколи Шугая — визнане найкращим туристичним селом України" },
  { name: "Синевирська Поляна",  desc: "Мальовниче гірське село біля озера Синевир у Міжгірському районі" },
  { name: "Ужок",                desc: "Старовинне бойківське село на перевалі Ужоцький, з фортецею та дерев'яною церквою" },
  { name: "Лумшори",             desc: "Курортне село з термальними та сірководневими джерелами у Перечинському районі" },
  { name: "Шаян",                desc: "Бальнеологічний курорт з мінеральними джерелами поблизу Хуста" },
  { name: "Поляна",              desc: "Відомий санаторно-курортний центр з мінеральними водами типу «Нафтуся»" },
  { name: "Лазещина",            desc: "Гірськолижний курорт у верхів'ях Чорної Тиси, ворота до Чорногірського хребта" },
  { name: "Солотвино",           desc: "Унікальне село з соляними озерами та старовинними соляними шахтами" },
  { name: "Ділове",              desc: "Географічний центр Європи, розташований на березі Тиси" },
  { name: "Великий Бичків",      desc: "Мальовниче село в долині Тиси, відправна точка для сплавів річкою" },
  { name: "Кобилецька Поляна",   desc: "Гірське село в Рахівському районі з традиційним гуцульським побутом" },
  { name: "Усть-Чорна",          desc: "Тихе лісове село в долині Чорної Тиси, популярне серед любителів екотуризму" },
  { name: "Тур'я Пасіка",        desc: "Унікальне село з термальним озером — природним басейном серед Карпатських гір" },
  { name: "Дубове",              desc: "Мальовниче гуцульське село на річці Тересва з багатою фольклорною спадщиною" },
  { name: "Нижній Бистрий",      desc: "Тихе закарпатське село біля Хуста зі збереженою народною архітектурою" },
  { name: "Широкий Луг",         desc: "Мальовниче село в долині Тересви, точка старту для походів у Свидовецький масив" },
  { name: "Квасово",             desc: "Курортне село з мінеральними джерелами типу «Боржомі» в Берегівському районі" },
  { name: "Негровець",           desc: "Мальовниче гірське село у Міжгірському районі, відоме широкими альпійськими луками та незайманою природою Карпат" },
  { name: "Синевир",             desc: "Гірське село поруч із однойменним високогірним озером — природною реліктовою пам'яткою та символом Закарпаття" },
  { name: "Мерешор",             desc: "Тихе закарпатське село в Рахівському районі на берегах Білої Тиси з автентичним гуцульським колоритом" },
];
