Добавление плагина для дедупликации очереди в Rabbitmq.
1. Найти актуальную версию плагина https://github.com/noxdafox/rabbitmq-message-deduplication/releases
2. В выбранной версии плагина есть несколько архивов, нужно выбрать тот, что подходит под версию rabbitmq 
```
rabbitmqctl version
4.1.1
```
3. Скачать и разархвировать выбранный архив
```
curl -L -o ./docker/custom_rabbitmq/plugins/plugins.zip \
  https://github.com/noxdafox/rabbitmq-message-deduplication/releases/download/0.7.3/plugins-rmqv4.1.x-erl27-elx1.18.zip

cd ./docker/custom_rabbitmq/plugins
unzip plugins.zip
rm plugins.zip
ls -la rabbitmq_message_deduplication-0.7.3.ez
cd ../../..
```
4. docker-compose подхватит его через `volumes`
5. плагин включится до запуска контейнера в `command`
