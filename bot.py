import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("API_KEY")

HEADERS = {"x-apisports-key": API_KEY}
BARCA_ID = 529
SEASON = 2024

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот про ФК Барселона!\n\n"
        "📋 /squad — состав команды\n"
        "📅 /next — следующий матч\n"
        "⚽ /live — текстовая трансляция"
    )

async def squad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Загружаю состав...")
    url = f"https://v3.football.api-sports.io/players/squads?team={BARCA_ID}"
    res = requests.get(url, headers=HEADERS).json()
    players = res["response"][0]["players"]
    positions = {"Goalkeeper": "🧤 Вратари", "Defender": "🛡 Защитники",
                 "Midfielder": "⚙️ Полузащитники", "Attacker": "⚡️ Нападающие"}
    grouped = {}
    for p in players:
        pos = p["position"]
        grouped.setdefault(pos, []).append(p["name"])
    text = "🔵🔴 Состав ФК Барселона:\n\n"
    for pos, title in positions.items():
        if pos in grouped:
            text += f"\n{title}:\n"
            for name in grouped[pos]:
                text += f"  • {name}\n"
    await update.message.reply_text(text)

async def next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Ищу следующий матч...")
    url = f"https://v3.football.api-sports.io/fixtures?team={BARCA_ID}&next=1"
    res = requests.get(url, headers=HEADERS).json()
    if not res["response"]:
        await update.message.reply_text("Матчей не найдено")
        return
    match = res["response"][0]
    home = match["teams"]["home"]["name"]
    away = match["teams"]["away"]["name"]
    date = match["fixture"]["date"][:10]
    time = match["fixture"]["date"][11:16]
    league = match["league"]["name"]
    text = (f"📅 Следующий матч:\n\n"
            f"🏆 {league}\n"
            f"⚽ {home} vs {away}\n"
            f"📆 {date} в {time} UTC")
    await update.message.reply_text(text)

async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Проверяю живые матчи...")
    url = f"https://v3.football.api-sports.io/fixtures?team={BARCA_ID}&live=all"
    res = requests.get(url, headers=HEADERS).json()
    if not res["response"]:
        await update.message.reply_text("🔴 Барселона сейчас не играет")
        return
    match = res["response"][0]
    home = match["teams"]["home"]["name"]
    away = match["teams"]["away"]["name"]
    home_score = match["goals"]["home"]
    away_score = match["goals"]["away"]
    minute = match["fixture"]["status"]["elapsed"]
    text = (f"🔴 LIVE!\n\n"
            f"⚽ {home} {home_score} - {away_score} {away}\n"
            f"⏱ {minute} минута")
    await update.message.reply_text(text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("squad", squad))
    app.add_handler(CommandHandler("next", next_match))
    app.add_handler(CommandHandler("live", live))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
