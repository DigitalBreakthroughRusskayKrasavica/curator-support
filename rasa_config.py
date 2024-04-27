"""
Скрипт для генерации конфигов в RASA

WORKING_DIR - рабочая директория, которая содержит папки
    data: для входных данных
    output: для сгенерированных по каждому датасету конфигураций
"""

from typing import List, Text, Optional
from pathlib import Path
import pandas as pd
import json
import rasa
import warnings
# from generate_actions_for_multibot import generate_actions
from itertools import chain

warnings.filterwarnings('ignore')

TAB_SYMBOL = ' ' * 2
WORKING_DIR = Path('')
OUTPUT_DIR = WORKING_DIR.joinpath('output')
DIET_EPOCHS = 250


class RasaDataGenerator:
    """
    Вход: xlsx файл вида

    intent: str | questions: list | answers: list
    """

    def __init__(
            self,
            output_dir=OUTPUT_DIR) -> None:

        """

        """
        self.output_dir = output_dir

    def generate_endpoints_file(self,
                                url,
                                output_dir: Path,
                                output_filename: Text = 'endpoints.yml'):
        with open(output_dir.joinpath(output_filename), "w", encoding='utf-8') as fout:
            fout.write(f"""action_endpoint:
  url: "{url}"
""")

    # http://localhost:5055/webhook
    # need to write: 'nlu'
    def save_nlu_to_file(
            self,
            intent_name: Text = 'test_intent',
            intent_examples: List = ['раз', '2 (два)', 'три'],
            output_filename: Text = 'nlu.yml'):

        """
        Записывает данные для одного интента в указанный nlu.yml
        """

        output_filename = self.output_dir.joinpath(output_filename)

        with open(output_filename, 'a', encoding='utf-8') as fout:
            intent_msgs_str = f"{TAB_SYMBOL * 2}- " + f'\n{TAB_SYMBOL * 2}- '.join(intent_examples)
            fout.write(f"""- intent: {intent_name}
{TAB_SYMBOL}examples: |
{intent_msgs_str}

""")

    def save_rules_to_file(
            self,
            intent_names: Text = ['test_intent', 'ДВа интент', 'Три интент'],
            output_filename: Text = "rules.yml"):
        """
        Записывает правила
        вида intent_name -> utter_intent_name
        в указанный rules.yml
        """
        output_filename = self.output_dir.joinpath(output_filename)

        with open(output_filename, 'a', encoding='utf-8') as fout:
            # fout.write("rules:\n")

            for intent_name in intent_names:
                fout.write(f"""- rule: new rule about {intent_name}
  steps:
  - intent: {intent_name}
  - action: utter_{intent_name}
""")

    def save_intent_and_action_names(
            self,
            intent_names: List[str],
            action_names=None,
            domain_output_filename="domain.yml"):
        """
        Записывает список интентов и список правил в файл domain.yml
        """
        domain_output_filename = self.output_dir.joinpath(domain_output_filename)

        separator = '\n- '
        intents_str = separator + separator.join(intent_names)
        if action_names is not None:
            actions_str = separator + separator.join(action_names)
        else:
            actions_str = separator + separator.join(f"utter_{intent_name}" for intent_name in intent_names)

        template = f"""

intents:{intents_str}

actions:{actions_str}

"""
        with open(domain_output_filename, 'a', encoding='utf-8') as fout:
            fout.write(template)

    def save_intent_responses_to_file(
            self,
            intent_name: Text = 'test_intent',
            intent_response_examples: List = ['ответ 1', 'ответ 2 (два)', 'ответ три'],
            responses_output_filename: Text = "responses.yml"):
        """
        Записывает базу данных ответов в указанный файл домена (domain.yml)
        """

        output_filename = self.output_dir.joinpath(responses_output_filename)

        responses_str = ''.join([f'{TAB_SYMBOL}- text: "{response}"\n' for response in intent_response_examples])

        # template =
        with open(output_filename, 'a', encoding='utf-8') as fout:
            fout.write(f"""{TAB_SYMBOL}utter_{intent_name}:
{responses_str.replace("̆", "")}""")

    def __write_headers__(self,
                          nlu_output_filename='nlu.yml',
                          responses_output_filename='responses.yml',
                          rules_output_filename="rules.yml",
                          domain_output_filename='domain.yml',
                          config_output_filename='config.yml'
                          ):

        """
        Записывает метаданные во все конфигурационные файлы
        nlu, rules, responses, domain
        """
        nlu_output_filename, \
            responses_output_filename, \
            rules_output_filename, \
            domain_output_filename, \
            config_output_filename = [
            self.output_dir.joinpath(filename) \
            for filename in [
                nlu_output_filename, \
                responses_output_filename, \
                rules_output_filename, \
                domain_output_filename, \
                config_output_filename]
        ]

        with open(nlu_output_filename, 'w') as nlu_fout, \
                open(responses_output_filename, 'w') as responses_fout, \
                open(rules_output_filename, 'w') as rules_fout, \
                open(domain_output_filename, 'w') as domain_fout, \
                open(config_output_filename, 'w') as config_fout:
            nlu_fout.write("""
version: '3.1'

nlu:

""")
            responses_fout.write("responses:\n\n")
            rules_fout.write("rules:\n\n")
            domain_fout.write("""version: '3.1'
session_config:
  session_expiration_time: 60
  carry_over_slots_to_new_session: false
""")
            config_fout.write(f"""
language: ru


pipeline:
- name: WhitespaceTokenizer
- name: CountVectorsFeaturizer
  analyzer: char_wb
  min_ngram: 2
  max_ngram: 6
- name: CountVectorsFeaturizer
- name: DIETClassifier
  epochs: {DIET_EPOCHS}
  num_transformer_layers: 4
  transformer_size: 256
  use_masked_language_model: true
  drop_rate: 0.25
  weight_sparsity: 0.7
  batch_size: [64, 256]
  embedding_dimension: 100
  hidden_layer_sizes:
    text: [512, 128]
"""
                              )

    def run_pipeline_for_hierarchical_classifier(self,
                                                 df,
                                                 use_subintents="single",
                                                 **filenames):
        """
        use_subintents: single, hierarchical, default
        Отличия от обычного:
        1. В nlu нужно записывать данные по субинтентам
        2. В responses (а далее в domain) записываем ответы для каждого из субинтентов
        Что осталось тем же:
        1. rules вида intent->utter_about_intent
        2. action_names в domain.yml включают в себя только данные по интентам (без субинтентов)
        """

        self.output_dir.mkdir(parents=True, exist_ok=True)  # create output_dir for dataset_name

        intent_names = df['intent'].unique().tolist()
        # sub_intent_names = df['subintent'].unique().tolist() # Это для классификатора без субинтентов

        self.__write_headers__(**filenames)
        self.save_intent_and_action_names(intent_names=intent_names,
                                          domain_output_filename=filenames['domain_output_filename'])
        # проходимся по каждому sub-интенту

        nlu_row_name = 'intent'

        for _, row in df.iterrows():
            intent_examples = row['questions']
            # intent_examples = [x for x in intent_examples if str(x) != 'nan']

            # print(F"Intent_name = {row['subintent']}, examples = {intent_examples}")
            self.save_nlu_to_file(intent_name=row[nlu_row_name],
                                  intent_examples=intent_examples,
                                  output_filename=filenames['nlu_output_filename']
                                  )
            self.save_intent_responses_to_file(intent_name=row[nlu_row_name],
                                               intent_response_examples=row['answers'],
                                               responses_output_filename=filenames['responses_output_filename'])
        self.save_rules_to_file(intent_names=intent_names,
                                output_filename=filenames['rules_output_filename'])
        if use_subintents == 'default':

            action_names = df['intent'].map(lambda x: f"utter_{x}").tolist()
            webhooks = [f"http://localhost:{port}/webhook" for port in (5005 + i for i in range(len(action_names)))]
            json_filename = 'webhooks_map.json'
            with open(self.output_dir.joinpath(json_filename), 'w') as fout:
                action_names_webhooks = dict(zip(action_names, webhooks))
                json.dump(action_names_webhooks,
                          fout,
                          ensure_ascii=False,
                          indent=4)

                # df[['intent']].to_excel(self.output_dir.joinpath("intent_names.xlsx"), index=False)
            for action_name, webhook_url in action_names_webhooks.items():
                expert_dir = self.output_dir.joinpath(action_name)
                expert_dir.mkdir(exist_ok=True)
                self.generate_endpoints_file(output_dir=expert_dir,
                                             output_filename=f"endpoints.yml",
                                             url=webhook_url)

    def update_config(self,
                      intent_names,
                      config_output_filename='config.yml',
                      n_epochs_for_response_selector=10):
        template_for_single_intent = """- name: ResponseSelector
  epochs: {epochs}
  retrieval_intent: {intent_name}
  num_transformer_layers: 4
  transformer_size: 256
  use_masked_language_model: false
  drop_rate: 0.25
  weight_sparsity: 0.7
  batch_size: [64, 256]
  embedding_dimension: 30
  hidden_layer_sizes:
    text: [512, 128]
"""
        template = f"""
pipeline:
{''.join(template_for_single_intent.format(epochs=n_epochs_for_response_selector,
                                           intent_name=intent_name) for intent_name in intent_names)}"""
        config_output_filename = self.output_dir.joinpath(config_output_filename)
        with open(config_output_filename, 'w') as fout:
            fout.write(template)


