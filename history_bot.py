from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import random
import json
import os
from pathlib import Path

# Создаем директорию для данных, если её нет
Path("data").mkdir(exist_ok=True)

def load_country_data(country_code):
    """Загружает данные страны из JSON файла"""
    try:
        file_path = f"data/{country_code}/info.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def format_topic_info(topic):
    """Форматирует информацию о теме для вывода"""
    result = [topic['title'], topic['description']]
    
    if 'founded' in topic:
        result.append(f"Год основания: {topic['founded']}")
    
    if 'details' in topic:
        result.append("\nПодробности:")
        result.extend([f"• {detail}" for detail in topic['details']])
    
    if 'achievements' in topic:
        result.append("\nДостижения:")
        result.extend([f"• {achievement}" for achievement in topic['achievements']])
    
    return "\n".join(result)

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

# Информация по категориям для каждой страны
country_info = {
    "🇫🇷 Франция": {
        "🏫 Вузы": [
            "🎓 École Polytechnique\nГод основания: 1794\nОдин из самых престижных технических вузов Франции\nИзвестен сильной математической школой",
            "🎓 Сорбонна\nГод основания: 1257\nСтарейший университет Франции\nИсторический центр французского образования",
            "🎓 École Normale Supérieure\nЭлитное высшее учебное заведение\nСпециализируется на фундаментальных науках"
        ],
        "⚙️ Технологии": [
            "⚡ Ядерная энергетика\n56 действующих реакторов\n70% электроэнергии страны",
            "🚄 TGV (High-speed rail)\nСкорость до 320 км/ч\nРеволюция в железнодорожном транспорте",
            "✈️ Airbus\nЕвропейский лидер авиастроения\nИнновации в гражданской авиации"
        ],
        "🏢 Компании": [
            "🛫 Dassault Aviation\nПроизводитель военных и гражданских самолетов\nСоздатель истребителей Mirage и Rafale",
            "⚡ EDF\nКрупнейшая энергетическая компания\nЛидер в ядерной энергетике",
            "🚗 Renault\nПионер автомобилестроения\nИнновации в электромобилях"
        ]
    },
    "🇺🇸 США": {
        "🏫 Вузы": [
            "🎓 MIT\nГод основания: 1861\nМировой лидер в технологическом образовании",
            "🎓 Stanford University\nСердце Кремниевой долины\nЛидер в компьютерных науках",
            "🎓 Harvard University\nСтарейший вуз США\nПризнанный лидер в науке и образовании"
        ],
        "⚙️ Технологии": [
            "🚀 NASA\nПрограмма Apollo\nМарсианские роверы\nКосмический телескоп Hubble",
            "💻 Silicon Valley\nЦентр мировой IT-индустрии\nРеволюционные технологии",
            "🧬 Биотехнологии\nПередовые исследования в генетике\nИнновационные медицинские технологии"
        ],
        "🏢 Компании": [
            "🚀 SpaceX\nРеволюция в космической индустрии\nМногоразовые ракеты-носители",
            "🖥️ Apple\nРеволюция в персональных устройствах\nИнновационный дизайн",
            "🤖 Boston Dynamics\nПередовая робототехника\nРеволюционные разработки"
        ]
    }
}

# Функция для создания клавиатуры с темами
def create_topics_keyboard(topics):
    print("Создание клавиатуры для тем:")  # Отладочное сообщение
    keyboard_buttons = []
    for topic in topics:
        title = topic.split('\n')[0]
        print(f"Добавляю кнопку: {title}")  # Отладочное сообщение
        keyboard_buttons.append([title])
    keyboard_buttons.append(["🔙 Назад"])
    print(f"Итоговая клавиатура: {keyboard_buttons}")  # Отладочное сообщение
    return ReplyKeyboardMarkup(keyboard_buttons, resize_keyboard=True)

