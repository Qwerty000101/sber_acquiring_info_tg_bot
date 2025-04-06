import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN
from messages import MESSAGES
# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def log_user_action(update: Update, action: str):
    user = update.effective_user
    if user:
        user_info = f"ID: {user.id}, Имя: {user.full_name}"
        if update.callback_query:
            logger.info(f"Пользователь {user_info} нажал кнопку: {action}")
        elif update.message:
            logger.info(f"Пользователь {user_info} отправил сообщение: {action}")
        print(f"Действие пользователя: {user_info}, Действие: {action}")


def get_start_keyboard():
    return ReplyKeyboardMarkup(
        [["Общая информация", "Подключение и отключение"]],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

def get_inline_keyboard(current_step=None, back_step=None):
    buttons = []
    
    # Основные кнопки для разных шагов
    if current_step == "general_info":
        buttons = [
            [InlineKeyboardButton("Какие карты можно принимать", callback_data="cards:general_info")],
            [InlineKeyboardButton("Как посмотреть операции", callback_data="operations:general_info")]
        ]
    elif current_step == "cards_info":
        buttons = [[InlineKeyboardButton("Назад", callback_data=f"back:{back_step}")]]
    elif current_step == "operations_info":
        buttons = [[InlineKeyboardButton("Назад", callback_data=f"back:{back_step}")]]
    else:
        buttons = [
            [InlineKeyboardButton("Какие карты можно принимать", callback_data="cards:main")],
            [InlineKeyboardButton("Как посмотреть операции", callback_data="operations:main")]
        ]
    
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update, "Команда /start")
    await update.message.reply_text(
        MESSAGES["start"],
        reply_markup=get_start_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    log_user_action(update, f"Текст: '{text}'")
    
    if text == "Общая информация":
        await update.message.reply_text(
            MESSAGES["general_info"],
            reply_markup=get_inline_keyboard(current_step="general_info")
        )
    elif text == "Подключение и отключение":
        await update.message.reply_text(MESSAGES["connection_info"])

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    log_user_action(update, f"Кнопка: '{data}'")
    
    if data.startswith("back:"):
        # Обработка кнопки "Назад"
        back_step = data.split(":")[1]
        if back_step == "general_info":
            await query.edit_message_text(
                MESSAGES[back_step],
                reply_markup=get_inline_keyboard(current_step=back_step)
            )
        elif back_step == "main":
            await query.edit_message_text(
                MESSAGES["start"],
                reply_markup=get_start_keyboard()
            )
    else:
        # Обработка обычных кнопок
        action, back_step = data.split(":")
        if action == "cards":
            await query.edit_message_text(
                MESSAGES["cards_info"],
                reply_markup=get_inline_keyboard(current_step="cards_info", back_step=back_step)
            )
        elif action == "operations":
            await query.edit_message_text(
                MESSAGES["operations_info"],
                reply_markup=get_inline_keyboard(current_step="operations_info", back_step=back_step)
            )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}", exc_info=True)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)
    
    print("Бот запущен и готов к работе...")
    application.run_polling()

if __name__ == "__main__":
    main()