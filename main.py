from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
)
import os

TOKEN = "توکن_جدید_ربات_را_اینجا_بگذار"
CHANNEL = "@todaywaslike"

pending = {}

async def check_member(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not await check_member(context.bot, user.id):
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL.replace('@','')}")],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check")]
        ]
        await update.message.reply_text(
            "برای استفاده از ربات ابتدا در کانال عضو شو.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if context.args:
        target = int(context.args[0])
        pending[user.id] = target
        await update.message.reply_text(
            "📩 حالا پیام، عکس، ویدیو، ویس یا فایل خودت را بفرست تا ناشناس ارسال شود."
        )
    else:
        link = f"https://t.me/{context.bot.username}?start={user.id}"
        await update.message.reply_text(
            f"👋 سلام {user.first_name}!\\n\\n"
            f"🔗 لینک ناشناس تو:\\n{link}\\n\\n"
            f"این لینک را برای دوستات بفرست تا ناشناس برات پیام بفرستن."
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if await check_member(context.bot, user.id):
        link = f"https://t.me/{context.bot.username}?start={user.id}"
        await query.message.reply_text(f"✅ عضویت تایید شد!\\n\\n🔗 لینک تو:\\n{link}")
    else:
        await query.message.reply_text("❌ هنوز عضو کانال نیستی.")

async def anonymous(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user.id

    if sender not in pending:
        return

    target = pending[sender]

    try:
        if update.message.text and not update.message.text.startswith("/"):
            await context.bot.send_message(target, f"📩 پیام ناشناس:\\n\\n{update.message.text}")

        elif update.message.photo:
            await context.bot.send_photo(target, update.message.photo[-1].file_id, caption="📷 عکس ناشناس")

        elif update.message.video:
            await context.bot.send_video(target, update.message.video.file_id, caption="🎬 ویدیوی ناشناس")

        elif update.message.voice:
            await context.bot.send_voice(target, update.message.voice.file_id, caption="🎤 ویس ناشناس")

        elif update.message.document:
            await context.bot.send_document(target, update.message.document.file_id, caption="📎 فایل ناشناس")

        elif update.message.sticker:
            await context.bot.send_sticker(target, update.message.sticker.file_id)
            await context.bot.send_message(target, "😄 استیکر ناشناس")

        await update.message.reply_text("✅ با موفقیت ناشناس ارسال شد.")
        del pending[sender]

    except Exception as e:
        await update.message.reply_text("❌ خطا در ارسال.")
        print(e)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.ALL, anonymous))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
