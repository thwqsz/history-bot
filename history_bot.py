from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import random

# Хранилище пользовательских состояний
user_states = {}

# Вопросы для "Русская рулетка"
roulette_questions = {
    "🇫🇷 Франция": [
        {
            "question": "Когда Франция начала строить свой первый ядерный реактор?",
            "options": ["1945", "1948", "1951"],
            "answer": "1948"
        }
    ],
    "🇺🇸 США": [
        {
            "question": "В каком году США сбросили первую атомную бомбу?",
            "options": ["1943", "1945", "1947"],
            "answer": "1945"
        }
    ]
}

# Вопросы для теста
test_questions = {
    "🇫🇷 Франция": [
        {
            "question": "Когда был создан скоростной поезд TGV?",
            "options": ["1960-е", "1970-е", "1980-е"],
            "answer": "1970-е"
        },
        {
            "question": "Какая компания производила истребители Mirage?",
            "options": ["Airbus", "Dassault", "Renault"],
            "answer": "Dassault"
        }
    ],
    "🇺🇸 США": [
        {
            "question": "Когда началась программа Apollo?",
            "options": ["1961", "1965", "1969"],
            "answer": "1961"
        },
        {
            "question": "Кто был президентом США в 1963 году?",
            "options": ["Линдон Джонсон", "Джон Кеннеди", "Ричард Никсон"],
            "answer": "Джон Кеннеди"
        }
    ]
}

# Главное меню
main_menu_keyboard = ReplyKeyboardMarkup(
    [["📋 Тест", "☠️ Русская рулетка"],
     ["🏫 Вузы", "⚙️ Технологии", "🏢 Компании"],
     ["🔙 Назад"]],
    resize_keyboard=True
)

# Меню выбора страны (7 стран)
countries_keyboard = ReplyKeyboardMarkup(
    [
        ["🇫🇷 Франция", "🇮🇳 Индия", "🇵🇱 Польша"],
        ["🇩🇪 Германия", "🇺🇸 США", "🇬🇧 Великобритания"],
        ["🇨🇳 Китай"]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Выбери страну:", reply_markup=countries_keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Обработка кнопки "Назад"
    if text == "🔙 Назад":
        if "current_question" in user_states.get(user_id, {}):
            del user_states[user_id]["current_question"]
        if "test" in user_states.get(user_id, {}):
            del user_states[user_id]["test"]
        if "current_category" in user_states.get(user_id, {}):
            del user_states[user_id]["current_category"]
        if "country" in user_states.get(user_id, {}):
            del user_states[user_id]
            await update.message.reply_text("Выберите страну:", reply_markup=countries_keyboard)
            return

        await update.message.reply_text("Вы вернулись в главное меню. Выберите действие:", reply_markup=main_menu_keyboard)
        return

    # Выбор страны
    all_countries = ["🇫🇷 Франция", "🇮🇳 Индия", "🇵🇱 Польша", "🇩🇪 Германия", "🇺🇸 США",
                     "🇬🇧 Великобритания", "🇨🇳 Китай"]

    if text in all_countries:
        user_states[user_id] = {"country": text}
        await update.message.reply_text(f"Вы выбрали {text}. Теперь выбери действие:", reply_markup=main_menu_keyboard)
        return

    # Если пользователь не выбрал страну
    if user_id not in user_states:
        await update.message.reply_text("Сначала выбери страну:", reply_markup=countries_keyboard)
        return

    country = user_states[user_id]["country"]

    if text == "☠️ Русская рулетка":
        if country not in roulette_questions:
            await update.message.reply_text("Извините, для этой страны пока нет вопросов.")
            return
        question = random.choice(roulette_questions[country])
        user_states[user_id]["current_question"] = question

        keyboard = ReplyKeyboardMarkup([[opt] for opt in question["options"]] + [["🔙 Назад"]], resize_keyboard=True)
        await update.message.reply_text(question["question"], reply_markup=keyboard)
        return

    if text == "📋 Тест":
        if country not in test_questions:
            await update.message.reply_text("Извините, для этой страны пока нет теста.")
            return
        questions = random.sample(test_questions[country], k=min(5, len(test_questions[country])))
        user_states[user_id]["test"] = {
            "questions": questions,
            "current_index": 0,
            "score": 0
        }
        q = questions[0]
        keyboard = ReplyKeyboardMarkup([[opt] for opt in q["options"]] + [["🔙 Назад"]], resize_keyboard=True)
        await update.message.reply_text(f"Вопрос 1: {q['question']}", reply_markup=keyboard)
        return

    if "current_question" in user_states.get(user_id, {}):
        question = user_states[user_id]["current_question"]
        if text in question["options"]:
            if text == question["answer"]:
                await update.message.reply_text("✅ Верно!")
            else:
                await update.message.reply_text(f"❌ Неверно. Правильный ответ: {question['answer']}")
            del user_states[user_id]["current_question"]
            await update.message.reply_text("Выберите следующее действие:", reply_markup=main_menu_keyboard)
            return

    if "test" in user_states.get(user_id, {}):
        test_data = user_states[user_id]["test"]
        current_index = test_data["current_index"]
        current_q = test_data["questions"][current_index]

        if text in current_q["options"]:
            if text == current_q["answer"]:
                test_data["score"] += 1
                await update.message.reply_text("✅ Верно!")
            else:
                await update.message.reply_text(f"❌ Неверно. Правильный ответ: {current_q['answer']}")

            test_data["current_index"] += 1

            if test_data["current_index"] < len(test_data["questions"]):
                next_q = test_data["questions"][test_data["current_index"]]
                keyboard = ReplyKeyboardMarkup([[opt] for opt in next_q["options"]] + [["🔙 Назад"]], resize_keyboard=True)
                await update.message.reply_text(
                    f"Вопрос {test_data['current_index'] + 1}: {next_q['question']}",
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    f"🧮 Тест завершён! Результат: {test_data['score']} из {len(test_data['questions'])}",
                    reply_markup=main_menu_keyboard
                )
                del user_states[user_id]["test"]
            return

    await update.message.reply_text("Пожалуйста, выбери действие из меню.")

if __name__ == "__main__":
    TOKEN = "7742146854:AAEg9VGTTpHCC5d46sn_fEPHuyIDfnyMbNw"  # ← Вставь сюда свой токен от @BotFather
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()