# Curator-support

## 🛠 Установка

### Локально

   1. Склонируйте проект и войдите в него
      ```
      git clone https://github.com/DigitalBreakthroughRusskayKrasavica3-0/curator-support
      cd curator-support/backend
      ```
   
   2. Создайте и активируйте виртуальное окружение
       ```
       python -m venv venv
       source venv/bin/activate
       ```
   
   3. Установите зависимости в интерактивном режиме
      ```
      pip install -e .
      pip install rasa --ignore-requires-python
      pip install SQLAlchemy==2.0.23
      pip install -U aiogram
      pip install openpyxl dask
      ```
   
   4. Инициалиируйте API фреймворка RASA (в другом процессе с активированным venv)
      ```
      cd src/curator_support/lms/rasa && python start.py && python -m rasa run -p 6060 -i 127.0.0.1 --enable-api -m ./models/model.tar.gz
      ```
   
   5. Переименуйте и заполните конфиги (app.example.toml -> app.toml, app.docker.example.toml -> app.docker.toml)
   
   6. Запустите бота (в первом процессе)
      ```
      python -m curator_support.main.bot
      ```

### Docker

   1. Склонируйте проект и войдите в директорию с ним
      ```
      git clone [https://github.com/akiko23/greenatom-test](https://github.com/DigitalBreakthroughRusskayKrasavica3-0/curator-suppor
      cd curator-suppor/backend
      ```
   
   2. Создайте докер образ
       ```
       docker build -f Dockerfile -t curator-support .
       ```
       
   3. Запустите компоус
       ```
       docker-compose up -d
       ```

## 🧰 Tech Stack


### Web API

- [FastAPI](https://fastapi.tiangolo.com/) - Modern and fast python web-framework for building APIs;
- [FastAPIUsers](https://fastapi-users.github.io/fastapi-users/latest/) - A library adding quick registration and authentication system;
- [Uvicorn](https://www.uvicorn.org/) - ASGI web server implemetation for python. 

### Telegram Bot API

- [aiogram](https://fastapi.tiangolo.com/) - Modern and fully asynchronous framework for Telegram Bot API;

### Backend/low-level part

- [Toml](https://pypi.org/project/toml/) - A library for parsing and serialising configs from toml files into python structures;
- [Pydantic](https://docs.pydantic.dev/latest/) - A most popular library for building validation rules;
- [SQLAlchemy](https://www.sqlalchemy.org/) - An ORM and SQL toolkit that provides easy database interaction from python;
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) - Database migration tool for SQLAlchemy.

### Testing
- [Pytest](https://docs.pytest.org) - A python testing framework;
- [Unittest](https://docs.python.org/3/library/unittest.html) - A python builtin library for building unit tests

### Docs
- [SwaggerUI](https://github.com/swagger-api/swagger-ui) -  A tool for describing, visualizing and interaction with the API’s resources

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/Sirius-journal-app/bakend/tags).

## Authors

> See the list of [contributors](https://github.com/Sirius-journal-app/bakend/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details

