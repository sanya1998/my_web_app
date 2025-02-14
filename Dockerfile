FROM python:3.10.11
WORKDIR /code
COPY poetry.lock pyproject.toml /code/
RUN pip install poetry==1.4.2
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
# TODO: poetry можно удалить
# TODO: все ли копировать?
COPY . /code


CMD ["python3", "manage.py", "runserver"]
