import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import logic
from config import token

# Инициализация бота
bot = telebot.TeleBot(token)  # Замените на ваш токен

# Загрузка данных из JSON
data = logic.open_json("tbl.json")

# Функция для создания клавиатуры
def create_keyboard(buttons):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for button in buttons:
        keyboard.add(KeyboardButton(button))
    return keyboard

# Функция для красивого отображения проекта
def format_project(project_name, project_data):
    statuses = data["Status_id"]
    skills = data["skill_id"]
    
    # Получаем название статуса по ID
    status_name = [k for k, v in statuses.items() if v == project_data["status_id"]][0]
    
    # Получаем названия навыков по ID
    skill_names = []
    for skill_id in project_data["skill_id"]:
        skill_name = [k for k, v in skills.items() if v == skill_id][0]
        skill_names.append(skill_name)
    
    return (
        f"📌 <b>{project_name}</b>\n\n"
        f"📝 Описание: {project_data['desc']}\n"
        f"🌐 Ссылка: {project_data['irl']}\n"
        f"🛠 Навыки: {', '.join(skill_names)}\n"
        f"📊 Статус: {status_name}\n"
        f"👤 Автор: {project_data['user']}\n"
        f"🆔 ID: {project_data['id']}"
    )

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    buttons = ["📋 Список проектов", "➕ Добавить проект", "❌ Удалить проект", "🔄 Обновить статус", "🧹 Очистить список"]
    keyboard = create_keyboard(buttons)
    bot.send_message(message.chat.id, "👋 Привет! Я бот для управления проектами. Выбери действие:", reply_markup=keyboard)

# Обработчик кнопки "📋 Список проектов"
@bot.message_handler(func=lambda message: message.text == "📋 Список проектов")
def show_projects(message):
    projects = data["Projects"]["Project_list"]
    if not projects:
        bot.send_message(message.chat.id, "📭 Список проектов пуст.")
    else:
        for project_name, project_data in projects.items():
            formatted_project = format_project(project_name, project_data)
            bot.send_message(message.chat.id, formatted_project, parse_mode="HTML")

# Обработчик кнопки "➕ Добавить проект"
@bot.message_handler(func=lambda message: message.text == "➕ Добавить проект")
def add_project_step1(message):
    msg = bot.send_message(message.chat.id, "Введите название проекта:")
    bot.register_next_step_handler(msg, add_project_step2)

def add_project_step2(message):
    project_name = message.text
    msg = bot.send_message(message.chat.id, "Введите описание проекта:")
    bot.register_next_step_handler(msg, add_project_step3, project_name)

def add_project_step3(message, project_name):
    desc = message.text
    msg = bot.send_message(message.chat.id, "Введите ссылку на проект:")
    bot.register_next_step_handler(msg, add_project_step4, project_name, desc)

def add_project_step4(message, project_name, desc):
    irl = message.text
    
    # Создаем клавиатуру для выбора навыков
    skills = list(data["skill_id"].keys())
    keyboard = create_keyboard(skills + ["✅ Готово"])
    msg = bot.send_message(message.chat.id, "Выберите навыки (можно несколько):", reply_markup=keyboard)
    bot.register_next_step_handler(msg, add_project_step5, project_name, desc, irl, [])

def add_project_step5(message, project_name, desc, irl, selected_skills):
    if message.text != "✅ Готово":
        skill = message.text
        if skill in data["skill_id"]:
            selected_skills.append(data["skill_id"][skill])
        msg = bot.send_message(message.chat.id, "Выберите еще навыки или нажмите '✅ Готово':", reply_markup=create_keyboard(list(data["skill_id"].keys()) + ["✅ Готово"]))
        bot.register_next_step_handler(msg, add_project_step5, project_name, desc, irl, selected_skills)
    else:
        # Создаем клавиатуру для выбора статуса
        statuses = list(data["Status_id"].keys())
        keyboard = create_keyboard(statuses)
        msg = bot.send_message(message.chat.id, "Выберите статус проекта:", reply_markup=keyboard)
        bot.register_next_step_handler(msg, add_project_step6, project_name, desc, irl, selected_skills)

