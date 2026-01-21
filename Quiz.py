from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
import random
import asyncio

TOKEN = "7793304676:AAH29ViZ0-W1TxoqKL8DJQ3y7ol-QUU93ng"

users = {}

TEXT = {
    "welcome": "🎓 Quiz Platformasına Xosh Keldińiz!",
    "send_test": (
        "Test tekstin tómenge jiberiń\n"
        "(++++ hám ==== formatında):"
    ),
    "no_test": "Aldın test tekstin kiritiń!",
    "correct": "✅ Durıs!",
    "wrong": "❌ Qáte!\n✅ Durıs juwap:",
    "result": "📊 {c} / {t}\n📈 {p}%",
    "fail": "OQÍW KEREK EDI😵‍💫😵‍💫😵‍💫",
    "good": "Jaqsı nátiyje! Tolıq tıyryshıń!",
    "excellent": "En zor nátiyje! Siz shebersiz!"
}

def parse_test(text):
    blocks = [b.strip() for b in text.split("++++") if b.strip()]
    questions = []

    for block in blocks:
        parts = [p.strip() for p in block.split("====") if p.strip()]
        if len(parts) < 2:
            continue

        q_text = parts[0]
        options = []
        correct = None

        for i, opt in enumerate(parts[1:]):
            if opt.startswith("#"):
                correct = i
                options.append(opt[1:].strip())
            else:
                options.append(opt)

        if correct is not None:
            questions.append({
                "q": q_text,
                "opts": options,
                "correct": correct
            })

    return questions


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id] = {
        "qs": [],
        "i": 0,
        "ok": 0
    }

    await update.message.reply_text(
        f"{TEXT['welcome']}\n\n{TEXT['send_test']}"
    )


async def receive_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    qs = parse_test(update.message.text)

    if not qs:
        await update.message.reply_text(TEXT["no_test"])
        return

    random.shuffle(qs)
    users[uid]["qs"] = qs
    users[uid]["i"] = 0
    users[uid]["ok"] = 0

    await send_question(context, uid)


async def send_question(context, uid):
    data = users[uid]
    i = data["i"]

    if i >= len(data["qs"]):
        return await finish(context, uid)

    q = data["qs"][i]

    kb = [
        [InlineKeyboardButton(opt, callback_data=str(n))]
        for n, opt in enumerate(q["opts"])
    ]

    await context.bot.send_message(
        chat_id=uid,
        text=f"{i+1}. {q['q']}",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    data = users[uid]
    q = data["qs"][data["i"]]

    choice = int(query.data)

    if choice == q["correct"]:
        data["ok"] += 1
        await query.edit_message_text(TEXT["correct"])
    else:
        await query.edit_message_text(
            f"{TEXT['wrong']} {q['opts'][q['correct']]}"
        )

    data["i"] += 1
    await asyncio.sleep(1)
    await send_question(context, uid)


async def finish(context, uid):
    data = users[uid]
    t = len(data["qs"])
    c = data["ok"]
    p = round((c / t) * 100)

    if p >= 90:
        emoji = "👑"
        title = TEXT["excellent"]
    elif p >= 70:
        emoji = "🥈"
        title = TEXT["good"]
    else:
        emoji = "😵‍💫"
        title = TEXT["fail"]

    await context.bot.send_message(
        chat_id=uid,
        text=f"{emoji} {title}\n\n" +
             TEXT["result"].format(c=c, t=t, p=p)
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_test))
    app.add_handler(CallbackQueryHandler(answer))
    app.run_polling()


if __name__ == "__main__":
    main()
