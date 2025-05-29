from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import random

# Клавиатуры
main_menu_keyboard = ReplyKeyboardMarkup(
    [["📋 Тест", "☠️ Русская рулетка"],
     ["🏫 Вузы", "⚙️ Технологии", "🏢 Компании"],
     ["🔙 Назад"]],
    resize_keyboard=True
)

countries_keyboard = ReplyKeyboardMarkup(
    [["🇭🇺 ВЕНГРИЯ", "🇮🇳 ИНДИЯ", "🇵🇱 ПОЛЬША"],
     ["🇹🇼 ТАЙВАНЬ", "🇫🇮 ФИНЛЯНДИЯ"]],
    resize_keyboard=True
)

# Хранилище пользовательских состояний
user_states = {}

# Импорт данных (вставлены прямо в код)
technology_info = {
    "🇭🇺 ВЕНГРИЯ": "🖥️ Primo — венгерский персональный компьютер социалистической эпохи\n\n"
                  "_Разработка: Институт компьютерных технологий и автоматизации Венгерской академии наук (MTA SZTAKI)_\n"
                  "Год выпуска: 1984\n\n"
                  "Primo — уникальный венгерский 8-битный персональный компьютер, созданный в условиях дефицита комплектующих "
                  "и ограничений социалистической экономики. Его разработка вдохновлялась британским Sinclair ZX Spectrum, но из-за "
                  "нехватки зарубежных микросхем инженерам пришлось проектировать плату с нуля и использовать доступные аналоги, например, "
                  "процессор U880 — советский клон Zilog Z80.\n\n"
                  "📌 Основные характеристики:\n"
                  "• 2,5 МГц, 16-48 КБ оперативной памяти, 16 КБ ПЗУ с BASIC\n"
                  "• Монохромная графика 256×192 пикселей с PAL-видеовыходом\n"
                  "• Клавиатура с ёмкостными «плоскими» клавишами\n"
                  "• Подключение бытового магнитофона для загрузки и сохранения программ\n\n"
                  "💡 Интересный факт:\n"
                  "Сборка первых 7000 Primo велась буквально на «кухонных столах». Компьютеры массово поставлялись в школы Венгрии.",

    "🇮🇳 ИНДИЯ": "🖥️ TDC — индийские мини-ЭВМ эпохи 'саморазвития'\n\n"
                "Разработка: ECIL (Electronics Corporation of India Limited), Хайдарабад\n"
                "Годы выпуска: 1973–1980-е\n\n"
                "TDC — серия индийских мини-ЭВМ, созданных на основе PDP-11 с полным локальным контролем схемотехники.\n\n"
                "📌 Основные модели:\n"
                "• TDC-12, TDC-316, TDC-332 для обороны и ядерной промышленности\n"
                "• Использовались в метеостанциях, банках, на транспорте\n\n"
                "💡 Факт:\n"
                "TDC-316 использовалась в BARC и стала учебной базой в вузах.\n\n"
                "🖥️ PARAM — первый индийский суперкомпьютер\n\n"
                "Разработка: C-DAC, Пуне\n"
                "Год выпуска: 1991\n\n"
                "Проект появился после отказа США в поставке Cray.\n"
                "📌 Характеристики:\n"
                "• RISC Inmos Transputer\n"
                "• ~1 GFlops\n"
                "• Экспорт: Россия, Германия, Сингапур\n\n"
                "💡 Название PARAM с санскрита — «абсолют»",

    "🇵🇱 ПОЛЬША": "🖥️ SAKO — первый польский язык программирования\n\n"
                 "Разработка: Польская академия наук\n"
                 "Годы: 1959–1960\n\n"
                 "SAKO предназначен для машин XYZ и ZAM-2, использует команды на польском языке.\n\n"
                 "📌 Особенности:\n"
                 "• Статическая адресация\n"
                 "• Компиляция через макроассемблер SAS-W\n"
                 "• Основное применение: инженерные расчёты\n\n"
                 "💡 Интересный факт:\n"
                 "Один из немногих языков программирования на польском языке",

    "🇹🇼 ТАЙВАНЬ": "🖥️ TSMC — полупроводниковый гигант мира\n\n"
                  "Основана: 1987\n"
                  "Локация: Хсиньчу, Тайвань\n\n"
                  "📌 Особенности:\n"
                  "• Чипы для Apple, AMD, Nvidia\n"
                  "• Лидер по техпроцессам 3нм и ниже\n"
                  "• Fabless+foundry модель\n\n"
                  "💡 Производит 90% продвинутых чипов в мире\n\n"
                  "🖥️ ASUS — ИТ-империя с тайваньскими корнями\n"
                  "Основана: 1989\n\n"
                  "📌 Инновации:\n"
                  "• Первая плата под Intel 486\n"
                  "• Линейка Eee PC и ROG\n\n"
                  "💡 Каждая 3-я материнка в мире — от ASUS\n\n"
                  "🖥️ Acer — демократизация ПК по-тайваньски\n"
                  "Основана: 1976 (Multitech → Acer в 1987)\n\n"
                  "📌 Достижения:\n"
                  "• №2 по ноутбукам в 2009\n"
                  "• ОС Gadmei OS, облачные решения\n\n"
                  "💡 Массовая компьютеризация стран Азии",

    "🇫🇮 ФИНЛЯНДИЯ": "🖥️ ECC — финская технология коррекции ошибок\n\n"
                    "Разработка: Университет Хельсинки, 1970–80-е\n\n"
                    "📌 Возможности:\n"
                    "• Повышение надёжности связи\n"
                    "• Применение в GSM и других протоколах\n\n"
                    "💡 Базовые алгоритмы ECC использовались в международных стандартах\n\n"
                    "🖥️ SAAB-101 — финская микроЭВМ\n\n"
                    "Разработка: 1975, финские НИИ\n\n"
                    "📌 Характеристики:\n"
                    "• 16-разрядный CPU\n"
                    "• 32 КБ RAM\n"
                    "• Применение — автоматизация и измерения\n\n"
                    "💡 Влияние на развитие микроэлектроники Финляндии"
}
  # сюда вставь полностью словарь technology_info