def add_project_step6(message, project_name, desc, irl, selected_skills):
    status = message.text
    if status in data["Status_id"]:
        status_id = data["Status_id"][status]
        logic.new_project(data, project_name, desc, irl, selected_skills, status_id)
        logic.update_json("tbl.json", data)
        bot.send_message(message.chat.id, f"✅ Проект '{project_name}' успешно добавлен!", reply_markup=create_keyboard(["📋 Список проектов", "➕ Добавить проект", "❌ Удалить проект", "🔄 Обновить статус", "🧹 Очистить список"]))
    else:
        bot.send_message(message.chat.id, "❌ Неверный статус. Попробуйте еще раз.")

# Обработчик кнопки "❌ Удалить проект"
@bot.message_handler(func=lambda message: message.text == "❌ Удалить проект")
def delete_project_step1(message):
    projects = data["Projects"]["Project_list"]
    if not projects:
        bot.send_message(message.chat.id, "📭 Список проектов пуст. Нечего удалять.")
    else:
        keyboard = create_keyboard(list(projects.keys()) + ["❌ Отмена"])
        msg = bot.send_message(message.chat.id, "Выберите проект для удаления:", reply_markup=keyboard)
        bot.register_next_step_handler(msg, delete_project_step2)

def delete_project_step2(message):
    if message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "Удаление отменено.", reply_markup=create_keyboard(["📋 Список проектов", "➕ Добавить проект", "❌ Удалить проект", "🔄 Обновить статус", "🧹 Очистить список"]))
    else:
        project_name = message.text
        try:
            logic.delete_project(data, project_name)
            logic.update_json("tbl.json", data)
            bot.send_message(message.chat.id, f"✅ Проект '{project_name}' успешно удален!", reply_markup=create_keyboard(["📋 Список проектов", "➕ Добавить проект", "❌ Удалить проект", "🔄 Обновить статус", "🧹 Очистить список"]))
        except KeyError:
            bot.send_message(message.chat.id, "❌ Проект не найден. Попробуйте еще раз.")

# Обработчик кнопки "🔄 Обновить статус"
@bot.message_handler(func=lambda message: message.text == "🔄 Обновить статус")
def update_status_step1(message):
    projects = data["Projects"]["Project_list"]
    if not projects:
        bot.send_message(message.chat.id, "📭 Список проектов пуст. Нечего обновлять.")
    else:
        keyboard = create_keyboard(list(projects.keys()) + ["❌ Отмена"])
        msg = bot.send_message(message.chat.id, "Выберите проект для обновления статуса:", reply_markup=keyboard)
        bot.register_next_step_handler(msg, update_status_step2)

def update_status_step2(message):
    if message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "Обновление статуса отменено.", reply_markup=create_keyboard(["📋 Список проектов", "➕ Добавить проект", "❌ Удалить проект", "🔄 Обновить статус", "🧹 Очистить список"]))
    else:
        project_name = message.text
        if project_name in data["Projects"]["Project_list"]:
            statuses = list(data["Status_id"].keys())
            keyboard = create_keyboard(statuses + ["❌ Отмена"])
            msg = bot.send_message(message.chat.id, "Выберите новый статус:", reply_markup=keyboard)
            bot.register_next_step_handler(msg, update_status_step3, project_name)
        else:
            bot.send_message(message.chat.id, "❌ Проект не найден. Попробуйте еще раз.")

def update_status_step3(message, project_name):
    if message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "Обновление статуса отменено.", reply_markup=create_keyboard(["📋 Список проектов", "➕ Добавить проект", "❌ Удалить проект", "🔄 Обновить статус", "🧹 Очистить список"]))
    else:
        status = message.text
        if status in data["Status_id"]:
            data["Projects"]["Project_list"][project_name]["status_id"] = data["Status_id"][status]
            logic.update_json("tbl.json", data)
            bot.send_message(message.chat.id, f"✅ Статус проекта '{project_name}' успешно обновлен на '{status}'!", reply_markup=create_keyboard(["📋 Список проектов", "➕ Добавить проект", "❌ Удалить проект", "🔄 Обновить статус", "🧹 Очистить список"]))
        else:
            bot.send_message(message.chat.id, "❌ Неверный статус. Попробуйте еще раз.")

# Обработчик кнопки "🧹 Очистить список"
@bot.message_handler(func=lambda message: message.text == "🧹 Очистить список")
def clear_projects(message):
    logic.clear_projects(data)
    logic.update_json("tbl.json", data)
    bot.send_message(message.chat.id, "✅ Список проектов успешно очищен!")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()