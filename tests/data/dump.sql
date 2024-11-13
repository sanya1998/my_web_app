INSERT INTO
    hotels (id, name, location, services, image_id)
VALUES
    (1, 'Cosmos Collection Altay', 'Республика Алтай, +точный адрес', array ['Wi-Fi', 'Парковка'], 1),
    (2, 'Skala', 'Адрес Skala', array ['Wi-Fi'], 2),
    (3, 'Ару-Кёль', 'республика, район, улица, дом', array ['Парковка'], 3),
    (4, 'Гостиница Сыктывкар', 'Коми, адрес', array ['Тренажёрный зал'], 4),
    (5, 'Palace', 'Республика Коми, адрес', array ['Кондиционер'], 5),
    (6, 'Bridge Resort', 'Поселок Сириус, улица, дом', array ['Wi-Fi'], 6);
SELECT setval(pg_get_serial_sequence('hotels', 'id'), (SELECT MAX(id) FROM hotels));


INSERT INTO
    rooms (id, hotel_id, name, price, quantity, services, image_id)
VALUES
    (1, 1, 'Улучшенный с террасой и видом на озеро', 24500, 5, array ['Wi-Fi'], 7),
    (2, 1, 'Делюкс Плюс', 24450, 4, array ['Wi-Fi'], 8),
    (3, 2, 'Номер на 2-х человек', 26500, 6, array []::varchar[], 9),
    (4, 2, 'Номер на 3-х человек', 29500, 2, array []::varchar[], 10),
    (5, 3, 'Полулюкс', 7500, 10, array []::varchar[], 11),
    (6, 3, '2-комнатный люкс комфорт', 8000, 3, array []::varchar[], 12),
    (7, 4, 'Стандпрт двухместный', 4300, 4, array []::varchar[], 13),
    (8, 4, 'Стандарт улучшенный ПЛЮС', 6500, 7, array []::varchar[], 14),
    (9, 5, 'Номер стандарт с 2 односпальными кроватями', 13500, 4, array []::varchar[], 15),
    (10, 5, 'Номер полулюкс премиум (с завтраком)', 15500, 4, array []::varchar[], 16),
    (11, 6, 'Стандарт (типовой корпус)', 26500, 4, array []::varchar[], 17);
SELECT setval(pg_get_serial_sequence('rooms', 'id'), (SELECT MAX(id) FROM rooms));


INSERT INTO
    users (id, email, roles, hashed_password)
VALUES
    (1, 'user@example.com', array ['admin', 'manager', 'moderator'], '07ab59f4731b0790d0acfded6a52d2c53e7e3c6a1e241f6dfe3a41f3072e07fb'), -- Для свагера, чтоб оставлять пароль по умолчанию
    (2, 'user123@example.com', array ['admin'], 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f'), -- Для админки, чтобы запомнить легкий пароль в браузере
    (3, 'fedor@moloko.ru', array ['admin']::varchar[], '962e0437e05964f5983ac12fa343324207a3bbde54779c83b5b9cc3ee2b3143f'),
    (4, 'sharik@moloko.ru', array []::varchar[], 'b757f284ca76df96dd2d70521a6af2005c335e5a8e3ea074b7cdbaefbb359387'),
    (5, 'kot@pes.ru', array ['manager']::varchar[], 'b757f284ca76df96dd2d70521a6af2005c335e5a8e3ea074b7cdbaefbb359387');
SELECT setval(pg_get_serial_sequence('users', 'id'), (SELECT MAX(id) FROM users));


INSERT INTO
    bookings (room_id, user_id, date_from, date_to, price)
VALUES
    (1, 3, '2024-07-15', '2024-07-30', 24500),
    (7, 2, '2024-07-12', '2024-07-21', 4300),
    (3, 1, '2024-07-01', '2024-07-14', 26500),
    (9, 4, '2024-02-01', '2024-02-14', 13500),
    (10, 4, '2024-06-01', '2024-06-14', 15500),
    (10, 4, '2024-07-01', '2024-07-14', 15500);
SELECT setval(pg_get_serial_sequence('bookings', 'id'), (SELECT MAX(id) FROM bookings));
