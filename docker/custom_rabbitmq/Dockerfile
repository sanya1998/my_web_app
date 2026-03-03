ARG RMQ_VERSION

FROM rabbitmq:${RMQ_VERSION}

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y curl unzip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Копируем все три .ez файла (они уже распакованы в ./plugins)
COPY docker/custom_rabbitmq/plugins/*.ez /opt/rabbitmq/plugins/

# Включаем плагин офлайн (elixir и logger подтянутся автоматически)
RUN rabbitmq-plugins enable --offline rabbitmq_message_deduplication

# Стандартная команда запуска
CMD ["rabbitmq-server"]