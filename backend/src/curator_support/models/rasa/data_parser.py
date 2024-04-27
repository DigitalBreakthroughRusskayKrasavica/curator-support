import pandas as pd
import csv


def excel_transfer(
        path_to_question_csv='train_data.csv',
        path_to_answer_csv='answer_class.csv',
        output_file='data/data.xlsx'
):

    table = {'questions_merged': [], 'answer_summary': [], 'intent': [], 'answers_merged': []}
    answers_questions = {}
    intents = {}

    with open(path_to_question_csv, encoding='utf-8', newline='') as questions_file:
        questions_reader = csv.DictReader(questions_file)
        for row in questions_reader:
            if row['answer_class'] not in answers_questions:
                answers_questions[row['answer_class']] = []
            answers_questions[row['answer_class']].append(row['Question'])
            if row['answer_class'] not in intents:
                intents[row['answer_class']] = row['Category'] + '_' + row['answer_class']

    with open(path_to_answer_csv, encoding='utf-8', newline='') as answers_file:
        answers_reader = csv.DictReader(answers_file)
        for row in answers_reader:
            table['answer_summary'].append(row['Answer'])
            table['questions_merged'].append(str(answers_questions[row['answer_class']]))
            table['intent'].append(intents[row['answer_class']])
            table['answers_merged'].append([row['Answer']])

    df = pd.DataFrame(table)
    df.to_excel(output_file)