university_info = {
    "🇭🇺 ВЕНГРИЯ": "🎓 MTA SZTAKI — венгерская кузница алгоритмов и компьютеров\n"
                  "Полное название: Институт компьютерных наук и автоматизации Венгерской академии наук\n"
                  "Основан: 1964, Будапешт\n\n"
                  "📌 Направления:\n"
                  "• Искусственный интеллект и робототехника\n"
                  "• Промышленный интернет вещей\n"
                  "• Компьютерное зрение и симуляции\n\n"
                  "💡 Интересный факт:\n"
                  "В 1970-х у института была собственная исследовательская сеть, связанная с западными проектами ЮНЕСКО.",

    "🇮🇳 ИНДИЯ": "🎓 IIT Bombay — Indian Institute of Technology\n"
                "Основан: 1958, Мумбаи (при поддержке СССР)\n\n"
                "📌 Особенности:\n"
                "• Один из первых кампусов с ЭВМ в Индии\n"
                "• Участие в проектах ISRO, ECIL, BARC\n"
                "• Сильные курсы по прикладному программированию\n\n"
                "💡 В 1970-х студенты собирали собственные микрокомпьютеры.\n\n"
                "🎓 IISc — Indian Institute of Science\n"
                "Основан: 1909, Бангалор (инициатива Тата)\n\n"
                "📌 Особенности:\n"
                "• Криптография, алгоритмы, суперкомпьютеры\n"
                "• Платформа PARAM, фундаментальная информатика\n"
                "• Сотрудничество с BARC и C-DAC",

    "🇵🇱 ПОЛЬША": "🎓 Варшавский политех\n"
                 "Основан: 1915, Варшава\n\n"
                 "📌 Направления:\n"
                 "• ИИ, робототехника, биоинформатика\n"
                 "• Один из крупнейших ИТ-факультетов в Восточной Европе\n"
                 "• Партнёр Microsoft Research и Samsung\n\n"
                 "🎓 AGH (Краков)\n"
                 "Основан: 1919, ИТ с 1960-х\n\n"
                 "📌 Особенности:\n"
                 "• Суперкомпьютер Prometheus\n"
                 "• Участие в проектах CERN, ESA\n"
                 "• Центр Data Science\n\n"
                 "🎓 Вроцлавский политех\n"
                 "Основан: 1945 (1951 статус), ИТ — с 60-х\n\n"
                 "📌 Специализация:\n"
                 "• Кибербезопасность, ИИ, суперкомпьютеры\n"
                 "• Разработка серии Odra",

    "🇹🇼 ТАЙВАНЬ": "🎓 National Taiwan University (NTU)\n"
                  "Город: Тайбэй, Основан: 1928 (как Taihoku Imperial University)\n\n"
                  "📌 Сильные стороны:\n"
                  "• Информатика, электроника, биотехнологии\n"
                  "• Выпускники: TSMC, ASUS, Acer, MediaTek\n"
                  "• Фундамент исследований в полупроводниках",

    "🇫🇮 ФИНЛЯНДИЯ": "🎓 University of Helsinki\n"
                    "Основан: 1640, Хельсинки\n\n"
                    "📌 Направления:\n"
                    "• Информатика, криптография, биоинформатика\n"
                    "• Центр квантовых технологий\n\n"
                    "💡 Интересный факт:\n"
                    "Здесь учился Линус Торвальдс — создатель Linux"
}
  # сюда вставь полностью словарь university_info
