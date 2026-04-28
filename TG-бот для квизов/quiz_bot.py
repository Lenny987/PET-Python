import json
import logging
import nest_asyncio
import sqlite3
import uuid
import os
from telegram import BotCommand
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    JobQueue
)

nest_asyncio.apply()


TOKEN = "убрал из соображений безопасности"
POLLS_FILE = "/data/polls.json"
DATABASE_FILE = "/data/bot_database.db"
MEDIA_FOLDER = "/data/media"
ADMIN_ID = 724558868  #Telegram ID

os.makedirs(MEDIA_FOLDER, exist_ok=True)

TITLE, QUESTION, QUESTION_IMAGE, OPTIONS, NEXT_QUESTION, RESULTS, RESULT_IMAGE, CONFIRM = range(8)
EDIT_CHOICE, EDIT_TITLE, EDIT_QUESTIONS, EDIT_QUESTION, EDIT_OPTIONS, EDIT_RESULTS = range(8, 14)
AWAITING_MESSAGE, AWAITING_TIME = range(14, 16)
SHARE_POLL, SHARE_WITH_IMAGE = range(16, 18)

polls_data = {"polls": {}}
user_sessions = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def save_file(file_id: str, context: ContextTypes.DEFAULT_TYPE, file_type: str = "photo") -> str:
    """Сохраняет файл из Telegram на диск и возвращает имя файла"""
    try:
        file = await context.bot.get_file(file_id)
        ext = "jpg" if file_type == "photo" else "mp4" if file_type == "video" else "bin"
        filename = f"{file_id}.{ext}"
        filepath = os.path.join(MEDIA_FOLDER, filename)
        
        await file.download_to_drive(filepath)
        return filename
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None

async def check_media_files(context: ContextTypes.DEFAULT_TYPE):
    """Проверяет доступность медиафайлов и обновляет file_id при необходимости"""
    for poll_id, poll in polls_data["polls"].items():
        
        for question in poll.get("questions", []):
            if "image" in question and isinstance(question["image"], dict):
                filepath = os.path.join(MEDIA_FOLDER, question["image"]["local_path"])
                if not os.path.exists(filepath):
                    try:
                        
                        file = await context.bot.get_file(question["image"]["file_id"])
                        question["image"]["local_path"] = await save_file(file.file_id, context)
                    except Exception as e:
                        logger.error(f"Failed to restore image: {e}")
                        question.pop("image", None)
        
        
        if "result_images" in poll:
            for result_name, image_data in list(poll["result_images"].items()):
                if isinstance(image_data, dict):
                    filepath = os.path.join(MEDIA_FOLDER, image_data["local_path"])
                    if not os.path.exists(filepath):
                        try:
                            file = await context.bot.get_file(image_data["file_id"])
                            image_data["local_path"] = await save_file(file.file_id, context)
                        except Exception as e:
                            logger.error(f"Failed to restore result image: {e}")
                            poll["result_images"].pop(result_name, None)

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        registration_date TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scheduled_posts (
        post_id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_type TEXT,
        content_text TEXT,
        content_file_id TEXT,
        scheduled_time TEXT,
        status TEXT DEFAULT 'pending'
    )
    ''')
    
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, registration_date)
    VALUES (?, ?, ?, ?, datetime('now'))
    ''', (user_id, username, first_name, last_name))
    
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return users

def add_scheduled_post(content_type, content_text, content_file_id, scheduled_time):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO scheduled_posts (content_type, content_text, content_file_id, scheduled_time)
    VALUES (?, ?, ?, ?)
    ''', (content_type, content_text, content_file_id, scheduled_time))
    
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return post_id

def get_pending_posts():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT post_id, content_type, content_text, content_file_id, scheduled_time 
    FROM scheduled_posts 
    WHERE status = 'pending'
    ''')
    
    posts = [{
        'post_id': row[0],
        'content_type': row[1],
        'content_text': row[2],
        'content_file_id': row[3],
        'scheduled_time': row[4]
    } for row in cursor.fetchall()]
    
    conn.close()
    return posts

