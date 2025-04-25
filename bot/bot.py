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
        [
            ["Общая информация по операциям"],
            ["Подключение и отключение эквайринга"],
            ["Зачисление денег"],
            ["Стоимость и оплата услуг эквайринга"],
            ["Техническая поддержка эквайринга"],
            ["Стоимость эквайринга на условиях публичных тарифов"],
            ["Управление эквайрингом"]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел"
    )

def get_inline_keyboard(current_step=None, back_step=None):
    buttons = []
    
    if current_step == "general_info":
        buttons = [
            [InlineKeyboardButton("Какие карты можно принимать к оплате", callback_data="cards:general_info")],
            [InlineKeyboardButton("Где посмотреть информацию по операциям", callback_data="operations:general_info")],
            [InlineKeyboardButton("Срок возврата средств при отмене", callback_data="return:general_info")],
            [InlineKeyboardButton("Карты American Express", callback_data="americanexpress:general_info")]
        ]
    elif current_step == "connection_info":
        buttons = [
            [InlineKeyboardButton("Как подключить эквайринг", callback_data="connect:connection_info")],
            [InlineKeyboardButton("Расторжение договора", callback_data="disconnect:connection_info")]
        ]
    elif current_step == "money_info":
        buttons = [
            [InlineKeyboardButton("Проверка зачисления выручки", callback_data="check_money:money_info")],
            [InlineKeyboardButton("Сроки зачисления", callback_data="money_terms:money_info")],
            [InlineKeyboardButton("Почему зачисление не сразу", callback_data="money_delay:money_info")]
        ]
    elif current_step == "cost_info":
        buttons = [
            [InlineKeyboardButton("Стоимость услуг", callback_data="service_cost:cost_info")],
            [InlineKeyboardButton("Как сэкономить", callback_data="save_money:cost_info")],
            [InlineKeyboardButton("Кешбэк по картам", callback_data="cashback:cost_info")],
            [InlineKeyboardButton("Перенос комиссии на плательщика", callback_data="fee_transfer:cost_info")],
            [InlineKeyboardButton("Эквайринг без 3D-Secure", callback_data="no_3dsecure:cost_info")],
            [InlineKeyboardButton("Оплата из-за границы", callback_data="foreign_payments:cost_info")],
            [InlineKeyboardButton("Комиссия при отказе", callback_data="refund_fee:cost_info")]
        ]
    elif current_step == "support_info":
        buttons = [
            [InlineKeyboardButton("Не работает POS-терминал", callback_data="pos_problem:support_info")],
            [InlineKeyboardButton("Не работает интернет-эквайринг", callback_data="online_problem:support_info")],
            [InlineKeyboardButton("СМС-информирование", callback_data="sms_info:support_info")],
            [InlineKeyboardButton("Программа 'Спасибо'", callback_data="thanks_program:support_info")]
        ]
    elif current_step == "tariffs_info":
        buttons = [
            [InlineKeyboardButton("Состав тарифа", callback_data="tariff_structure:tariffs_info")],
            [InlineKeyboardButton("Динамический тариф", callback_data="dynamic_tariff:tariffs_info")],
            [InlineKeyboardButton("Расчёт динамического тарифа", callback_data="tariff_calc:tariffs_info")],
            [InlineKeyboardButton("Начальный тариф", callback_data="initial_tariff:tariffs_info")],
            [InlineKeyboardButton("Промотариф", callback_data="promo_tariff:tariffs_info")],
            [InlineKeyboardButton("Бесплатный POS-терминал", callback_data="free_pos:tariffs_info")],
            [InlineKeyboardButton("Тариф за смарт-терминал", callback_data="smart_terminal:tariffs_info")],
            [InlineKeyboardButton("Начисление сервисной платы", callback_data="service_fee:tariffs_info")],
            [InlineKeyboardButton("Оплата сервисной платы", callback_data="fee_payment:tariffs_info")]
        ]
    elif current_step in ["cards_info", "operations_info", "return_info", "americanexpress_info",
                         "connect_info", "disconnect_info", "check_money_info", "money_terms_info",
                         "money_delay_info", "service_cost_info", "save_money_info", "cashback_info",
                         "fee_transfer_info", "no_3dsecure_info", "foreign_payments_info", "refund_fee_info",
                         "pos_problem_info", "online_problem_info", "sms_info_info", "thanks_program_info",
                         "tariff_structure_info", "dynamic_tariff_info", "tariff_calc_info", "initial_tariff_info",
                         "promo_tariff_info", "free_pos_info", "smart_terminal_info", "service_fee_info",
                         "fee_payment_info"]:
        buttons = [[InlineKeyboardButton("Назад", callback_data=f"back:{back_step}")]]
    elif current_step == "management_info":
        buttons = [
            [InlineKeyboardButton("Текущий и будущий тариф", callback_data="tariff_view:management_info")],
            [InlineKeyboardButton("Счёт за сервисную плату", callback_data="service_invoice:management_info")],
            [InlineKeyboardButton("Отчёт по зачислениям", callback_data="income_report:management_info")],
            [InlineKeyboardButton("Возврат покупки", callback_data="refund_process:management_info")],
            [InlineKeyboardButton("Заказ оборудования", callback_data="order_equipment:management_info")],
            [InlineKeyboardButton("Новая торговая точка", callback_data="new_outlet:management_info")],
            [InlineKeyboardButton("Изменение данных точки", callback_data="outlet_update:management_info")],
            [InlineKeyboardButton("Оплаты по SberPay QR", callback_data="sberpay_qr:management_info")],
            [InlineKeyboardButton("Логин QR кассира", callback_data="qr_cashier:management_info")],
            [InlineKeyboardButton("Настройка смартфона", callback_data="phone_setup:management_info")],
            [InlineKeyboardButton("История оплат QR", callback_data="qr_history:management_info")],
            [InlineKeyboardButton("Разблокировка QR", callback_data="qr_unlock:management_info")],
            [InlineKeyboardButton("Блокировка оборудования", callback_data="equipment_block:management_info")],
            [InlineKeyboardButton("Поддержка эквайринга", callback_data="management_support:management_info")]
        ]
    elif current_step in ["tariff_view_info", "service_invoice_info", "income_report_info",
                         "refund_process_info", "order_equipment_info", "new_outlet_info",
                         "outlet_update_info", "sberpay_qr_info", "qr_cashier_info",
                         "phone_setup_info", "qr_history_info", "qr_unlock_info",
                         "equipment_block_info", "management_support_info"]:
        buttons = [[InlineKeyboardButton("Назад", callback_data=f"back:{back_step}")]]
    
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
    
    if text == "Общая информация по операциям":
        await update.message.reply_text(
            MESSAGES["general_info"],
            reply_markup=get_inline_keyboard(current_step="general_info")
        )
    elif text == "Подключение и отключение эквайринга":
        await update.message.reply_text(
            MESSAGES["connection_info"],
            reply_markup=get_inline_keyboard(current_step="connection_info")
        )
    elif text == "Зачисление денег":
        await update.message.reply_text(
            MESSAGES["money_info"],
            reply_markup=get_inline_keyboard(current_step="money_info")
        )
    elif text == "Стоимость и оплата услуг эквайринга":
        await update.message.reply_text(
            MESSAGES["cost_info"],
            reply_markup=get_inline_keyboard(current_step="cost_info")
        )
    elif text == "Техническая поддержка эквайринга":
        await update.message.reply_text(
            MESSAGES["support_info"],
            reply_markup=get_inline_keyboard(current_step="support_info")
        )
    elif text == "Стоимость эквайринга на условиях публичных тарифов":
        await update.message.reply_text(
            MESSAGES["tariffs_info"],
            reply_markup=get_inline_keyboard(current_step="tariffs_info")
        )
    elif text == "Управление эквайрингом":
        await update.message.reply_text(
            MESSAGES["management_info"],
            reply_markup=get_inline_keyboard(current_step="management_info")
        )
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    log_user_action(update, f"Кнопка: '{data}'")
    
    if data.startswith("back:"):
        back_step = data.split(":")[1]
        if back_step in ["general_info", "connection_info", "money_info", "cost_info", "support_info", "tariffs_info", "management_info"]:
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
        action, back_step = data.split(":")
        message_key = f"{action}_info"
        
        if message_key in MESSAGES:
            await query.edit_message_text(
                MESSAGES[message_key],
                reply_markup=get_inline_keyboard(current_step=message_key, back_step=back_step)
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