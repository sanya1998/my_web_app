Простой фронт нужен для тестирования некоторых бэкенд-фич.
Например, CORS.
## Запустить сервер-фронт http://localhost:3000/
### Запуск первый раз:
1. Установить Node.js из https://nodejs.org
2. 
```
$ cd frontend
$ npx create-react-app my_front
$ npm install axios --save
$ cd my_front
$ npm start
```
3. Переименовать файл `frontend/my_front/src/App.jsx` в `frontend/my_front/src/App.jsx`.
4. Наполнить `frontend/my_front/src/App.jsx` своей логикой


### Запуск каждый раз
```
$ cd frontend/my_front
$ npm start
```