def clean_and_transliterate(intent_name):
    intent_name = str(intent_name)

    def clean(string: str):
        string = string.lower()
        for symbol, replace_value in {
            # "«": ""
            ',': "",
            ".": "",
            '"': '',
            '/': '',
            "'": '',
            ' ': '_',
        }.items():
            string = string.replace(symbol, replace_value)
        return string

    # res = translit(clean(intent_name), 'ru', reversed=True)
    res = clean(intent_name)
    return res


def transform_intent_names(df):
    """
    Переводит имя интента в валидную для RASA строку
    """
    df['intent'] = df['intent'].map(
        lambda x: clean_and_transliterate(x))


def split_df_by_intents(df):
    intent_names = df.intent.unique().tolist()
    # intent_names = [intent.replace(' ', '_') for intent in intent_names]

    intent_dataframes = {intent: df[df['intent'] == intent]
                         for intent in intent_names}
    return intent_dataframes


def create_subintents(intent_df, intent_name, use_subintents='hierarchical'):
    """true subintents == hierarchy of intents"""

    n_subintents = intent_df.shape[0]

    if use_subintents == 'default':
        create_intent_name = lambda x: "{intent_name}".format(intent_name=intent_name)
    else:
        sep = '_'
        create_intent_name = lambda x: "{intent_name}{sep}question_{x}".format(intent_name=intent_name,
                                                                               sep=sep,
                                                                               x=x)

    intent_df['subintent'] = range(1, n_subintents + 1)
    intent_df['subintent'] = intent_df['subintent'].map(
        create_intent_name)


