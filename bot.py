import os
from telegram import Update, ChatPermissions
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

TOKEN = os.getenv("BOT_TOKEN")
warnings = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("AsilAdminBot aktif! 👑")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/rules - Grup kuralları\n"
        "/admins - Yöneticileri göster\n"
        "/info - Üye bilgisi\n"
        "/ban - Üyeyi yasakla (yanıtla)\n"
        "/kick - Üyeyi çıkar (yanıtla)\n"
        "/mute - Üyeyi sustur (yanıtla)\n"
        "/unmute - Susturmayı kaldır (yanıtla)\n"
        "/warn - Uyarı ver (yanıtla)"
    )

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Grup kurallarına uyun. Saygılı olun. 👑")

async def is_admin(update, context):
    user = update.effective_user
    member = await context.bot.get_chat_member(
        update.effective_chat.id, user.id
    )
    return member.status in ("administrator", "creator")

async def ban(update, context):
    if not await is_admin(update, context):
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text("Üye yasaklandı.")

async def kick(update, context):
    if not await is_admin(update, context):
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await context.bot.unban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text("Üye gruptan çıkarıldı.")

async def mute(update, context):
    if not await is_admin(update, context):
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.restrict_chat_member(
            update.effective_chat.id, user.id,
            ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text("Üye susturuldu.")

async def unmute(update, context):
    if not await is_admin(update, context):
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.restrict_chat_member(
            update.effective_chat.id, user.id,
            ChatPermissions(can_send_messages=True,
                            can_send_photos=True,
                            can_send_videos=True,
                            can_send_audios=True)
        )
        await update.message.reply_text("Üyenin susturması kaldırıldı.")

async def warn(update, context):
    if not await is_admin(update, context):
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        key = (update.effective_chat.id, user.id)
        warnings[key] = warnings.get(key, 0) + 1
        await update.message.reply_text(
            f"{user.first_name} uyarıldı. Uyarı sayısı: {warnings[key]}"
        )

async def info(update, context):
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    await update.message.reply_text(
        f"Ad: {user.full_name}\nID: {user.id}"
    )

async def admins(update, context):
    members = await context.bot.get_chat_administrators(update.effective_chat.id)
    names = "\n".join(m.user.full_name for m in members)
    await update.message.reply_text("Grup yöneticileri:\n" + names)

async def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN ayarlanmamış!")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("admins", admins))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.wait()
    await app.stop()
    await app.shutdown()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
  
