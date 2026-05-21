import telebot
from telebot import types
from environs import Env
from helpers_functions import get_question_and_question_number
from helpers_functions import get_quiz_questions
from helpers_functions import connect_to_redis_db
from helpers_functions import get_answer


def run_bot(bot, redis_db, quiz_questions, messenger_article):
    @bot.message_handler(commands=["start","help"])
    def handle_start(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Новый вопрос")
        btn2 = types.KeyboardButton("Сдаться")
        markup.add(btn1, btn2)
        bot.send_message(
            message.chat.id,
            "Привет! Я бот для викторин",
            reply_markup=markup
        )
    
    
    @bot.message_handler(func=lambda message: message.text == "Новый вопрос")
    def handle_new_question_request(message):
        question, question_number = get_question_and_question_number(quiz_questions)
        redis_db.set(f"{messenger_article}{message.from_user.id}", question_number)
        bot.send_message(message.chat.id, question)
    
    
    @bot.message_handler(func=lambda message: message.text == "Сдаться")
    def handle_get_answer_and_new_question_request(message):
        answer = get_answer(message.from_user.id, redis_db, quiz_questions, messenger_article)
        bot.send_message(message.chat.id, f"Правильный ответ: {answer}")
        question, question_number = get_question_and_question_number(quiz_questions)
        redis_db.set(f"{messenger_article}{message.from_user.id}", question_number)
        bot.send_message(message.chat.id, question)
    
           
    @bot.message_handler(func=lambda message: True)
    def handle_solution_attempt(message):
        answer = get_answer(message.from_user.id, redis_db, quiz_questions, messenger_article)
        if answer == message.text:
            bot.send_message(
                message.chat.id,
                "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
            )
        else:
            bot.send_message(message.chat.id, "Неправильно… Попробуешь ещё раз?")
    
    bot.infinity_polling()


def main():
    env = Env()
    env.read_env()
    messenger_article = "tg-"
    path_to_questons_file = env.str("PATH_TO_QUESTIONS_FILE")
    db_name = env.str("REDIS_DB")
    db_port = env.str("REDIS_DB_PORT")
    db_password = env.str("REDIS_DB_PASSWORD")
    tg_bot_token = env.str("TELEGRAM_BOT_API_KEY")
    quiz_questions = get_quiz_questions(path_to_questons_file)
    redis_db = connect_to_redis_db(db_name, db_port, db_password)
    bot = telebot.TeleBot(tg_bot_token)
    run_bot(bot, redis_db, quiz_questions, messenger_article)


if __name__ == "__main__":
    main()
