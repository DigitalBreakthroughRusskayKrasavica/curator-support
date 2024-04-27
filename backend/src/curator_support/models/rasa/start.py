import subprocess

import rasa

from data_parser import excel_transfer
from rasa_config import pipe

# ======
# тут советую подключить бд
# ======

#  RASA configs generating
# ========================

# Xlsx table generating
input_file_questions = 'train_data.csv'
input_file_answers = 'answer_class.csv'
output_file = 'data.xlsx'
excel_transfer(
    path_to_question_csv=input_file_questions,
    path_to_answer_csv=input_file_answers,
    output_file=output_file
)  # you can use default params

# Final configs generating
dataset_name = ""
pipe(
    dataset_name=dataset_name,
    input_file=output_file,
    use_subintents='single'
)

# ========================


# RASA training
model_name = 'model.tar.gz'
rasa.train(
    config='rasa_data/config.yml',
    domain='rasa_data/domain.yml',
    training_files=['rasa_data/' + file for file in ['nlu.yml', 'responses.yml', 'rules.yml']],
    fixed_model_name=model_name,
)

# RASA starting
# rasa.run(тут какие-то аргументы говна - руки оборвать людям, кто расу писал)
subprocess.Popen(f'venv/scripts/rasa.exe run -p 6060 -i 127.0.0.1 --enable-api -m ./models/{model_name}')
#

# ЗДЕСЬ ДАЛЬШЕ МОЖНО ЗАПУСКАТЬ ЮЗЕР ИНТЕРФЕЙСЫ - пример bot.py
# print('Bot starting')
# print('DONE')
