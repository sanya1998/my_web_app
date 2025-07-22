FROM python:3.10.11
WORKDIR /code
COPY pyproject.toml poetry.lock /code/
# TODO: нужно ли RUN pip install --upgrade pip ?
# TODO: pip install poetry==1.4.2 перед копированием ?
RUN pip install poetry==1.4.2
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
# TODO: poetry можно удалить

# Они уже исполняемыми попадают в качестве volume. TODO: хорошо ли это?
# RUN chmod a+x /code/docker/custom_python/*.sh
