import random

import redis


def get_question_and_question_number(quiz_questions):
    question_number = str(random.randint(1,len(quiz_questions)))
    question_and_answer = quiz_questions.get(question_number)
    question = question_and_answer.get("question")

    return question, question_number


def get_answer(user_id, redis_db, quiz_questions, messenger_article):
    question_number = redis_db.get(f"{messenger_article}{user_id}")
    question_and_answer = quiz_questions.get(question_number)
    if question_and_answer:
        answer = question_and_answer.get("answer").split(".")[0]

    return answer


def get_quiz_questions(path_to_questons_file):
    with open(path_to_questons_file, "r", encoding="KOI8-R") as my_file:
        file_contents = my_file.read()
    paragraphs = file_contents.split("\n\n")
    quiz_questions = {}
    question_number = 1
    for i, paragraph in enumerate(paragraphs, 1):
        if "Вопрос" in paragraph:
            quiz_questions[str(question_number)] = {
                "question": paragraph.split(":")[1].strip(),
                "answer": paragraphs[i].split(":")[1].strip()
            }
            question_number += 1
    return quiz_questions


def connect_to_redis_db(db_name, db_port, db_password):
    redis_db = redis.Redis(
        host=db_name, 
        port=db_port,
        username="default",
        password=db_password,
        decode_responses=True
    )
    return redis_db