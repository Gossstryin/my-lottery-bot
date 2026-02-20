import telebot
import sqlite3
import random
import time

TOKEN = 'ваш токен тгбота'
bot = telebot.TeleBot(TOKEN)

def init_db():
    with sqlite3.connect('lottery.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS participants (name TEXT)')

@bot.message_handler(commands=['start'])
def start(message):
    msg = ("🏆 **Бот-Лотерея (v2.0)**\n\n"
           "📍 **Команды управления:**\n"
           "🔹 `/add Имя` — добавить одного человека\n"
           "🔹 `/del Имя` — удалить одного человека\n"
           "🔹 `/setlist` — заменить весь список (отправьте список следующим сообщением)\n"
           "🔹 `/clear` — очистить всё\n"
           "🔹 `/list` — кто в списке\n\n"
           "🎰 **/lottery** — распределить места!")
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

@bot.message_handler(commands=['add'])
def add_name(message):
    name = message.text.replace('/add', '').strip()
    if not name:
        bot.reply_to(message, "❌ Напишите имя после команды. Пример: `/add Иванов`", parse_mode='Markdown')
        return

    with sqlite3.connect('lottery.db') as conn:
        count = conn.execute("SELECT count(*) FROM participants").fetchone()[0]
        if count >= 30:
            bot.send_message(message.chat.id, "🚫 Лимит 30 человек!")
            return
        conn.execute("INSERT INTO participants VALUES (?)", (name,))
    bot.send_message(message.chat.id, f"✅ *{name}* добавлен.", parse_mode='Markdown')

@bot.message_handler(commands=['del'])
def delete_name(message):
    name = message.text.replace('/del', '').strip()
    if not name:
        bot.reply_to(message, "❌ Пример: `/del Иванов`", parse_mode='Markdown')
        return

    with sqlite3.connect('lottery.db') as conn:
        exists = conn.execute("SELECT name FROM participants WHERE name = ?", (name,)).fetchone()
        if exists:
            conn.execute("DELETE FROM participants WHERE name = ?", (name,))
            bot.send_message(message.chat.id, f"🗑 *{name}* удален из списка.", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "❓ Такого имени нет в списке (проверьте регистр).")

@bot.message_handler(commands=['setlist'])
def ask_for_list(message):
    sent = bot.send_message(message.chat.id, "📝 Отправьте новый список фамилий (каждая с новой строки):")
    bot.register_next_step_handler(sent, process_full_list)

def process_full_list(message):
    new_names = [n.strip() for n in message.text.split('\n') if n.strip()]
    if len(new_names) > 30:
        bot.send_message(message.chat.id, "⚠️ Ошибка: максимум 30 человек!")
    else:
        with sqlite3.connect('lottery.db') as conn:
            conn.execute("DELETE FROM participants")
            conn.executemany("INSERT INTO participants VALUES (?)", [(n,) for n in new_names])
        bot.send_message(message.chat.id, f"✅ Весь список обновлен! Всего: {len(new_names)} чел.")

@bot.message_handler(commands=['list'])
def list_names(message):
    with sqlite3.connect('lottery.db') as conn:
        res = conn.execute("SELECT name FROM participants").fetchall()
    if not res:
        bot.send_message(message.chat.id, "📭 Список пуст.")
    else:
        output = "\n".join([f"{i+1}. {row[0]}" for i, row in enumerate(res)])
        bot.send_message(message.chat.id, f"📋 **Участники ({len(res)}/30):**\n\n{output}", parse_mode='Markdown')

@bot.message_handler(commands=['lottery'])
def run_lottery(message):
    with sqlite3.connect('lottery.db') as conn:
        res = conn.execute("SELECT name FROM participants").fetchall()

    if not res:
        bot.send_message(message.chat.id, "❌ Список пуст!")
        return

    names = [row[0] for row in res]
    random.shuffle(names)

    msg = bot.send_message(message.chat.id, "🎲 Распределяю места...")
    time.sleep(1.2)

    result = "🏆 **Итоги лотереи:**\n\n"
    for i, name in enumerate(names):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🔹"
        result += f"{medal} {i+1} место — *{name}*\n"

    bot.edit_message_text(result, message.chat.id, msg.message_id, parse_mode='Markdown')

@bot.message_handler(commands=['clear'])
def clear_list(message):
    with sqlite3.connect('lottery.db') as conn:
        conn.execute("DELETE FROM participants")
    bot.send_message(message.chat.id, "🗑 Список очищен.")


if __name__ == '__main__':
    init_db()
    bot.infinity_polling()