def mark_post_as_sent(post_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE scheduled_posts 
    SET status = 'sent' 
    WHERE post_id = ?
    ''', (post_id,))
    
    conn.commit()
    conn.close()

def load_polls():
    global polls_data
    try:
        with open(POLLS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "polls" in data and isinstance(data["polls"], dict):
                polls_data = data
            else:
                polls_data = {"polls": {}}
    except (FileNotFoundError, json.JSONDecodeError):
        polls_data = {"polls": {}}

async def save_polls(context: ContextTypes.DEFAULT_TYPE):
    try:

        await check_media_files(context)

        with open(POLLS_FILE, "w", encoding="utf-8") as f:
            json.dump(polls_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving polls: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        add_user(user.id, user.username, user.first_name, user.last_name)
        
        args = context.args if hasattr(context, "args") else []
        if args and args[0].startswith("startpoll_"):
            poll_id = args[0][10:]
            if poll_id not in polls_data["polls"]:
                await update.message.reply_text("⚠️ Опрос не найден!")
                return
            user_sessions[user.id] = {
                "poll_session": {
                    "poll_id": poll_id,
                    "score": 0,
                    "current_q": 0,
                    "answers": []
                },
                "last_message_id": None
            }
            await send_poll_question(update, context)
            return

        keyboard = [
            [InlineKeyboardButton("📊 Пройти опрос", callback_data="list_polls")],
            [InlineKeyboardButton("➕ Создать опрос", callback_data="create_poll")],
            [InlineKeyboardButton("🗂️ Мои опросы", callback_data="my_polls")]
        ]

        if update.message:
            await update.message.reply_text(
                "🌟 <b>Добро пожаловать в бота для анонимных опросов!</b> 🌟\n\n"
                "Здесь вы можете:\n"
                "• 🎯 Проходить интересные тесты\n"
                "• 🛠️ Создавать свои опросы\n"
                "• 📤 Делиться опросами и результатами с друзьями",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )
    
        else:
            await update.callback_query.edit_message_text(
                "🌟 <b>Добро пожаловать в бота для анонимных опросов!</b> 🌟\n\n"
                "Здесь вы можете:\n"
                "• 🎯 Проходить интересные тесты\n"
                "• 🛠️ Создавать свои опросы\n"
                "• 📤 Делиться опросами и результатами с друзьями",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )
            await update.callback_query.answer()
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await handle_error(update, context)

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.callback_query:
            await update.callback_query.answer("Произошла ошибка, попробуйте снова", show_alert=True)
        else:
            await update.message.reply_text("Произошла ошибка, попробуйте снова")
    except:
        pass

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Главная страница", callback_data="home")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Главное меню", reply_markup=reply_markup)

async def set_commands(application: Application):
    commands = [
        BotCommand(command="/menu", description="Открыть главное меню")
    ]
    await application.bot.set_my_commands(commands)

async def create_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        user_sessions[user_id] = {
            "current_poll": {"questions": [], "creator": user_id},
            "last_message_id": None,
            "state": TITLE
        }

        await update.callback_query.answer()
        msg = await update.callback_query.edit_message_text(
            "📝 <b>Введите название нового опроса, добавьте эмодзи для яркости:</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_poll")]
            ]),
            parse_mode="HTML"
        )
        user_sessions[user_id]["last_message_id"] = msg.message_id
        return TITLE
    except Exception as e:
        logger.error(f"Error in create_poll: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            await update.message.reply_text("🚫 Сессия устарела, начните заново /start")
            return ConversationHandler.END

        title = update.message.text.strip()
        if len(title) > 40:
            await update.message.reply_text("⚠️ Слишком длинное название! Максимум 40 символов.")
            return TITLE

        user_sessions[user_id]["current_poll"]["title"] = title
        user_sessions[user_id]["question_number"] = 1

        msg = await update.message.reply_text(
            f"📌 <b>Название опроса:</b> {title}\n\n"
            "📝 Теперь введите текст <b>1-го вопроса</b>:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_poll")]
            ]),
            parse_mode="HTML"
        )
        user_sessions[user_id]["last_message_id"] = msg.message_id
        return QUESTION
    except Exception as e:
        logger.error(f"Error in process_title: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            await update.message.reply_text("🚫 Сессия устарела, начните заново /start")
            return ConversationHandler.END

        q_text = update.message.text.strip()
        if len(q_text) > 1000:
            await update.message.reply_text("⚠️ Слишком длинный вопрос! Максимум 100 символов.")
            return QUESTION

        q_num = user_sessions[user_id]["question_number"]
        user_sessions[user_id]["current_question"] = {"text": q_text, "options": []}

        msg = await update.message.reply_text(
            f"📝 <b>Вопрос {q_num}:</b> {q_text}\n\n"
            "🖼️ <i>Хотите добавить изображение к этому вопросу?</i>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏭ Пропустить", callback_data="skip_image")],
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_poll")]
            ]),
            parse_mode="HTML"
        )
        user_sessions[user_id]["last_message_id"] = msg.message_id
        return QUESTION_IMAGE
    except Exception as e:
        logger.error(f"Error in process_question: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_question_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            await update.callback_query.answer("🚫 Сессия устарела", show_alert=True)
            return ConversationHandler.END

        if update.callback_query and update.callback_query.data == "skip_image":
            await update.callback_query.answer()
        elif update.message and update.message.photo:
            photo = max(update.message.photo, key=lambda p: p.file_size)
            filename = await save_file(photo.file_id, context)
            if filename:
                user_sessions[user_id]["current_question"]["image"] = {
                    "file_id": photo.file_id,
                    "local_path": filename
                }

        q_num = user_sessions[user_id]["question_number"]

        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=user_sessions[user_id]["last_message_id"]
        )

        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"➕ <b>Введите варианты ответов для вопроса {q_num}:</b>\n\n"
                 "Формат: <code>Текст ответа|Баллы</code>\n"
                 "Пример:\n<code>Да|2\nНет|-1\nНе знаю|0</code>\n\n"
                 "🔢 Каждый ответ с новой строки (от 2 до 10 вариантов)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_poll")]
            ]),
            parse_mode="HTML"
        )
        user_sessions[user_id]["last_message_id"] = msg.message_id
        return OPTIONS
    except Exception as e:
        logger.error(f"Error in process_question_image: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            await update.message.reply_text("🚫 Сессия устарела, начните заново /start")
            return ConversationHandler.END

        options = []
        for line in update.message.text.split("\n"):
            if line.strip() and "|" in line:
                text, weight = line.split("|", 1)
                options.append({"text": text.strip(), "weight": int(weight.strip())})

        if len(options) < 2:
            raise ValueError("❕ Нужно минимум 2 варианта ответа")
        if len(options) > 10:
            raise ValueError("❕ Максимум 10 вариантов ответа")

        user_sessions[user_id]["current_question"]["options"] = options
        current_poll = user_sessions[user_id]["current_poll"]
        current_poll["questions"].append(user_sessions[user_id]["current_question"].copy())

        q_num = user_sessions[user_id]["question_number"]
        q_count = len(current_poll["questions"])

        keyboard = []
        if q_count < 30:
            keyboard.append([InlineKeyboardButton("➕ Добавить следующий вопрос", callback_data="next_question")])

        if q_count >= 4:
            keyboard.append([InlineKeyboardButton("✅ Перейти к результатам", callback_data="to_results")])
        else:
            keyboard.append([InlineKeyboardButton(f"🔢 Нужно ещё {4-q_count} вопросов (минимум 4)", callback_data="need_more_questions")])

        keyboard.append([InlineKeyboardButton("❌ Отменить создание", callback_data="cancel_poll")])

        question = user_sessions[user_id]["current_question"]
        message_text = (
            f"✅ <b>Вопрос {q_num} добавлен!</b>\n"
            f"📊 Всего вопросов: {q_count}\n\n"
            f"ℹ️ {'Можно добавить ещё вопросы' if q_count < 30 else 'Достигнут максимум вопросов (30)'}"
        )

        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=user_sessions[user_id]["last_message_id"]
        )

        if "image" in question:
            filepath = os.path.join(MEDIA_FOLDER, question["image"]["local_path"])
            if os.path.exists(filepath):
                msg = await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=question["image"]["file_id"],
                    caption=message_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="HTML"
                )
            else:
                msg = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="HTML"
                )
        else:
            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )

        user_sessions[user_id]["last_message_id"] = msg.message_id
        return NEXT_QUESTION

    except ValueError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}\nПопробуйте ещё раз:")
        return OPTIONS
    except Exception as e:
        logger.error(f"Error in process_options: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def need_more_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            await update.callback_query.answer("🚫 Сессия устарела", show_alert=True)
            return ConversationHandler.END

        current_poll = user_sessions[user_id]["current_poll"]
        q_count = len(current_poll["questions"])
        needed = 4 - q_count

        await update.callback_query.answer(
            f"❕ Нужно ещё {needed} вопросов для продолжения!",
            show_alert=True
        )
        return NEXT_QUESTION
    except Exception as e:
        logger.error(f"Error in need_more_questions: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            await update.callback_query.answer("🚫 Сессия устарела", show_alert=True)
            return ConversationHandler.END

        user_sessions[user_id]["question_number"] += 1
        q_num = user_sessions[user_id]["question_number"]

        await update.callback_query.answer()

        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=user_sessions[user_id]["last_message_id"]
        )

        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📝 Введите текст <b>{q_num}-го вопроса</b>:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_poll")]
            ]),
            parse_mode="HTML"
        )
        user_sessions[user_id]["last_message_id"] = msg.message_id
        return QUESTION
    except Exception as e:
        logger.error(f"Error in next_question: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def to_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            await update.callback_query.answer("🚫 Сессия устарела", show_alert=True)
            return ConversationHandler.END

        current_poll = user_sessions[user_id]["current_poll"]
        q_count = len(current_poll["questions"])

        min_score = sum(min(opt["weight"] for opt in q["options"]) for q in current_poll["questions"])
        max_score = sum(max(opt["weight"] for opt in q["options"]) for q in current_poll["questions"])

        max_results = min(4 * ((q_count // 5) + 1), 12)

        await update.callback_query.answer()

        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=user_sessions[user_id]["last_message_id"]
        )

        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"📊 <b>Создание результатов теста</b>\n\n"
                f"ℹ️ Можно добавить от 1 до {max_results} результатов.\n"
                f"Формат: <code>Название|Минимальный балл</code>\n\n"
                f"Пример:\n<code>Отлично|15\nХорошо|10\nУдовлетворительно|5</code>\n\n"
                f"ℹ️ Диапазон возможных баллов: от {min_score} до {max_score}"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_poll")]
            ]),
            parse_mode="HTML"
        )
        user_sessions[user_id]["last_message_id"] = msg.message_id
        user_sessions[user_id]["max_results"] = max_results
        user_sessions[user_id]["min_score"] = min_score
        user_sessions[user_id]["max_score"] = max_score
        return RESULTS
    except Exception as e:
        logger.error(f"Error in to_results: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            await update.message.reply_text("🚫 Сессия устарела, начните заново /start")
            return ConversationHandler.END

        thresholds = []
        for line in update.message.text.split("\n"):
            if line.strip() and "|" in line:
                name, score = line.split("|", 1)
                thresholds.append((name.strip(), int(score.strip())))

        max_results = user_sessions[user_id]["max_results"]
        min_score = user_sessions[user_id]["min_score"]
        max_score = user_sessions[user_id]["max_score"]

        if len(thresholds) < 1:
            raise ValueError(f"❕ Нужно 1 результат")
        if len(thresholds) > max_results:
            raise ValueError(f"❕ Максимум {max_results} результатов")

        thresholds.sort(key=lambda x: x[1], reverse=True)

        if thresholds[0][1] > max_score:
            raise ValueError(f"❕ Максимальный порог {thresholds[0][1]} превышает возможный максимум {max_score}")
        if thresholds[-1][1] < min_score:
            raise ValueError(f"❕ Минимальный порог {thresholds[-1][1]} ниже возможного минимума {min_score}")

        for i in range(1, len(thresholds)):
            if thresholds[i-1][1] <= thresholds[i][1]:
                raise ValueError("❕ Пороги должны идти в убывающем порядке")

        if thresholds[-1][1] > min_score:
            thresholds.append(("Минимальный результат", min_score))

        user_sessions[user_id]["current_poll"]["thresholds"] = thresholds
        user_sessions[user_id]["result_images"] = {}
        user_sessions[user_id]["current_result"] = 0
        user_sessions[user_id]["result_names"] = [name for name, score in thresholds]

        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=user_sessions[user_id]["last_message_id"]
        )

        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "🖼️ <b>Хотите добавить изображения для результатов?</b>\n\n"
                f"Сейчас: {user_sessions[user_id]['result_names'][0]}\n"
                "Отправьте фото или нажмите 'Пропустить'"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏭ Пропустить", callback_data="skip_result_image")],
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_poll")]
            ]),
            parse_mode="HTML"
        )
        user_sessions[user_id]["last_message_id"] = msg.message_id
        return RESULT_IMAGE
    except ValueError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}\nПопробуйте ещё раз:")
        return RESULTS
    except Exception as e:
        logger.error(f"Error in process_results: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_result_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            await update.callback_query.answer("🚫 Сессия устарела", show_alert=True)
            return ConversationHandler.END

        if update.callback_query and update.callback_query.data == "skip_result_image":
            await update.callback_query.answer()
        elif update.message and update.message.photo:
            photo = max(update.message.photo, key=lambda p: p.file_size)
            current_result = user_sessions[user_id]["current_result"]
            result_name = user_sessions[user_id]["result_names"][current_result]
            filename = await save_file(photo.file_id, context)
            if filename:
                user_sessions[user_id]["result_images"][result_name] = {
                    "file_id": photo.file_id,
                    "local_path": filename
                }

        user_sessions[user_id]["current_result"] += 1
        current_result = user_sessions[user_id]["current_result"]
        result_names = user_sessions[user_id]["result_names"]

        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=user_sessions[user_id]["last_message_id"]
        )

        if current_result < len(result_names):
            next_result = result_names[current_result]
            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f"🖼️ <b>Добавление изображения для результата:</b>\n\n"
                    f"Сейчас: {next_result}\n"
                    "Отправьте фото или нажмите 'Пропустить'"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏭ Пропустить", callback_data="skip_result_image")],
                    [InlineKeyboardButton("❌ Отмена", callback_data="cancel_poll")]
                ]),
                parse_mode="HTML"
            )
            user_sessions[user_id]["last_message_id"] = msg.message_id
            return RESULT_IMAGE
        else:
            current_poll = user_sessions[user_id]["current_poll"]
            result_images = user_sessions[user_id]["result_images"]
            current_poll["result_images"] = result_images

            summary = (
                f"📋 <b>Сводка по опросу:</b>\n\n"
                f"📌 <b>Название:</b> {current_poll['title']}\n"
                f"🔢 <b>Количество вопросов:</b> {len(current_poll['questions'])}\n"
                f"📊 <b>Диапазон баллов:</b> от {user_sessions[user_id]['min_score']} до {user_sessions[user_id]['max_score']}\n\n"
                f"🏆 <b>Результаты:</b>\n" +
                "\n".join(f"• {name}: от {score} баллов" for name, score in current_poll['thresholds'])
            )

            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=summary,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Сохранить опрос", callback_data="save_poll")],
                    [InlineKeyboardButton("🔄 Изменить заново", callback_data="cancel_poll")]
                ]),
                parse_mode="HTML"
            )
            user_sessions[user_id]["last_message_id"] = msg.message_id
            return CONFIRM
    except Exception as e:
        logger.error(f"Error in process_result_image: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def save_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            await update.callback_query.answer("🚫 Сессия устарела", show_alert=True)
            return ConversationHandler.END

        poll_id = f"poll_{uuid.uuid4().hex}"  # Генерируем уникальный ID
        polls_data["polls"][poll_id] = user_sessions[user_id]["current_poll"].copy()
        polls_data["polls"][poll_id]["views"] = 0
        await save_polls(context)

        await update.callback_query.answer("✅ Опрос сохранён!")

        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=user_sessions[user_id]["last_message_id"]
        )

        bot_username = (await context.bot.get_me()).username
        poll_link = f"https://t.me/{bot_username}?start=startpoll_{poll_id}"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "🎉 <b>Опрос успешно создан!</b>\n\n"
                f"📌 Название: {polls_data['polls'][poll_id]['title']}\n"
                f"🔢 Вопросов: {len(polls_data['polls'][poll_id]['questions'])}\n\n"
                "Теперь вы можете поделиться этим опросом с друзьями!"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Поделиться опросом", callback_data=f"share_poll_{poll_id}")],
                [InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]
            ]),
            parse_mode="HTML"
        )
        if user_id in user_sessions:
            del user_sessions[user_id]
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in save_poll: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def share_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        poll_id = query.data.split("_", 2)[-1]
        poll = polls_data["polls"].get(poll_id)
        
        if not poll or poll.get("creator") != user_id:
            await query.answer("Опрос не найден или у вас нет прав!", show_alert=True)
            return
        
        context.user_data["share_poll"] = {
            "poll_id": poll_id,
            "poll_title": poll["title"],
            "poll_link": f"https://t.me/{(await context.bot.get_me()).username}?start=startpoll_{poll_id}"
        }
        
        await query.answer()
        await query.edit_message_text(
            f"📤 <b>Поделиться опросом:</b> {poll['title']}\n\n"
            "🖼️ Хотите добавить изображение к сообщению?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Да, добавить изображение", callback_data="share_with_image")],
                [InlineKeyboardButton("⏭ Нет, без изображения", callback_data="share_without_image")],
                [InlineKeyboardButton("❌ Отмена", callback_data=f"my_poll_{poll_id}")]
            ]),
            parse_mode="HTML"
        )
        return SHARE_POLL
    except Exception as e:
        logger.error(f"Error in share_poll: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def share_with_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🖼️ Отправьте изображение для сообщения:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_share")]
            ])
        )
        
        context.user_data["share_poll"]["awaiting_image"] = True
        return SHARE_WITH_IMAGE
    except Exception as e:
        logger.error(f"Error in share_with_image: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_share_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.photo:
            await update.message.reply_text("Пожалуйста, отправьте изображение.")
            return
        
        photo = max(update.message.photo, key=lambda p: p.file_size)
        context.user_data["share_poll"]["image_file_id"] = photo.file_id
        context.user_data["share_poll"]["awaiting_image"] = False
        
        await send_share_message(update, context)
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in process_share_image: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def share_without_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        await send_share_message(update, context)
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in share_without_image: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def send_share_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        share_data = context.user_data.get("share_poll", {})
        poll_id = share_data.get("poll_id")
        poll_link = share_data.get("poll_link")
        poll_title = share_data.get("poll_title")
        image_file_id = share_data.get("image_file_id")
        
        if not poll_id:
            if hasattr(update, "message"):
                await update.message.reply_text("Ошибка: данные опроса не найдены.")
            else:
                await update.callback_query.edit_message_text("Ошибка: данные опроса не найдены.")
            return
        
        message_text = (
            f"📝 <b>{poll_title}</b>\n\n"
            "Я создал(а) интересный опрос в <b>Interesting Polls</b>! "
            "Скорее проходите и делитесь результатами! 😃\n\n"
            f"👉 <a href='{poll_link}'>Перейти к опросу</a>"
        )
        
        try:
            if image_file_id:
                await context.bot.send_photo(
                    chat_id=update.effective_user.id,
                    photo=image_file_id,
                    caption=message_text,
                    parse_mode="HTML"
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=message_text,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="✅ Сообщение готово! Теперь вы можете переслать его в нужный чат.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К опросу", callback_data=f"my_poll_{poll_id}")]
                ])
            )
            
        except Exception as e:
            logger.error(f"Failed to send share message: {e}")
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="⚠️ Не удалось создать сообщение для пересылки. Попробуйте позже."
            )
        
        if "share_poll" in context.user_data:
            del context.user_data["share_poll"]
    except Exception as e:
        logger.error(f"Error in send_share_message: {e}")
        await handle_error(update, context)

async def cancel_share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        poll_id = context.user_data.get("share_poll", {}).get("poll_id")
        
        if "share_poll" in context.user_data:
            del context.user_data["share_poll"]
        
        await query.answer("❌ Отменено")
        if poll_id:
            await query.edit_message_text(
                "❌ Поделиться опросом отменено.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К опросу", callback_data=f"my_poll_{poll_id}")]
                ])
            )
        else:
            await query.edit_message_text(
                "❌ Поделиться опросом отменено.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]
                ])
            )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in cancel_share: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def cancel_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id in user_sessions:
            del user_sessions[user_id]

        if update.callback_query:
            await update.callback_query.answer("❌ Создание отменено")
            await update.callback_query.edit_message_text(
                "🗑️ <b>Создание опроса отменено.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]
                ]),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                "🗑️ <b>Создание опроса отменено.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]
                ]),
                parse_mode="HTML"
            )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in cancel_poll: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def list_polls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not polls_data.get("polls") or not isinstance(polls_data["polls"], dict):
            await update.callback_query.answer("📭 Нет опросов!")
            await update.callback_query.edit_message_text(
                "📭 <b>Сейчас нет доступных опросов.</b>\n\n"
                "Вы можете создать свой собственный опрос!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Создать опрос", callback_data="create_poll")],
                    [InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]
                ]),
                parse_mode="HTML"
            )
            return

        valid_polls = []
        for pid, poll in polls_data["polls"].items():
            try:
                if isinstance(poll, dict) and "title" in poll and "questions" in poll and isinstance(poll["questions"], list):
                    valid_polls.append((pid, poll))
            except:
                continue

        if not valid_polls:
            await update.callback_query.answer("📭 Нет опросов!")
            await update.callback_query.edit_message_text(
                "📭 <b>Сейчас нет доступных опросов.</b>\n\n"
                "Вы можете создать свой собственный опрос!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Создать опрос", callback_data="create_poll")],
                    [InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]
                ]),
                parse_mode="HTML"
            )
            return

        valid_polls.sort(key=lambda x: x[1].get("views", 0), reverse=True)
        top_polls = valid_polls[:50]

        keyboard = [
            [InlineKeyboardButton(
                f"{poll['title']}",
                callback_data=f"start_poll_{pid}"
            )]
            for pid, poll in top_polls
        ]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "📚 <b>Топ-50 популярных опросов:</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in list_polls: {e}")
        await handle_error(update, context)

async def start_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        poll_id = update.callback_query.data.split("_", 2)[-1]

        if poll_id not in polls_data["polls"]:
            await update.callback_query.answer("⚠️ Опрос не найден!", show_alert=True)
            return

        user_sessions[user_id] = {
            "poll_session": {
                "poll_id": poll_id,
                "score": 0,
                "current_q": 0,
                "answers": []
            },
            "last_message_id": None
        }

        await send_poll_question(update, context)
    except Exception as e:
        logger.error(f"Error in start_poll: {e}")
        await handle_error(update, context)


async def send_poll_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions or "poll_session" not in user_sessions[user_id]:
            if hasattr(update, "callback_query") and update.callback_query:
                await update.callback_query.answer("🚫 Сессия устарела", show_alert=True)
            return

        poll_id = user_sessions[user_id]["poll_session"]["poll_id"]
        poll = polls_data["polls"][poll_id]
        q_idx = user_sessions[user_id]["poll_session"]["current_q"]
        question = poll["questions"][q_idx]

        options_text = "\n".join(
            f"{idx+1}. {opt['text']}" 
            for idx, opt in enumerate(question["options"]))
        
        keyboard = [
            [InlineKeyboardButton(str(idx+1), callback_data=f"answer_{q_idx}_{idx}")]
            for idx in range(len(question["options"]))
        ]
        keyboard.append([InlineKeyboardButton("❌ Отменить прохождение", callback_data="cancel_poll_session")])

        question_text = (
            f"📊 <b>Опрос:</b> {poll['title']}\n\n"
            f"🔢 <b>Вопрос {q_idx+1}/{len(poll['questions'])}:</b>\n\n"
            f"{question['text']}\n\n"
            f"<b>Варианты ответов:</b>\n{options_text}"
        )

        if hasattr(update, "callback_query") and update.callback_query:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.callback_query.message.message_id
                )
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения: {e}")

        if "image" in question:
            filepath = os.path.join(MEDIA_FOLDER, question["image"]["local_path"])
            if os.path.exists(filepath):
                try:
                    msg = await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=question["image"]["file_id"],
                        caption=question_text,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Ошибка при отправке фото: {e}")
                    msg = await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=question_text,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode="HTML"
                    )
            else:
                msg = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=question_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="HTML"
                )
        else:
            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=question_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )

        user_sessions[user_id]["last_message_id"] = msg.message_id

    except Exception as e:
        logger.error(f"Ошибка в send_poll_question: {e}")
        await handle_error(update, context)

            

async def process_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions or "poll_session" not in user_sessions[user_id]:
            await update.callback_query.answer("🚫 Сессия устарела", show_alert=True)
            return

        query = update.callback_query
        await query.answer()

        data = query.data.split("_")
        q_idx = int(data[1])
        opt_idx = int(data[2])

        poll_id = user_sessions[user_id]["poll_session"]["poll_id"]
        poll = polls_data["polls"][poll_id]
        question = poll["questions"][q_idx]
        selected_option = question["options"][opt_idx]

        user_sessions[user_id]["poll_session"]["answers"].append({
            "question": question["text"],
            "answer": selected_option["text"],
            "weight": selected_option["weight"]
        })

        user_sessions[user_id]["poll_session"]["score"] += selected_option["weight"]

        if q_idx + 1 < len(poll["questions"]):
            user_sessions[user_id]["poll_session"]["current_q"] += 1
            await send_poll_question(update, context)
        else:
            score = user_sessions[user_id]["poll_session"]["score"]
            result = None

            for name, threshold in sorted(poll["thresholds"], key=lambda x: x[1], reverse=True):
                if score >= threshold:
                    result = name
                    break

            poll["views"] = poll.get("views", 0) + 1
            await save_polls(context)

            bot_username = (await context.bot.get_me()).username
            poll_link = f"https://t.me/{bot_username}?start=startpoll_{poll_id}"

            result_text = (
                f"🏆 <b>Ваш результат:</b> {result}\n\n"
                f"Пройти опрос: {poll_link}"
            )

            keyboard = [
                [InlineKeyboardButton("🔄 Пройти опрос", url=poll_link)],
                [InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]
            ]

            if "result_images" in poll and result in poll["result_images"]:
                filepath = os.path.join(MEDIA_FOLDER, poll["result_images"][result]["local_path"])
                if os.path.exists(filepath):
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=poll["result_images"][result]["file_id"],
                        caption=result_text,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode="HTML"
                    )
                else:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=result_text,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode="HTML"
                    )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=result_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="HTML"
                )

            if user_id in user_sessions:
                del user_sessions[user_id]
    except Exception as e:
        logger.error(f"Error in process_answer: {e}")
        await handle_error(update, context)

async def cancel_poll_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if user_id in user_sessions and "poll_session" in user_sessions[user_id]:
            del user_sessions[user_id]["poll_session"]
        
        await update.callback_query.answer("❌ Прохождение отменено")
        await start(update, context)
    except Exception as e:
        logger.error(f"Error in cancel_poll_session: {e}")
        await handle_error(update, context)

async def my_polls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        my_polls = [
            (pid, poll) for pid, poll in polls_data["polls"].items()
            if poll.get("creator") == user_id
        ]
        if not my_polls:
            await update.callback_query.answer("У вас пока нет опросов!", show_alert=True)
            await update.callback_query.edit_message_text(
                "📭 <b>У вас нет созданных опросов.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Создать опрос", callback_data="create_poll")],
                    [InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]
                ]),
                parse_mode="HTML"
            )
            return

        keyboard = [
            [InlineKeyboardButton(
                f"📋 {poll['title']} ({len(poll['questions'])} вопросов, {poll.get('views',0)} прохожд.)",
                callback_data=f"my_poll_{pid}"
            )] for pid, poll in my_polls
        ]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
        await update.callback_query.edit_message_text(
            "🗂️ <b>Ваши опросы:</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in my_polls: {e}")
        await handle_error(update, context)

async def my_poll_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        poll_id = update.callback_query.data.split("_", 2)[-1]
        poll = polls_data["polls"].get(poll_id)
        if not poll or poll.get("creator") != user_id:
            await update.callback_query.answer("Опрос не найден!", show_alert=True)
            return

        bot_username = (await context.bot.get_me()).username
        poll_link = f"https://t.me/{bot_username}?start=startpoll_{poll_id}"

        keyboard = [
            [InlineKeyboardButton("🔗 Поделиться опросом", callback_data=f"share_poll_{poll_id}")],
            [InlineKeyboardButton("📝 Редактировать", callback_data=f"edit_poll_{poll_id}")],
            [InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_confirm_{poll_id}")],  # Изменили префикс здесь
            [InlineKeyboardButton("🔙 Назад", callback_data="my_polls")]
        ]
        await update.callback_query.edit_message_text(
            f"📋 <b>{poll['title']}</b>\n"
            f"🔢 Вопросов: {len(poll['questions'])}\n"
            f"📊 Прохождений: {poll.get('views', 0)}\n\n"
            f"🔗 Ссылка: <code>{poll_link}</code>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in my_poll_menu: {e}")
        await handle_error(update, context)

async def delete_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        poll_id = update.callback_query.data.split("_", 2)[-1]
        poll = polls_data["polls"].get(poll_id)
        if poll and poll.get("creator") == user_id:
            for question in poll.get("questions", []):
                if "image" in question and isinstance(question["image"], dict):
                    try:
                        os.remove(os.path.join(MEDIA_FOLDER, question["image"]["local_path"]))
                    except:
                        pass
            
            if "result_images" in poll:
                for result_name, image_data in poll["result_images"].items():
                    if isinstance(image_data, dict):
                        try:
                            os.remove(os.path.join(MEDIA_FOLDER, image_data["local_path"]))
                        except:
                            pass
            
            del polls_data["polls"][poll_id]
            await save_polls(context)
            await update.callback_query.answer("Опрос удалён!")
            await my_polls(update, context)
        else:
            await update.callback_query.answer("Нет доступа!", show_alert=True)
    except Exception as e:
        logger.error(f"Error in delete_poll: {e}")
        await handle_error(update, context)

async def confirm_delete_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        poll_id = update.callback_query.data.split("_", 2)[-1]
        poll = polls_data["polls"].get(poll_id)
        
        if not poll:
            await update.callback_query.answer("Опрос не найден!", show_alert=True)
            return
        
        await update.callback_query.edit_message_text(
            f"❌ Вы уверены, что хотите удалить опрос?\n\n"
            f"📌 Название: {poll['title']}\n"
            f"🔢 Вопросов: {len(poll['questions'])}\n"
            f"📊 Прохождений: {poll.get('views', 0)}\n\n"
            "Это действие нельзя отменить!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Да, удалить", callback_data=f"delete_poll_{poll_id}")],  # Используем delete_poll_ как префикс
                [InlineKeyboardButton("❌ Нет, отменить", callback_data=f"my_poll_{poll_id}")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in confirm_delete_poll: {e}")
        await handle_error(update, context)

async def delete_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        poll_id = update.callback_query.data.split("_", 2)[-1]
        poll = polls_data["polls"].get(poll_id)
        
        if poll and poll.get("creator") == user_id:
            for question in poll.get("questions", []):
                if "image" in question and isinstance(question["image"], dict):
                    try:
                        os.remove(os.path.join(MEDIA_FOLDER, question["image"]["local_path"]))
                    except:
                        pass
            
            if "result_images" in poll:
                for result_name, image_data in poll["result_images"].items():
                    if isinstance(image_data, dict):
                        try:
                            os.remove(os.path.join(MEDIA_FOLDER, image_data["local_path"]))
                        except:
                            pass
            
            del polls_data["polls"][poll_id]
            await save_polls(context)
            await update.callback_query.answer("Опрос удалён!")
            await my_polls(update, context)
        else:
            await update.callback_query.answer("Нет доступа!", show_alert=True)
    except Exception as e:
        logger.error(f"Error in delete_poll: {e}")
        await handle_error(update, context)

async def edit_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        poll_id = update.callback_query.data.split("_", 2)[-1]
        poll = polls_data["polls"].get(poll_id)
        
        if not poll or poll.get("creator") != user_id:
            await update.callback_query.answer("Нет доступа!", show_alert=True)
            return
        
        context.user_data["editing_poll_id"] = poll_id
        context.user_data["editing_poll"] = poll.copy()
        
        keyboard = [
            [InlineKeyboardButton("📌 Изменить название", callback_data="edit_title")],
            [InlineKeyboardButton("📝 Изменить вопросы", callback_data="edit_questions")],
            [InlineKeyboardButton("🏆 Изменить результаты", callback_data="edit_results")],
            [InlineKeyboardButton("🔙 Назад", callback_data=f"my_poll_{poll_id}")]
        ]
        
        await update.callback_query.edit_message_text(
            f"✏️ <b>Редактирование опроса:</b> {poll['title']}\n"
            "Выберите что хотите изменить:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return EDIT_CHOICE
    except Exception as e:
        logger.error(f"Error in edit_poll: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def edit_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "📝 Введите новое название опроса:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")]
            ])
        )
        return EDIT_TITLE
    except Exception as e:
        logger.error(f"Error in edit_title: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_edit_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_title = update.message.text.strip()
        if len(new_title) > 100:
            await update.message.reply_text("⚠️ Слишком длинное название! Максимум 100 символов.")
            return EDIT_TITLE
        
        poll_id = context.user_data["editing_poll_id"]
        polls_data["polls"][poll_id]["title"] = new_title
        await save_polls(context)
        
        await update.message.reply_text(
            "✅ Название успешно изменено!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 К редактированию", callback_data=f"edit_poll_{poll_id}")]
            ])
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in process_edit_title: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def edit_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        poll_id = context.user_data["editing_poll_id"]
        poll = polls_data["polls"][poll_id]
        
        keyboard = [
            [InlineKeyboardButton(
                f"{i+1}. {q['text'][:30]}..." if len(q['text']) > 30 else f"{i+1}. {q['text']}",
                callback_data=f"edit_question_{i}"
            )]
            for i, q in enumerate(poll["questions"])
        ]
        keyboard.append([InlineKeyboardButton("➕ Добавить вопрос", callback_data="add_question")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"edit_poll_{poll_id}")])
        
        await update.callback_query.edit_message_text(
            "📝 Выберите вопрос для редактирования:",
            reply_markup=InlineKeyboardMarkup(keyboard))
        return EDIT_QUESTIONS
    except Exception as e:
        logger.error(f"Error in edit_questions: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def edit_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        poll_id = context.user_data["editing_poll_id"]
        question_idx = int(update.callback_query.data.split("_")[-1])
        question = polls_data["polls"][poll_id]["questions"][question_idx]
        
        context.user_data["editing_question_idx"] = question_idx
        
        keyboard = [
            [InlineKeyboardButton("📝 Текст вопроса", callback_data=f"edit_qtext_{question_idx}")],
            [InlineKeyboardButton("🖼️ Изображение", callback_data=f"edit_qimage_{question_idx}")],
            [InlineKeyboardButton("📋 Варианты ответов", callback_data=f"edit_qoptions_{question_idx}")],
            [InlineKeyboardButton("🗑️ Удалить вопрос", callback_data=f"delete_question_{question_idx}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="edit_questions")]
        ]
        
        await update.callback_query.edit_message_text(
            f"✏️ Редактирование вопроса {question_idx+1}:\n\n"
            f"{question['text']}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EDIT_QUESTION
    except Exception as e:
        logger.error(f"Error in edit_question: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def edit_question_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        question_idx = int(update.callback_query.data.split("_")[-1])
        context.user_data["editing_question_idx"] = question_idx
        
        await update.callback_query.edit_message_text(
            "📝 Введите новый текст вопроса:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data=f"edit_question_{question_idx}")]
            ])
        )
        return EDIT_QUESTION
    except Exception as e:
        logger.error(f"Error in edit_question_text: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_edit_question_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_text = update.message.text.strip()
        if len(new_text) > 300:
            await update.message.reply_text("⚠️ Слишком длинный вопрос! Максимум 300 символов.")
            return
        
        poll_id = context.user_data["editing_poll_id"]
        question_idx = context.user_data["editing_question_idx"]
        polls_data["polls"][poll_id]["questions"][question_idx]["text"] = new_text
        await save_polls(context)
        
        await update.message.reply_text(
            "✅ Текст вопроса успешно изменен!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 К вопросу", callback_data=f"edit_question_{question_idx}")]
            ])
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in process_edit_question_text: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def edit_question_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        question_idx = int(update.callback_query.data.split("_")[-1])
        context.user_data["editing_question_idx"] = question_idx
        
        await update.callback_query.edit_message_text(
            "🖼️ Отправьте новое изображение для вопроса или нажмите 'Удалить':",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🗑️ Удалить изображение", callback_data=f"delete_qimage_{question_idx}")],
                [InlineKeyboardButton("❌ Отмена", callback_data=f"edit_question_{question_idx}")]
            ])
        )
        return EDIT_QUESTION
    except Exception as e:
        logger.error(f"Error in edit_question_image: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_edit_question_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        poll_id = context.user_data["editing_poll_id"]
        question_idx = context.user_data["editing_question_idx"]
        
        photo = max(update.message.photo, key=lambda p: p.file_size)
        filename = await save_file(photo.file_id, context)
        if filename:
            polls_data["polls"][poll_id]["questions"][question_idx]["image"] = {
                "file_id": photo.file_id,
                "local_path": filename
            }
            await save_polls(context)
        
        await update.message.reply_text(
            "✅ Изображение вопроса обновлено!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 К вопросу", callback_data=f"edit_question_{question_idx}")]
            ])
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in process_edit_question_image: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def delete_question_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        question_idx = int(update.callback_query.data.split("_")[-1])
        poll_id = context.user_data["editing_poll_id"]
        
        if "image" in polls_data["polls"][poll_id]["questions"][question_idx]:
            try:
                os.remove(os.path.join(MEDIA_FOLDER, polls_data["polls"][poll_id]["questions"][question_idx]["image"]["local_path"]))
            except:
                pass
            del polls_data["polls"][poll_id]["questions"][question_idx]["image"]
            await save_polls(context)
            await update.callback_query.answer("Изображение удалено!")
        else:
            await update.callback_query.answer("Нет изображения для удаления!")
        
        await update.callback_query.edit_message_text(
            "🖼️ Изображение вопроса удалено.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 К вопросу", callback_data=f"edit_question_{question_idx}")]
            ])
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in delete_question_image: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def edit_question_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        question_idx = int(update.callback_query.data.split("_")[-1])
        poll_id = context.user_data["editing_poll_id"]
        question = polls_data["polls"][poll_id]["questions"][question_idx]
        
        context.user_data["editing_question_idx"] = question_idx
        
        options_text = "\n".join(
            f"{i+1}. {opt['text']} ({'+' if opt['weight'] >= 0 else ''}{opt['weight']})"
            for i, opt in enumerate(question["options"])
        )
        
        keyboard = [
            [InlineKeyboardButton("✏️ Изменить варианты", callback_data=f"edit_qoptions_full_{question_idx}")],
            [InlineKeyboardButton("🔙 Назад", callback_data=f"edit_question_{question_idx}")]
        ]
        
        await update.callback_query.edit_message_text(
            f"📋 Текущие варианты ответов:\n\n{options_text}\n\n"
            "Вы можете полностью перезаписать варианты ответов:",
            reply_markup=InlineKeyboardMarkup(keyboard))
        
        return EDIT_OPTIONS
    except Exception as e:
        logger.error(f"Error in edit_question_options: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def edit_question_options_full(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        question_idx = int(update.callback_query.data.split("_")[-1])
        poll_id = context.user_data["editing_poll_id"]
        question = polls_data["polls"][poll_id]["questions"][question_idx]
        
        await update.callback_query.edit_message_text(
            "📝 Введите новые варианты ответов (каждый с новой строки, формат: Текст|Баллы):\n\n"
            "Пример:\n"
            "Да|2\n"
            "Нет|-1\n"
            "Не знаю|0",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data=f"edit_qoptions_{question_idx}")]
            ])
        )
        return EDIT_OPTIONS
    except Exception as e:
        logger.error(f"Error in edit_question_options_full: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_edit_question_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        options = []
        for line in update.message.text.split("\n"):
            if line.strip() and "|" in line:
                text, weight = line.split("|", 1)
                options.append({"text": text.strip(), "weight": int(weight.strip())})

        if len(options) < 2:
            raise ValueError("❕ Нужно минимум 2 варианта ответа")
        if len(options) > 10:
            raise ValueError("❕ Максимум 10 вариантов ответа")

        poll_id = context.user_data["editing_poll_id"]
        question_idx = context.user_data["editing_question_idx"]
        polls_data["polls"][poll_id]["questions"][question_idx]["options"] = options
        await save_polls(context)

        await update.message.reply_text(
            "✅ Варианты ответов успешно обновлены!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 К вопросу", callback_data=f"edit_question_{question_idx}")]
            ])
        )
        return ConversationHandler.END

    except ValueError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}\nПопробуйте ещё раз:")
        return EDIT_OPTIONS
    except Exception as e:
        logger.error(f"Error in process_edit_question_options: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        question_idx = int(update.callback_query.data.split("_")[-1])
        poll_id = context.user_data["editing_poll_id"]
        
        if len(polls_data["polls"][poll_id]["questions"]) <= 4:
            await update.callback_query.answer("❌ Нельзя удалить - минимум 4 вопроса!", show_alert=True)
            return
        
        if "image" in polls_data["polls"][poll_id]["questions"][question_idx]:
            try:
                os.remove(os.path.join(MEDIA_FOLDER, polls_data["polls"][poll_id]["questions"][question_idx]["image"]["local_path"]))
            except:
                pass
        
        del polls_data["polls"][poll_id]["questions"][question_idx]
        await save_polls(context)
        
        await update.callback_query.edit_message_text(
            "✅ Вопрос удален!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 К списку вопросов", callback_data="edit_questions")]
            ])
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in delete_question: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def add_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        poll_id = context.user_data["editing_poll_id"]
        poll = polls_data["polls"][poll_id]
        
        if len(poll["questions"]) >= 30:
            await update.callback_query.answer("❌ Максимум 30 вопросов!", show_alert=True)
            return
        
        context.user_data["adding_question"] = True
        context.user_data["question_number"] = len(poll["questions"]) + 1
        
        await update.callback_query.edit_message_text(
            f"📝 Введите текст нового вопроса {context.user_data['question_number']}:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="edit_questions")]
            ])
        )
        return QUESTION
    except Exception as e:
        logger.error(f"Error in add_question: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def edit_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        poll_id = context.user_data["editing_poll_id"]
        poll = polls_data["polls"][poll_id]
        
        results_text = "\n".join(
            f"{name}: от {score} баллов"
            for name, score in poll["thresholds"]
        )
        
        keyboard = [
            [InlineKeyboardButton("✏️ Изменить результаты", callback_data="edit_results_full")],
            [InlineKeyboardButton("🖼️ Изменить изображения", callback_data="edit_result_images")],
            [InlineKeyboardButton("🔙 Назад", callback_data=f"edit_poll_{poll_id}")]
        ]
        
        await update.callback_query.edit_message_text(
            f"🏆 Текущие результаты:\n\n{results_text}\n\n"
            "Вы можете изменить пороги результатов или их изображения:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EDIT_RESULTS
    except Exception as e:
        logger.error(f"Error in edit_results: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def edit_results_full(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        poll_id = context.user_data["editing_poll_id"]
        poll = polls_data["polls"][poll_id]
        
        min_score = sum(min(opt["weight"] for opt in q["options"]) for q in poll["questions"])
        max_score = sum(max(opt["weight"] for opt in q["options"]) for q in poll["questions"])
        
        await update.callback_query.edit_message_text(
            f"📝 Введите новые результаты (каждый с новой строки, формат: Название|Минимальный балл):\n\n"
            f"Диапазон возможных баллов: от {min_score} до {max_score}\n\n"
            "Пример:\n"
            "Отлично|15\n"
            "Хорошо|10\n"
            "Удовлетворительно|5",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="edit_results")]
            ])
        )
        return EDIT_RESULTS
    except Exception as e:
        logger.error(f"Error in edit_results_full: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_edit_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        thresholds = []
        for line in update.message.text.split("\n"):
            if line.strip() and "|" in line:
                name, score = line.split("|", 1)
                thresholds.append((name.strip(), int(score.strip())))

        poll_id = context.user_data["editing_poll_id"]
        poll = polls_data["polls"][poll_id]
        
        min_score = sum(min(opt["weight"] for opt in q["options"]) for q in poll["questions"])
        max_score = sum(max(opt["weight"] for opt in q["options"]) for q in poll["questions"])

        if len(thresholds) < 1:
            raise ValueError(f"❕ Нужно минимум 1 результат")
        if len(thresholds) > 12:
            raise ValueError(f"❕ Максимум 12 результатов")

        thresholds.sort(key=lambda x: x[1], reverse=True)

        if thresholds[0][1] > max_score:
            raise ValueError(f"❕ Максимальный порог {thresholds[0][1]} превышает возможный максимум {max_score}")
        if thresholds[-1][1] < min_score:
            raise ValueError(f"❕ Минимальный порог {thresholds[-1][1]} ниже возможного минимума {min_score}")

        for i in range(1, len(thresholds)):
            if thresholds[i-1][1] <= thresholds[i][1]:
                raise ValueError("❕ Пороги должны идти в убывающем порядке")

        if thresholds[-1][1] > min_score:
            thresholds.append(("Минимальный результат", min_score))

        result_images = {}
        if "result_images" in poll:
            for name, score in thresholds:
                if name in poll["result_images"]:
                    result_images[name] = poll["result_images"][name]

        polls_data["polls"][poll_id]["thresholds"] = thresholds
        polls_data["polls"][poll_id]["result_images"] = result_images
        await save_polls(context)

        await update.message.reply_text(
            "✅ Результаты успешно обновлены!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 К редактированию", callback_data=f"edit_poll_{poll_id}")]
            ])
        )
        return ConversationHandler.END

    except ValueError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}\nПопробуйте ещё раз:")
        return EDIT_RESULTS
    except Exception as e:
        logger.error(f"Error in process_edit_results: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def edit_result_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        poll_id = context.user_data["editing_poll_id"]
        poll = polls_data["polls"][poll_id]
        
        context.user_data["editing_result_idx"] = 0
        result_name = poll["thresholds"][0][0]
        
        await update.callback_query.edit_message_text(
            f"🖼️ Редактирование изображения для результата: {result_name}\n\n"
            "Отправьте новое изображение или нажмите 'Пропустить':",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏭ Пропустить", callback_data="skip_edit_result_image")],
                [InlineKeyboardButton("🗑️ Удалить", callback_data="delete_result_image")],
                [InlineKeyboardButton("❌ Отмена", callback_data="edit_results")]
            ])
        )
        return RESULT_IMAGE
    except Exception as e:
        logger.error(f"Error in edit_result_images: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        poll_id = context.user_data.get("editing_poll_id")
        if poll_id:
            await update.callback_query.edit_message_text(
                "❌ Редактирование отменено.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К опросу", callback_data=f"my_poll_{poll_id}")]
                ])
            )
        else:
            await update.callback_query.edit_message_text(
                "❌ Редактирование отменено.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 В меню", callback_data="main_menu")]
                ])
            )
        
        if "editing_poll_id" in context.user_data:
            del context.user_data["editing_poll_id"]
        if "editing_poll" in context.user_data:
            del context.user_data["editing_poll"]
        
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in cancel_edit: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def post_add_at_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("⛔ У вас нет доступа к этой команде")
            return
        
        context.user_data["awaiting_message"] = True
        
        await update.message.reply_text(
            "🕒 Отправьте сообщение, которое нужно опубликовать позже:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_scheduled_post")]
            ])
        )
        return AWAITING_MESSAGE
    except Exception as e:
        logger.error(f"Error in post_add_at_time: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_scheduled_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            return
        
        if "awaiting_message" not in context.user_data:
            return
        
        message_data = {
            "content_type": "text",
            "content_text": update.message.text or update.message.caption,
            "content_file_id": None
        }
        
        if update.message.photo:
            photo = max(update.message.photo, key=lambda p: p.file_size)
            message_data["content_type"] = "photo"
            message_data["content_file_id"] = photo.file_id
        elif update.message.video:
            message_data["content_type"] = "video"
            message_data["content_file_id"] = update.message.video.file_id
        elif update.message.document:
            message_data["content_type"] = "document"
            message_data["content_file_id"] = update.message.document.file_id
        
        context.user_data["scheduled_message"] = message_data
        context.user_data["awaiting_time"] = True
        del context.user_data["awaiting_message"]
        
        await update.message.reply_text(
            "⏰ Теперь укажите время публикации в формате ДД.ММ.ГГГГ ЧЧ:ММ\n"
            "Например: 15.05.2025 14:30",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel_scheduled_post")]
            ])
        )
        return AWAITING_TIME
    except Exception as e:
        logger.error(f"Error in process_scheduled_message: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def process_scheduled_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            return
        
        if "awaiting_time" not in context.user_data:
            return
        
        try:
            time_str = update.message.text.strip()
            publish_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M")
            
            now = datetime.now()
            if publish_time <= now:
                await update.message.reply_text("⚠️ Время должно быть в будущем!")
                return AWAITING_TIME
            
            message_data = context.user_data["scheduled_message"]
            post_id = add_scheduled_post(
                message_data["content_type"],
                message_data["content_text"],
                message_data["content_file_id"],
                time_str
            )
            
            delay = (publish_time - now).total_seconds()
            context.job_queue.run_once(
                callback=publish_scheduled_message,
                when=delay,
                data={"post_id": post_id},
                name=f"scheduled_post_{post_id}"
            )
            
            del context.user_data["awaiting_time"]
            del context.user_data["scheduled_message"]
            
            await update.message.reply_text(
                f"✅ Сообщение запланировано на {time_str} (ID: {post_id})",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]
                ])
            )
            return ConversationHandler.END
        
        except ValueError:
            await update.message.reply_text("⚠️ Неверный формат времени! Используйте ДД.ММ.ГГГГ ЧЧ:ММ")
            return AWAITING_TIME
    except Exception as e:
        logger.error(f"Error in process_scheduled_time: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def publish_scheduled_message(context: ContextTypes.DEFAULT_TYPE):
    try:
        job = context.job
        post_id = job.data["post_id"]
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT content_type, content_text, content_file_id 
        FROM scheduled_posts 
        WHERE post_id = ? AND status = 'pending'
        ''', (post_id,))
        
        post_data = cursor.fetchone()
        if not post_data:
            logger.error(f"Scheduled post {post_id} not found or already sent")
            return
        
        content_type, content_text, content_file_id = post_data
        
        users = get_all_users()
        success = 0
        failures = 0
        
        for user_id in users:
            try:
                if content_type == "photo":
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=content_file_id,
                        caption=content_text
                    )
                elif content_type == "video":
                    await context.bot.send_video(
                        chat_id=user_id,
                        video=content_file_id,
                        caption=content_text
                    )
                elif content_type == "document":
                    await context.bot.send_document(
                        chat_id=user_id,
                        document=content_file_id,
                        caption=content_text
                    )
                else:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=content_text
                    )
                success += 1
            except Exception as e:
                logger.error(f"Failed to send post {post_id} to {user_id}: {e}")
                failures += 1
        
        mark_post_as_sent(post_id)
        conn.close()
        
        report = (
            f"📢 Рассылка завершена (ID: {post_id})\n"
            f"✅ Успешно: {success}\n"
            f"❌ Ошибок: {failures}"
        )
        
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=report)
        except Exception as e:
            logger.error(f"Failed to send report to admin: {e}")
    except Exception as e:
        logger.error(f"Error in publish_scheduled_message: {e}")