company_info = {
    "🇭🇺 ВЕНГРИЯ": "🏭 Graphisoft — цифровой архитектор\n"
                  "Основана: 1982, Будапешт\n"
                  "Продукт: Archicad (первая BIM-система)\n\n"
                  "📌 Особенности:\n"
                  "• Первая CAD-система на Mac в Европе\n"
                  "• Archicad использовался по всему миру\n"
                  "• С 2007 — часть Nemetschek Group\n\n"
                  "💡 Интересный факт:\n"
                  "Archicad писался в подвале с перебоями электричества",

    "🇮🇳 ИНДИЯ": "🏢 Tata Consultancy Services (TCS)\n"
                "Основана: 1968\n"
                "📌 Достижения:\n"
                "• Первые в Индии начали использовать мейнфреймы\n"
                "• Автоматизация банков и телекомов\n"
                "• С 1980-х — на международном рынке\n\n"
                "💡 Программирование — на перфокартах в 70-х\n\n"
                "🏢 Bharat Electronics Limited (BEL)\n"
                "Основана: 1954, Банглор\n"
                "📌 Особенности:\n"
                "• Оборонные вычислительные системы\n"
                "• Контроллеры для ИСРО и DRDO",

    "🇵🇱 ПОЛЬША": "🏢 Asseco — крупнейший ИТ-холдинг Восточной Европы\n"
                 "Основана: 1991, Жешув\n\n"
                 "📌 Сферы:\n"
                 "• Финтех, здравоохранение, госсектор\n"
                 "• Более 32 000 сотрудников\n\n"
                 "💡 Входит в индекс WIG30\n\n"
                 "🏢 CD Projekt RED — геймдев-звезда\n"
                 "Основана: 1994 (официально 2002), Варшава\n\n"
                 "📌 Главные продукты:\n"
                 "• Ведьмак 3, Cyberpunk 2077, GOG.com\n"
                 "💡 В 2020 стала самой ценной игровой компанией Европы",

    "🇹🇼 ТАЙВАНЬ": "🏢 ASUS — от материнок до ROG\n"
                  "Основана: 1989, Тайбэй\n\n"
                  "📌 Особенности:\n"
                  "• Первая плата под Intel 486\n"
                  "• ROG, Eee PC, Zenbook\n"
                  "💡 Каждая третья мать в мире — ASUS\n\n"
                  "🏢 Acer — доступность ПК\n"
                  "Основана: 1976 (Multitech → Acer в 1987)\n"
                  "📌 Особенности:\n"
                  "• №2 по ноутам в 2009\n"
                  "• ОС, облака, массовая цифровизация",

    "🇫🇮 ФИНЛЯНДИЯ": "🏢 Nokia — от сапог к смартфонам\n"
                    "Основана: 1865, Эспоо\n"
                    "📌 Вехи:\n"
                    "• Лидер по телефонам в 2000-х\n"
                    "• 3310, N-Gage, Communicator\n"
                    "• Продажа Microsoft — 2013\n\n"
                    "💡 Современная Nokia — 5G и патенты"
}
     # сюда вставь полностью словарь company_info