def merge_intent_dataframes(intent_dataframes):
    df_s = [intent_dataframe \
            for _, intent_dataframe in intent_dataframes.items()
            ]

    final_df = pd.concat(df_s, ignore_index=True)

    return final_df


# convert q&a list serialized as `str` to lists
def clean_qa(question_or_answer_text: str):
    text = question_or_answer_text.strip()  #
    clean_map = {
        "\n": "",
        '"': "'",
    }
    for char in clean_map:
        text = text.replace(char, clean_map[char])

    return text


clean_and_eval = lambda x: [clean_qa(str(string)) for string in eval(x)]


def pipe(dataset_name: Text, input_file: Text, use_subintents: bool):
    working_dir = Path(WORKING_DIR)
    data_filename = working_dir.joinpath(input_file)
    output_filenames = {
        f"{config_type}_output_filename": f'{config_type}.yml'
        for config_type in
        ('nlu', 'responses', 'rules', 'domain', 'config')
    }

    qa_df = pd.read_excel(data_filename) \
        [["intent", "questions_merged", "answers_merged"]]
    qa_df.fillna("", inplace=True)

    qa_df.rename(columns={
        "questions_merged": "questions",
        "answers_merged": "answers"
    },
        inplace=True)

    for col_name in ['answers', 'questions']:
        qa_df[col_name] = qa_df[col_name].map(clean_and_eval)

    transform_intent_names(qa_df)

    intent_dataframes = split_df_by_intents(qa_df)

    for intent, intent_dataframe in intent_dataframes.items():
        if use_subintents == 'default':
            intent_dict = {
                col: [list(chain.from_iterable(intent_dataframe[col].tolist()))]
                for col in ('questions', 'answers')
            }
            intent_dataframes[intent] = pd.DataFrame.from_dict(data=intent_dict)
        create_subintents(intent_dataframes[intent], intent, use_subintents=use_subintents)

    qa_df = merge_intent_dataframes(intent_dataframes)

    config_generator = RasaDataGenerator(working_dir.joinpath('rasa_data', dataset_name))
    config_generator.run_pipeline_for_hierarchical_classifier(df=qa_df, use_subintents=use_subintents,
                                                              **output_filenames)


"""
Необходимые колонки
`intent`, `questions_merged`: List, `answers_merged`: List
"""