async def cancel_scheduled_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            await update.callback_query.answer("⛔ У вас нет доступа", show_alert=True)
            return
        
        if "awaiting_message" in context.user_data:
            del context.user_data["awaiting_message"]
        if "awaiting_time" in context.user_data:
            del context.user_data["awaiting_time"]
        if "scheduled_message" in context.user_data:
            del context.user_data["scheduled_message"]
        
        await update.callback_query.answer("❌ Публикация отменена")
        await update.callback_query.edit_message_text(
            "🗑️ Запланированная публикация отменена.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]
            ])
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in cancel_scheduled_post: {e}")
        await handle_error(update, context)
        return ConversationHandler.END

async def restore_scheduled_jobs(application: Application):
    try:
        pending_posts = get_pending_posts()
        now = datetime.now()
        
        for post in pending_posts:
            try:
                post_time = datetime.strptime(post["scheduled_time"], "%d.%m.%Y %H:%M")
                
                if post_time <= now:
                    mark_post_as_sent(post["post_id"])
                    continue
                
                delay = (post_time - now).total_seconds()
                
                application.job_queue.run_once(
                    callback=publish_scheduled_message,
                    when=delay,
                    data={"post_id": post["post_id"]},
                    name=f"scheduled_post_{post['post_id']}"
                )
                
                logger.info(f"Restored scheduled post {post['post_id']} for {post['scheduled_time']}")
            
            except Exception as e:
                logger.error(f"Failed to restore post {post['post_id']}: {e}")
    except Exception as e:
        logger.error(f"Error in restore_scheduled_jobs: {e}")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