test_questions = {
    "🇭🇺 ВЕНГРИЯ": [
        {
            "question": "Какой венгерский компьютер был создан в 1984 году?",
            "options": ["Primo", "MikroMiko", "ZX Spectrum"],
            "answer": "Primo"
        },
        {
            "question": "Какой процессор использовался в Primo?",
            "options": ["U880", "Intel 8080", "Motorola 68000"],
            "answer": "U880"
        }
    ],
    "🇮🇳 ИНДИЯ": [
        {
            "question": "В каком году был основан Индийский технологический институт в Бомбее (IIT Bombay)?",
            "options": ["1947", "1958", "1965"],
            "answer": "1958"
        },
        {
            "question": "Какие две стороны совместно поддерживали создание и развитие IIT Bombay в начальный период?",
            "options": ["США и Япония", "СССР и правительство Индии", "Великобритания и Франция"],
            "answer": "СССР и правительство Индии"
        },
        {
            "question": "Какой известный индийский научный институт был основан промышленником Джамшеджи Тата?",
            "options": ["IIT Delhi", "Индийский институт науки (IISc)", "BITS Pilani"],
            "answer": "Индийский институт науки (IISc)"
        },
        {
            "question": "В каком крупном индийском городе расположен главный кампус IISc?",
            "options": ["Дели", "Ченнаи", "Бангалор"],
            "answer": "Бангалор"
        },
        {
            "question": "Какое название получил первый индийский суперкомпьютер?",
            "options": ["TDC", "PARAM", "Cray"],
            "answer": "PARAM"
        },
        {
            "question": "В каком году был создан суперкомпьютер PARAM 8000?",
            "options": ["1985", "1991", "1995"],
            "answer": "1991"
        }
    ],
    "🇵🇱 ПОЛЬША": [
        {
            "question": "Какой польский вуз начал подготовку IT-специалистов ещё в социалистический период?",
            "options": ["Варшавский политех", "Ягеллонский университет", "Университет Коперника"],
            "answer": "Варшавский политех"
        },
        {
            "question": "Какая компания начинала с торговли играми на базаре?",
            "options": ["Techland", "CD Projekt RED", "11 bit studios"],
            "answer": "CD Projekt RED"
        }
    ],
    "🇹🇼 ТАЙВАНЬ": [
        {
            "question": "Крупнейший IT вуз Тайваня:",
            "options": ["National Chengchi University", "National Taiwan University (NTU)", "National Tsing Hua University"],
            "answer": "National Taiwan University (NTU)"
        },
        {
            "question": "Какая компания производит чипы для Apple, AMD и Nvidia?",
            "options": ["MediaTek", "UMC", "TSMC"],
            "answer": "TSMC"
        },
        {
            "question": "Какой тайваньский бренд начинал с производства материнских плат и сейчас делает каждую третью в мире?",
            "options": ["Gigabyte", "ASUS", "MSI"],
            "answer": "ASUS"
        },
        {
            "question": "Какая компания первой внедрила модель «fabless + foundry»?",
            "options": ["Intel", "Samsung Foundry", "TSMC"],
            "answer": "TSMC"
        },
        {
            "question": "Какой тайваньский бренд в 2009 году временно стал вторым в мире по продажам ноутбуков?",
            "options": ["Acer", "ASUS", "HTC"],
            "answer": "Acer"
        }
    ],
    "🇫🇮 ФИНЛЯНДИЯ": [
        {
            "question": "Какой финский университет связан с созданием Linux?",
            "options": ["Университет Турку", "Университет Хельсинки", "Технологический университет Тампере"],
            "answer": "Университет Хельсинки"
        },
        {
            "question": "Что разрабатывала Nokia до выхода на телеком-рынок?",
            "options": ["Военную технику", "Резиновые сапоги и бумагу", "Автомобильные двигатели"],
            "answer": "Резиновые сапоги и бумагу"
        },
        {
            "question": "Какая игра принесла Rovio мировой успех после 51 провала?",
            "options": ["Clash of Clans", "Angry Birds", "Candy Crush Saga"],
            "answer": "Angry Birds"
        },
        {
            "question": "Какая технология, разработанная в Финляндии, улучшила цифровую связь?",
            "options": ["Bluetooth", "ECC (Error Correction Codes)", "GSM"],
            "answer": "ECC (Error Correction Codes)"
        }
    ]
}
 # сюда вставлен полностью словарь test_questions

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Выбери страну:", reply_markup=countries_keyboard)

