import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import yfinance as yf
import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.environ.get("TELEGRAM_TOKEN")

# রেন্ডারের Failed এরর বন্ধ করার জন্য ওয়েব সার্ভার
def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"🌍 Web server running on port {port}")
    server.serve_forever()

def generate_signal():
    try:
        ticker = yf.Ticker("EURUSD=X")
        df = ticker.history(period="1d", interval="5m")
        if df.empty:
            return "⚠️ Market Data Unavailable"
        
        close_prices = df['Close']
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        if current_rsi < 35:
            return f"🟢 UP (CALL) - RSI is Low ({current_rsi:.2f})"
        elif current_rsi > 65:
            return f"🔴 DOWN (PUT) - RSI is High ({current_rsi:.2f})"
        else:
            ma = close_prices.rolling(window=10).mean().iloc[-1]
            current_price = close_prices.iloc[-1]
            if current_price > ma:
                return f"🟢 UP (CALL) - Bullish Trend"
            else:
                return f"🔴 DOWN (PUT) - Bearish Trend"
    except Exception as e:
        return "⚠️ Analysis Error"

async def start(update, context):
    keyboard = [[InlineKeyboardButton("🔍 Analyze EUR/USD", callback_data='analyze')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('🤖 QX Live Signal Bot Ready!', reply_markup=reply_markup)

async def button_click(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'analyze':
        decision = generate_signal()
        keyboard = [[InlineKeyboardButton("🔍 Analyze Again", callback_data='analyze')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"📊 **Market Analysis Result**\n✨ Recommendation: **{decision}**", reply_markup=reply_markup, parse_mode="Markdown")

def main():
    # ব্যাকগ্রাউন্ডে ওয়েব সার্ভার চালু করা
    threading.Thread(target=run_web_server, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    print("🚀 QX Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
