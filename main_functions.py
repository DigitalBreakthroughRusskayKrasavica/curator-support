import csv
import requests

url = 'http://127.0.0.1:6060/model/parse'
confidence_limit = 0.3  # уверенность, ниже которой скипаем вопрос

# ЭТУ ЧАСТЬ УБРАТЬ ПРИ ПОДКЛЮЧЕНИИ БД
# ===================================
answers = {}
with open('answer_class.csv', encoding='utf-8', newline='') as answers_file:
    answers_reader = csv.DictReader(answers_file)
    for row in answers_reader:
        answers[row['answer_class']] = row['Answer']
# ===================================


def get_answer(question: str):
    r = requests.post(
        url,
        json={
            'text': question
        }
    )
    if r.status_code != 200:
        return 'Произошла ошибка'
    # ЗАМЕНИТЬ НА ПОИСК ЗНАЧЕНИЯ В БД
    if r.json()['intent']['confidence'] < confidence_limit:
        return "Не получилось найти ответ - свяжитесь с куратором"
    return f"{answers[r.json()['intent']['name'].split('_')[-1]]}\n\n{r.json()['intent']['confidence']}"