# Обработка всех сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "🔙 Назад":
        user_states.pop(user_id, None)
        await update.message.reply_text("Выберите страну:", reply_markup=countries_keyboard)
        return

    countries = list(technology_info.keys())

    if text in countries:
        user_states[user_id] = {"country": text, "test_step": 0, "test_score": 0}
        await update.message.reply_text(f"Вы выбрали {text}. Теперь выбери действие:", reply_markup=main_menu_keyboard)
        return

    if user_id not in user_states:
        await update.message.reply_text("Сначала выбери страну:", reply_markup=countries_keyboard)
        return

    country = user_states[user_id]["country"]

    if text == "⚙️ Технологии":
        await update.message.reply_text(technology_info.get(country, "Нет данных."), reply_markup=main_menu_keyboard)
    elif text == "🏫 Вузы":
        await update.message.reply_text(university_info.get(country, "Нет данных."), reply_markup=main_menu_keyboard)
    elif text == "🏢 Компании":
        await update.message.reply_text(company_info.get(country, "Нет данных."), reply_markup=main_menu_keyboard)
    elif text == "📋 Тест":
        questions = test_questions.get(country)
        if not questions:
            await update.message.reply_text("Пока нет вопросов для этой страны.", reply_markup=main_menu_keyboard)
            return
        question_data = questions[0]
        options_text = "\n".join([f"{chr(97+i)}) {opt}" for i, opt in enumerate(question_data["options"])])
        await update.message.reply_text(f"1. {question_data['question']}\n{options_text}", reply_markup=main_menu_keyboard)
        user_states[user_id]["mode"] = "quiz"
    elif text == "☠️ Русская рулетка":
        questions = test_questions.get(country)
        if not questions:
            await update.message.reply_text("Нет вопросов для этой страны.", reply_markup=main_menu_keyboard)
            return
        roulette_q = random.choice(questions)
        user_states[user_id]["mode"] = "roulette"
        user_states[user_id]["roulette_q"] = roulette_q
        options_text = "\n".join([f"{chr(97+i)}) {opt}" for i, opt in enumerate(roulette_q["options"])])
        await update.message.reply_text(f"🎲 Русская рулетка!\nОтвечай, чтобы выжить:\n\n{roulette_q['question']}\n{options_text}",
                                        reply_markup=main_menu_keyboard)
    elif user_states[user_id].get("mode") == "quiz":
        questions = test_questions[country]
        step = user_states[user_id]["test_step"]
        correct_answer = questions[step]["answer"].lower()
        user_input = text.strip().lower()

        options = questions[step]["options"]
        letters = [chr(97+i) for i in range(len(options))]
        letter_to_option = dict(zip(letters, options))

        if user_input in letters:
            selected = letter_to_option[user_input].lower()
        elif user_input in [opt.lower() for opt in options]:
            selected = user_input
        else:
            await update.message.reply_text("Выберите вариант ответа (например, a, b или c).")
            return

        if selected == correct_answer:
            user_states[user_id]["test_score"] += 1
        user_states[user_id]["test_step"] += 1
        step += 1
        if step < len(questions):
            q = questions[step]
            options_text = "\n".join([f"{chr(97+i)}) {opt}" for i, opt in enumerate(q["options"])])
            await update.message.reply_text(f"{step+1}. {q['question']}\n{options_text}", reply_markup=main_menu_keyboard)
        else:
            score = user_states[user_id]["test_score"]
            await update.message.reply_text(f"Тест завершён! Правильных ответов: {score}/{len(questions)}", reply_markup=main_menu_keyboard)
            user_states[user_id].pop("mode", None)
            user_states[user_id]["test_step"] = 0
            user_states[user_id]["test_score"] = 0
    elif user_states[user_id].get("mode") == "roulette":
        q = user_states[user_id]["roulette_q"]
        correct_answer = q["answer"].lower()
        options = q["options"]
        letters = [chr(97+i) for i in range(len(options))]
        letter_to_option = dict(zip(letters, options))

        user_input = text.strip().lower()
        if user_input in letters:
            selected = letter_to_option[user_input].lower()
        elif user_input in [opt.lower() for opt in options]:
            selected = user_input
        else:
            await update.message.reply_text("Выберите вариант ответа (например, a, b или c).")
            return

        if selected == correct_answer:
            await update.message.reply_text("😌 Уфф... Выживший!", reply_markup=main_menu_keyboard)
        else:
            await update.message.reply_text("💥 БАМ! Вы выбыли!", reply_markup=main_menu_keyboard)

        user_states[user_id].pop("mode", None)
        user_states[user_id].pop("roulette_q", None)
    else:
        await update.message.reply_text("Пожалуйста, выбери действие из меню.", reply_markup=main_menu_keyboard)

if __name__ == "__main__":
    app = ApplicationBuilder().token("7742146854:AAEg9VGTTpHCC5d46sn_fEPHuyIDfnyMbNw").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()