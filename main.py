import telebot
import sqlite3
import random
import time

TOKEN = 'ваш токен'
bot = telebot.TeleBot(TOKEN)

def init_db():
    with sqlite3.connect('lottery.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS participants (name TEXT)')

@bot.message_handler(commands=['start'])
def start(message):
    msg = ("🏆 **Бот-Распределитель мест**\n\n"
           "📍 **Как управлять списком:**\n"
           "1. Отправь список имен (каждое с новой строки) — *заменит весь список*.\n"
           "2. `/add Фамилия` — добавить одного человека к текущим.\n"
           "3. `/clear` — полностью очистить список.\n"
           "4. `/list` — посмотреть, кто уже записан.\n\n"
           "🎰 **/lottery** — распределить всех по местам!")
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

@bot.message_handler(commands=['add'])
def add_name(message):
    name = message.text.replace('/add', '').strip()
    if not name:
        bot.reply_to(message, "Пример: `/add Иванов`", parse_mode='Markdown')
        return
    
    with sqlite3.connect('lottery.db') as conn:
        count = conn.execute("SELECT count(*) FROM participants").fetchone()[0]
        if count >= 30:
            bot.send_message(message.chat.id, "❌ Лимит 30 человек исчерпан!")
            return
        conn.execute("INSERT INTO participants VALUES (?)", (name,))
    bot.send_message(message.chat.id, f"✅ {name} добавлен в список.")

@bot.message_handler(commands=['clear'])
def clear_list(message):
    with sqlite3.connect('lottery.db') as conn:
        conn.execute("DELETE FROM participants")
    bot.send_message(message.chat.id, "🗑 Список полностью очищен.")

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
        bot.send_message(message.chat.id, "❌ В списке никого нет!")
        return

    names = [row[0] for row in res]
    random.shuffle(names) # Перемешиваем весь список
    
    msg = bot.send_message(message.chat.id, "🎲 Идет распределение мест...")
    time.sleep(1.5)
    
    result = "🏆 **Итоги розыгрыша:**\n\n"
    for i, name in enumerate(names):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🔹"
        result += f"{medal} {i+1} место — *{name}*\n"
    
    bot.edit_message_text(result, message.chat.id, msg.message_id, parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def overwrite_list(message):
    new_names = [n.strip() for n in message.text.split('\n') if n.strip()]
    if len(new_names) > 30:
        bot.send_message(message.chat.id, "⚠️ Максимум 30 человек!")
    else:
        with sqlite3.connect('lottery.db') as conn:
            conn.execute("DELETE FROM participants")
            conn.executemany("INSERT INTO participants VALUES (?)", [(n,) for n in new_names])
        bot.send_message(message.chat.id, f"✅ Список перезаписан! Всего: {len(new_names)}")

if __name__ == '__main__':
    init_db()
    bot.infinity_polling()
