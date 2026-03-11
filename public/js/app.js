// ===== Firebase init =====
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// ===== Session helpers =====
const Session = {
  set(token, name, isTeacher) {
    sessionStorage.setItem('token',     token);
    sessionStorage.setItem('name',      name);
    sessionStorage.setItem('isTeacher', isTeacher ? '1' : '0');
  },
  get token()     { return sessionStorage.getItem('token'); },
  get name()      { return sessionStorage.getItem('name'); },
  get isTeacher() { return sessionStorage.getItem('isTeacher') === '1'; },
  clear()         { sessionStorage.clear(); },
  require(page) {
    if (!this.token) { window.location.href = 'index.html'; return false; }
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
const VILLAGES = [
  { name: "Синевирська Поляна",  desc: "Мальовниче гірське село біля озера Синевир у Міжгірському районі" },
  { name: "Колочава",            desc: "Унікальне село з дев'ятьма музеями просто неба, відоме своїм самобутнім укладом" },
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
  { name: "Вишково",             desc: "Поліетнічне село на Хустщині з самобутньою архітектурою і традиціями" },
  { name: "Дубове",              desc: "Мальовниче гуцульське село на річці Тересва з багатою фольклорною спадщиною" },
  { name: "Нижній Бистрий",      desc: "Тихе закарпатське село біля Хуста зі збереженою народною архітектурою" },
  { name: "Мирча",               desc: "Невелике виноградарське село в передгір'ях Закарпаття, відоме домашніми винами" },
  { name: "Широкий Луг",         desc: "Мальовниче село в долині Тересви, точка старту для походів у Свидовецький масив" },
  { name: "Квасово",             desc: "Курортне село з мінеральними джерелами типу «Боржомі» в Берегівському районі" },
  { name: "Іршавська Поляна",    desc: "Мальовниче лісове передгірське село з розвиненим зеленим туризмом" },
];

const EXPERT_NAMES = [
  "Іванченко Олексій", "Петренко Марія",    "Коваленко Дмитро",
  "Бондаренко Ольга",  "Мельник Василь",    "Шевченко Наталія",
  "Кравченко Андрій",  "Лисенко Тетяна",    "Морозенко Ігор",
  "Гончаренко Людмила","Тимошенко Роман",   "Захаренко Ірина",
  "Павленко Сергій",   "Романенко Оксана",  "Савченко Микола",
  "Олійник Вікторія",  "Яременко Богдан",   "Клименко Анна",
  "Ткаченко Юрій",     "Пилипенко Галина",
];

function genToken(len = 8) {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  return Array.from({ length: len }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
}
