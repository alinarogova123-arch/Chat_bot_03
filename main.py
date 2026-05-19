import pprint

import telebot
from environs import Env


# with open("quiz-questions/1vs1200.txt", "r", encoding="KOI8-R") as my_file:
#   file_contents = my_file.read()


# paragraphs = file_contents.split('\n\n')


# quiz_questions = {}

# for i, paragraph in enumerate(paragraphs, 1):
#     if "Вопрос" in paragraph:
#         quiz_questions[f"question_{i}"] = {
#             "question": paragraph.split(':')[1].strip(),
#             "answer": paragraphs[i].split(':')[1].strip()
#         }

# pprint.pprint(quiz_questions)


env = Env()
env.read_env()
tg_bot_token = env.str("TELEGRAM_BOT_API_KEY")
bot = telebot.TeleBot(tg_bot_token)

@bot.message_handler(commands=["start","help"])
def handle_start(message):
    bot.send_message(message.chat.id, "Здравствуйте")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_message(message.chat.id, message.text)

bot.infinity_polling()