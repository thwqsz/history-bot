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
    "🇮🇳 Индия": [
        {
            "question": "В каком году была основана ISRO?",
            "options": ["1962", "1969", "1975"],
            "answer": "1969"
        }
    ],
    "🇵🇱 Польша": [
        {
            "question": "Когда был основан Варшавский университет технологии?",
            "options": ["1915", "1920", "1933"],
            "answer": "1915"
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
    "🇮🇳 Индия": [
        {
            "question": "Как назывался первый спутник Индии?",
            "options": ["Aryabhata", "Chandrayaan", "Vikram"],
            "answer": "Aryabhata"
        },
        {
            "question": "Когда была основана Tata Steel?",
            "options": ["1907", "1920", "1951"],
            "answer": "1907"
        }
    ],
    "🇵🇱 Польша": [
        {
            "question": "Когда Польша стала членом ООН?",
            "options": ["1945", "1956", "1961"],
            "answer": "1945"
        },
        {
            "question": "Кто был лидером движения «Солидарность»?",
            "options": ["Валесса", "Качиньский", "Туск"],
            "answer": "Валесса"
        }
    ]
}

# Главное меню
main_menu_keyboard = ReplyKeyboardMarkup(
    [["📋 Тест", "☠️ Русская рулетка"],
     ["🏫 Вузы", "⚙️ Технологии", "🏢 Компании"]],
    resize_keyboard=True
)

# Меню выбора страны
countries_keyboard = ReplyKeyboardMarkup(
    [["🇫🇷 Франция", "🇮🇳 Индия", "🇵🇱 Польша"]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Выбери страну:", reply_markup=countries_keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Выбор страны
    if text in ["🇫🇷 Франция", "🇮🇳 Индия", "🇵🇱 Польша"]:
        user_states[user_id] = {"country": text}
        await update.message.reply_text(f"Вы выбрали {text}. Теперь выбери действие:", reply_markup=main_menu_keyboard)
        return

    # Если пользователь ещё не выбрал страну
    if user_id not in user_states:
        await update.message.reply_text("Сначала выбери страну.", reply_markup=countries_keyboard)
        return

    country = user_states[user_id]["country"]

    # Русская рулетка
    if text == "☠️ Русская рулетка":
        question = random.choice(roulette_questions[country])
        user_states[user_id]["current_question"] = question

        options = question["options"]
        keyboard = ReplyKeyboardMarkup([[opt] for opt in options], resize_keyboard=True)
        await update.message.reply_text(question["question"], reply_markup=keyboard)
        return

    # Тест
    if text == "📋 Тест":
        questions = random.sample(test_questions[country], k=min(5, len(test_questions[country])))

        user_states[user_id]["test"] = {
            "questions": questions,
            "current_index": 0,
            "score": 0
        }

        q = questions[0]
        keyboard = ReplyKeyboardMarkup([[opt] for opt in q["options"]], resize_keyboard=True)
        await update.message.reply_text(f"Вопрос 1: {q['question']}", reply_markup=keyboard)
        return

    # Проверка ответа "Русская рулетка"
    if "current_question" in user_states[user_id]:
        question = user_states[user_id]["current_question"]
        if text in question["options"]:
            if text == question["answer"]:
                await update.message.reply_text("✅ Верно!")
            else:
                await update.message.reply_text(f"❌ Неверно. Правильный ответ: {question['answer']}")
            del user_states[user_id]["current_question"]
            await update.message.reply_text("Выберите следующее действие:", reply_markup=main_menu_keyboard)
            return

    # Проверка ответа в тесте
    if "test" in user_states[user_id]:
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
                keyboard = ReplyKeyboardMarkup([[opt] for opt in next_q["options"]], resize_keyboard=True)
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
    import os

    TOKEN = "7742146854:AAEg9VGTTpHCC5d46sn_fEPHuyIDfnyMbNw"  # ← Замени на свой токен

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()
