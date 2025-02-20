FROM python:3.10.11
WORKDIR /code
COPY pyproject.toml poetry.lock /code/
RUN pip install poetry==1.4.2
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
# TODO: poetry можно удалить
# TODO: все ли копировать?
# TODO: копировать сначала то, что редко меняется
COPY . /code
RUN chmod a+x /code/docker/custom_python/*.sh
