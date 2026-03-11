# Найкращі села Закарпаття — Система розподіленого голосування

Лабораторна робота №1 · Технології розподіленого введення даних

## Розгортання (покрокова інструкція)

### 1. Створити Firebase-проєкт
1. Відкрийте [console.firebase.google.com](https://console.firebase.google.com)
2. Натисніть **Add project** → назвіть проєкт (наприклад `villages-vote`)
3. Вимкніть Google Analytics (необов'язково) → **Create project**

### 2. Увімкнути Firestore
- У Firebase Console → **Build** → **Firestore Database** → **Create database**
- Оберіть **Start in test mode** → вибрати регіон (наприклад `europe-west1`) → **Enable**

### 3. Вставити конфігурацію
- Firebase Console → **Project Settings** (⚙️) → **Your apps** → **Web** (`</>`)
- Зареєструйте застосунок, скопіюйте об'єкт `firebaseConfig`
- Відкрийте файл `public/js/firebase-config.js` і замініть значення:

```js
const firebaseConfig = {
  apiKey:            "ваш-api-key",
  authDomain:        "ваш-project.firebaseapp.com",
  projectId:         "ваш-project-id",
  storageBucket:     "ваш-project.appspot.com",
  messagingSenderId: "123456789",
  appId:             "1:123:web:abc123"
};
```

### 4. Встановити Firebase CLI та задеплоїти
```bash
npm install -g firebase-tools
firebase login
firebase init          # обрати Hosting + Firestore; public dir = public
firebase deploy
```

Після деплою ви отримаєте посилання типу `https://villages-vote.web.app`.

### 5. Ініціалізувати базу даних
- Відкрийте `https://ваш-проєкт.web.app/setup.html`
- Натисніть **«Ініціалізувати базу даних»**
- Збережіть або роздрукуйте таблицю токенів — роздайте кожному студенту особисто

---

## Сторінки

| Сторінка | URL | Для кого |
|----------|-----|----------|
| Вхід | `/index.html` | Всі |
| Голосування | `/vote.html` | Студенти (після входу) |
| Результати | `/results.html` | Публічно |
| Протокол | `/admin.html` | Тільки викладач |
| Налаштування | `/setup.html` | Тільки викладач (одноразово) |

## Математична модель

- **n = 20** об'єктів (сіл), **k** експертів, **ν = 3** (МП — множинне порівняння)
- Кожен ЧК задає: A^ν_i = {a¹ ≻ a² ≻ a³}
- **Ядро A²** = ⋃_{j∈I} A^ν_j ⊆ A (об'єднання обраних підмножин)
- **Агрегація**: 1-е місце = 3 бали, 2-е = 2 бали, 3-є = 1 бал
