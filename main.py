import telebot
import sqlite3
import random
import time

# Вставьте ваш токен от @BotFather здесь
TOKEN = '8503437627:AAEXDI8f4eJJJZJYFslQUTz580oajOe2kOU'
bot = telebot.TeleBot(TOKEN)


# Настройка базы данных
def init_db():
    with sqlite3.connect('lottery.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS participants (name TEXT)')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "👋 Привет! Я бот для лотереи.\n\n"
                     "1️⃣ Пришли список фамилий (каждая с новой строки, до 30 человек).\n"
                     "2️⃣ /list — посмотреть список.\n"
                     "3️⃣ /lottery — выбрать победителя!")


@bot.message_handler(commands=['list'])
def list_names(message):
    with sqlite3.connect('lottery.db') as conn:
        res = conn.execute("SELECT name FROM participants").fetchall()

    if not res:
        bot.send_message(message.chat.id, "📭 Список пуст. Просто пришли фамилии текстом.")
    else:
        # Извлекаем фамилии из кортежей БД
        names = [row[0] for row in res]
        output = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(names)])
        bot.send_message(message.chat.id, f"📋 **Текущий список:**\n\n{output}", parse_mode='Markdown')


@bot.message_handler(commands=['lottery'])
def run_lottery(message):
    with sqlite3.connect('lottery.db') as conn:
        res = conn.execute("SELECT name FROM participants").fetchall()

    if not res:
        bot.send_message(message.chat.id, "❌ Ошибка: список пуст!")
        return

    names = [row[0] for row in res]
    winner = random.choice(names)

    msg = bot.send_message(message.chat.id, "🎰 Розыгрыш пошел...")
    time.sleep(1)
    bot.edit_message_text(f"🎰 Результат лотереи:\n\n🎉 Победитель: **{winner}** 🎉",
                          message.chat.id, msg.message_id, parse_mode='Markdown')


@bot.message_handler(func=lambda m: True)
def update_list(message):
    # Если это не команда, записываем как фамилии
    raw_names = [n.strip() for n in message.text.split('\n') if n.strip()]

    if len(raw_names) > 30:
        bot.send_message(message.chat.id, "⚠️ Ошибка: максимум 30 человек!")
    elif len(raw_names) > 0:
        with sqlite3.connect('lottery.db') as conn:
            conn.execute("DELETE FROM participants")
            conn.executemany("INSERT INTO participants VALUES (?)", [(n,) for n in raw_names])
        bot.send_message(message.chat.id, f"✅ Список обновлен! Добавлено: {len(raw_names)} чел.")


if __name__ == '__main__':
    init_db()
    print("Бот запущен через Telebot!")
    bot.infinity_polling()
