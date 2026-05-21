#!/usr/bin/env python3
"""
EL FER3OON - AI Market Analytics Platform Bot
"""

import os
import asyncio
import threading
from datetime import datetime
from flask import Flask
import psycopg2
import psycopg2.extras
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# ===== Flask Uptime Server =====
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "EL FER3OON Analytics Platform is running! 👑"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# ===== Configuration =====
BOT_TOKEN    = os.environ.get("BOT_TOKEN")
CHANNEL_LINK = "https://t.me/+wm-XT1rWsHhkNjJk"
ADMIN_ID     = 8136877112
DATABASE_URL = os.environ.get("DATABASE_URL")

# ===== Database =====
def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id BIGINT PRIMARY KEY,
                joined TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database initialized")
    except Exception as e:
        print(f"Error init_db: {e}")

def db_get_user(chat_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT chat_id FROM users WHERE chat_id = %s", (chat_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except Exception as e:
        print(f"Error db_get_user: {e}")
        return None

def db_add_user(chat_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (chat_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (chat_id,)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error db_add_user: {e}")

def db_get_all_users():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT chat_id FROM users")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"chat_id": r[0]} for r in rows]
    except Exception as e:
        print(f"Error db_get_all_users: {e}")
        return []

def db_count_users():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except Exception as e:
        print(f"Error db_count_users: {e}")
        return 0

# ===== Keyboards =====
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Market Overview", callback_data="market_overview"),
            InlineKeyboardButton("🤖 AI Analytics",    callback_data="ai_analytics")
        ],
        [
            InlineKeyboardButton("⚡ Live Updates",    callback_data="live_updates"),
            InlineKeyboardButton("🛠 Smart Tools",     callback_data="smart_tools")
        ],
        [
            InlineKeyboardButton("📚 Platform Info",  callback_data="platform_info")
        ],
        [
            InlineKeyboardButton("🚀 Open Platform",  url=CHANNEL_LINK)
        ]
    ])

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]
    ])

# ===== Message Texts =====
WELCOME_MSG = """👑 *Welcome to EL FER3OON*

Your AI-powered market analytics and smart monitoring platform.

Access real-time market insights, advanced analytics tools, and intelligent tracking systems — all in one place.

_Choose an option below to get started:_"""

MARKET_OVERVIEW_MSG = """📊 *Market Overview*

Current market activity:

• Volatility: Moderate
• Trend Strength: Bullish
• Market Sentiment: Stable
• Session Status: Active

_Analytics are updated continuously._"""

AI_ANALYTICS_MSG = """🤖 *AI Analytics Monitor*

Our AI systems continuously track:

• Trend Momentum
• Price Movement Patterns
• Market Behavior Analysis
• Volume Activity
• Real-Time Sentiment Tracking

_Advanced monitoring systems are active._"""

LIVE_UPDATES_MSG = """⚡ *Live Updates*

Our live feed provides:

• Market Movement Tracking
• Session Notifications
• Trend Change Alerts
• Real-Time Monitoring

_Updates are refreshed automatically._"""

SMART_TOOLS_MSG = """🛠 *Smart Tools*

Available platform tools:

• 🔍 Market Scanner
• 📈 Trend Analysis
• 🕐 Session Monitoring
• 🔔 Smart Notifications
• 📉 Momentum Tracking
• ⚙️ Signal Filtering

_All tools are powered by AI._"""

PLATFORM_INFO_MSG = """📚 *About EL FER3OON*

EL FER3OON is a smart analytics platform designed to provide advanced market monitoring tools and AI-powered insights.

Our platform offers:
• Professional-grade analytics
• Real-time market intelligence
• Smart automated monitoring
• Clean and intuitive interface

_Powered by Data. Driven by AI._"""

# ===== Handlers =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    try:
        if not db_get_user(chat_id):
            db_add_user(chat_id)
    except Exception as e:
        print(f"Error saving user: {e}")
    await update.message.reply_text(
        WELCOME_MSG,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Help & Commands*\n\n"
        "/start — Launch the platform\n"
        "/help — Show this help menu\n"
        "/about — About EL FER3OON\n\n"
        "_Use the interactive menu to access all platform features._",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 *EL FER3OON*\n\n"
        "An AI-powered market analytics and smart monitoring platform.\n\n"
        "_Powered by Data. Driven by AI._",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    responses = {
        "market_overview": MARKET_OVERVIEW_MSG,
        "ai_analytics":    AI_ANALYTICS_MSG,
        "live_updates":    LIVE_UPDATES_MSG,
        "smart_tools":     SMART_TOOLS_MSG,
        "platform_info":   PLATFORM_INFO_MSG,
    }

    if data == "back_menu":
        await query.edit_message_text(
            WELCOME_MSG,
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    elif data in responses:
        await query.edit_message_text(
            responses[data],
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )

# ===== Admin Commands =====

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Not allowed")
        return

    users = db_get_all_users()
    if not users:
        await update.message.reply_text("❌ No users found")
        return

    msg = update.message
    success = 0
    failed = 0

    await update.message.reply_text(f"📤 Sending to {len(users)} users...")

    for user in users:
        uid = user["chat_id"]
        try:
            if msg.reply_to_message:
                rep = msg.reply_to_message
                if rep.text:
                    await context.bot.send_message(chat_id=uid, text=rep.text)
                elif rep.photo:
                    await context.bot.send_photo(chat_id=uid, photo=rep.photo[-1].file_id, caption=rep.caption or "")
                elif rep.video:
                    await context.bot.send_video(chat_id=uid, video=rep.video.file_id, caption=rep.caption or "")
            elif context.args:
                text = " ".join(context.args)
                await context.bot.send_message(chat_id=uid, text=text)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await update.message.reply_text(f"✅ Done!\nSuccess: {success}\nFailed: {failed}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    count = db_count_users()
    await update.message.reply_text(f"📊 Bot Statistics:\n👥 Total Users: {count}")

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if update.message.video:
        await update.message.reply_text(f"VIDEO_ID:\n`{update.message.video.file_id}`", parse_mode="Markdown")
    elif update.message.photo:
        await update.message.reply_text(f"PHOTO_ID:\n`{update.message.photo[-1].file_id}`", parse_mode="Markdown")

# ===== Main =====

def main():
    init_db()

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("help",      help_command))
    app.add_handler(CommandHandler("about",     about_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("stats",     stats_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.VIDEO | filters.PHOTO, get_file_id))

    print("✅ EL FER3OON Analytics Platform is running! 👑")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