def setup_handlers(application):
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(create_poll, pattern="^create_poll$")],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_title)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_question)],
            QUESTION_IMAGE: [
                MessageHandler(filters.PHOTO, process_question_image),
                CallbackQueryHandler(process_question_image, pattern="^skip_image$")
            ],
            OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_options)],
            NEXT_QUESTION: [
                CallbackQueryHandler(next_question, pattern="^next_question$"),
                CallbackQueryHandler(to_results, pattern="^to_results$"),
                CallbackQueryHandler(need_more_questions, pattern="^need_more_questions$")
            ],
            RESULTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_results)],
            RESULT_IMAGE: [
                MessageHandler(filters.PHOTO, process_result_image),
                CallbackQueryHandler(process_result_image, pattern="^skip_result_image$")
            ],
            CONFIRM: [
                CallbackQueryHandler(save_poll, pattern="^save_poll$"),
                CallbackQueryHandler(cancel_poll, pattern="^cancel_poll$")
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_poll),
            CallbackQueryHandler(cancel_poll, pattern="^cancel_poll$")
        ],
        per_message=False
    )

    edit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_poll, pattern="^edit_poll_")],
        states={
            EDIT_CHOICE: [
                CallbackQueryHandler(edit_title, pattern="^edit_title$"),
                CallbackQueryHandler(edit_questions, pattern="^edit_questions$"),
                CallbackQueryHandler(edit_results, pattern="^edit_results$"),
                CallbackQueryHandler(cancel_edit, pattern="^cancel_edit$")
            ],
            EDIT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_edit_title)],
            EDIT_QUESTIONS: [
                CallbackQueryHandler(edit_question, pattern=r"^edit_question_\d+$"),
                CallbackQueryHandler(add_question, pattern="^add_question$"),
                CallbackQueryHandler(cancel_edit, pattern="^cancel_edit$")
            ],
            EDIT_QUESTION: [
                CallbackQueryHandler(edit_question_text, pattern=r"^edit_qtext_\d+$"),
                CallbackQueryHandler(edit_question_image, pattern=r"^edit_qimage_\d+$"),
                CallbackQueryHandler(edit_question_options, pattern=r"^edit_qoptions_\d+$"),
                CallbackQueryHandler(delete_question, pattern=r"^delete_question_\d+$"),
                CallbackQueryHandler(cancel_edit, pattern="^cancel_edit$")
            ],
            EDIT_OPTIONS: [
                CallbackQueryHandler(edit_question_options_full, pattern=r"^edit_qoptions_full_\d+$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_edit_question_options),
                CallbackQueryHandler(cancel_edit, pattern="^cancel_edit$")
            ],
            EDIT_RESULTS: [
                CallbackQueryHandler(edit_results_full, pattern="^edit_results_full$"),
                CallbackQueryHandler(edit_result_images, pattern="^edit_result_images$"),
                CallbackQueryHandler(cancel_edit, pattern="^cancel_edit$")
            ],
            RESULT_IMAGE: [
                MessageHandler(filters.PHOTO, process_result_image),
                CallbackQueryHandler(process_result_image, pattern="^skip_edit_result_image$"),
                CallbackQueryHandler(delete_question_image, pattern="^delete_result_image$"),
                CallbackQueryHandler(cancel_edit, pattern="^cancel_edit$")
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_edit),
            CallbackQueryHandler(cancel_edit, pattern="^cancel_edit$")
        ],
        per_message=False
    )

    post_conv = ConversationHandler(
        entry_points=[CommandHandler("postaddattime", post_add_at_time, filters.User(ADMIN_ID))],
        states={
            AWAITING_MESSAGE: [
                MessageHandler(
                    (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL),
                    process_scheduled_message
                )
            ],
            AWAITING_TIME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & filters.Regex(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}"),
                    process_scheduled_time
                )
            ]
        },
        fallbacks=[
            CallbackQueryHandler(cancel_scheduled_post, pattern="^cancel_scheduled_post$")
        ],
        per_message=True
    )

    share_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(share_poll, pattern=r"^share_poll_")],
        states={
            SHARE_POLL: [
                CallbackQueryHandler(share_with_image, pattern="^share_with_image$"),
                CallbackQueryHandler(share_without_image, pattern="^share_without_image$"),
                CallbackQueryHandler(cancel_share, pattern="^cancel_share$")
            ],
            SHARE_WITH_IMAGE: [
                MessageHandler(filters.PHOTO, process_share_image),
                CallbackQueryHandler(cancel_share, pattern="^cancel_share$")
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_share),
            CallbackQueryHandler(cancel_share, pattern="^cancel_share$")
        ],
        per_message=True
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(list_polls, pattern="^list_polls$"))
    application.add_handler(CallbackQueryHandler(start_poll, pattern="^start_poll_"))
    application.add_handler(CallbackQueryHandler(process_answer, pattern=r"^answer_\d+_\d+$"))
    application.add_handler(CallbackQueryHandler(my_polls, pattern="^my_polls$"))
    application.add_handler(CallbackQueryHandler(my_poll_menu, pattern="^my_poll_"))
    application.add_handler(CallbackQueryHandler(delete_poll, pattern="^delete_poll_"))
    application.add_handler(CallbackQueryHandler(cancel_poll_session, pattern="^cancel_poll_session$"))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(confirm_delete_poll, pattern="^delete_confirm_"))  # Для подтверждения
    application.add_handler(CallbackQueryHandler(delete_poll, pattern="^delete_poll_"))
    
    application.add_handler(conv_handler)
    application.add_handler(edit_conv)
    application.add_handler(post_conv)
    application.add_handler(share_conv)

async def on_startup(application: Application):
    await set_commands(application)
    try:
        load_polls()
        await restore_scheduled_jobs(application)
        logger.info("Bot started and scheduled jobs restored")
    except Exception as e:
        logger.error(f"Error in on_startup: {e}")

def main():
    try:
        init_db()
        
        application = Application.builder().token(TOKEN).post_init(on_startup).build()
        setup_handlers(application)
        
        application.run_polling()
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()