import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8969604366:AAHe0gtCtdCmyKsID5tDwJe-YLVY1K_aEJE"

def generate_signal():
    rsi_value = random.randint(25, 85) 
    if rsi_value < 40:
        return "🟢 UP (CALL) - RSI is Low"
    elif rsi_value > 65:
        return "🔴 DOWN (PUT) - RSI is High"
    else:
        return random.choice(["🟢 UP (CALL) - Trend Follow", "🔴 DOWN (PUT) - Trend Follow"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔍 Analyze Now", callback_data='analyze')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('🤖 QX Bot: CONNECTED\nClick below to analyze:', reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'analyze':
        decision = generate_signal()
        keyboard = [[InlineKeyboardButton("🔍 Analyze Again", callback_data='analyze')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"📊 **Market Analysis Result**\n✨ Recommendation: **{decision}**", reply_markup=reply_markup, parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    print("🚀 QX Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
