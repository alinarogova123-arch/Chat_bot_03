import random

from environs import Env
from helpers_functions import get_question_and_question_number
from helpers_functions import get_answer
from helpers_functions import get_quiz_questions
from helpers_functions import connect_to_redis_db
import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType


def send_message(vk_api, event, keyboard, message):
    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1,1000)
    )


def run_bot(longpoll, redis_db, quiz_questions, vk_api, messenger_article):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Новый вопрос")
    keyboard.add_button("Сдаться")
    for event in longpoll.listen():
        if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
            continue

        if event.text.lower() == 'начать':
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button("Новый вопрос")
            keyboard.add_button("Сдаться")
            send_message(vk_api, event, keyboard, "Привет! Я бот для викторин")

        elif event.text == "Новый вопрос":
            question, question_number = get_question_and_question_number(quiz_questions)
            redis_db.set(f"{messenger_article}{event.user_id}", question_number)
            send_message(vk_api, event, keyboard, question)

        elif event.text == "Сдаться":
            answer = get_answer(event.user_id, redis_db, quiz_questions, messenger_article)
            send_message(vk_api, event, keyboard, f"Правильный ответ: {answer}")           
            question, question_number = get_question_and_question_number(quiz_questions)
            redis_db.set(f"{messenger_article}{event.user_id}", question_number)
            send_message(vk_api, event, keyboard, question)

        else:
            answer = get_answer(event.user_id, redis_db, quiz_questions, messenger_article)
            if answer == event.text:
                send_message(
                    vk_api,
                    event,
                    keyboard,
                    "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
                )
            else:
                send_message(vk_api, event, keyboard, "Неправильно… Попробуешь ещё раз?")


def main():
    env = Env()
    env.read_env()
    messenger_article = "vk-"
    db_name = env.str("REDIS_DB")
    db_port = env.str("REDIS_DB_PORT")
    db_password = env.str("REDIS_DB_PASSWORD")
    vk_bot_token = env.str("VK_API_KEY")
    vk_session = vk.VkApi(token=vk_bot_token)
    vk_api = vk_session.get_api()
    quiz_questions = get_quiz_questions()
    redis_db = connect_to_redis_db(db_name, db_port, db_password)
    longpoll = VkLongPoll(vk_session)
    run_bot(longpoll, redis_db, quiz_questions, vk_api, messenger_article)


if __name__ == "__main__":
    main()