# Главное меню
main_menu_keyboard = ReplyKeyboardMarkup(
    [["📋 Тест", "☠️ Русская рулетка"],
     ["🏫 Вузы", "⚙️ Технологии", "🏢 Компании"],
     ["🔙 Назад"]],
    resize_keyboard=True
)

# Меню выбора страны
countries_keyboard = ReplyKeyboardMarkup(
    [
        ["🇫🇷 Франция", "🇮🇳 Индия", "🇵🇱 Польша"],
        ["🇩🇪 Германия", "🇺🇸 США", "🇬🇧 Великобритания"],
        ["🇨🇳 Китай"]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Выберите страну:", reply_markup=countries_keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Обработка кнопки "Назад"
    if text == "🔙 Назад":
        if "category" in user_states.get(user_id, {}):
            # Если мы в конкретной теме или списке тем, возвращаемся к выбору рубрики
            del user_states[user_id]["category"]
            await update.message.reply_text(
                f"Вы вернулись в главное меню {user_states[user_id]['country']}. Выберите рубрику:",
                reply_markup=main_menu_keyboard
            )
            return
        if "country" in user_states.get(user_id, {}):
            # Возвращаемся к выбору страны
            del user_states[user_id]
            await update.message.reply_text("Выберите страну:", reply_markup=countries_keyboard)
            return
        await update.message.reply_text("Выберите страну:", reply_markup=countries_keyboard)
        return

    # Выбор страны
    all_countries = ["🇫🇷 Франция", "🇮🇳 Индия", "🇵🇱 Польша", "🇩🇪 Германия", "🇺🇸 США",
                     "🇬🇧 Великобритания", "🇨🇳 Китай"]
    country_codes = {
        "🇫🇷 Франция": "france",
        "🇺🇸 США": "usa",
        # Добавьте коды для других стран
    }

    if text in all_countries:
        country_code = country_codes.get(text)
        if country_code:
            country_data = load_country_data(country_code)
            if country_data:
                user_states[user_id] = {
                    "country": text,
                    "country_code": country_code,
                    "data": country_data
                }
                await update.message.reply_text(
                    f"Вы выбрали {text}. Теперь выберите действие:",
                    reply_markup=main_menu_keyboard
                )
                return
        await update.message.reply_text(
            "Извините, информация об этой стране пока недоступна.",
            reply_markup=countries_keyboard
        )
        return

    # Если пользователь не выбрал страну
    if user_id not in user_states:
        await update.message.reply_text("Сначала выберите страну:", reply_markup=countries_keyboard)
        return

    country = user_states[user_id]["country"]

    # Обработка выбора категории
    categories = {
        "🏫 Вузы": "universities",
        "⚙️ Технологии": "technologies",
        "🏢 Компании": "companies"
    }

    if text in categories:
        category = categories[text]
        country_data = user_states[user_id]["data"]
        
        if category in country_data:
            topics = country_data[category]
            keyboard = [[topic['title']] for topic in topics]
            keyboard.append(["🔙 Назад"])
            user_states[user_id]["category"] = category
            
            await update.message.reply_text(
                "Выберите тему:",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
            return
        
        await update.message.reply_text(
            f"Извините, информация о {text.lower()} этой страны пока недоступна.",
            reply_markup=main_menu_keyboard
        )
        return

    # Обработка выбора конкретной темы
    if "category" in user_states[user_id]:
        category = user_states[user_id]["category"]
        country_data = user_states[user_id]["data"]
        topics = country_data[category]

        for topic in topics:
            if topic['title'] == text:
                keyboard = [[t['title']] for t in topics]
                keyboard.append(["🔙 Назад"])
                
                await update.message.reply_text(
                    topic['text'],
                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                )
                return

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

    await update.message.reply_text("Пожалуйста, выберите действие из меню.")

if __name__ == "__main__":
    TOKEN = "7742146854:AAEg9VGTTpHCC5d46sn_fEPHuyIDfnyMbNw"  # ← Вставь сюда свой токен от @BotFather
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()