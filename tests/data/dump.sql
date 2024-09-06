INSERT INTO
    hotels (id, name, location, services, image_id)
VALUES
    (1, 'Cosmos Collection Altay', 'Республика Алтай, +точный адрес', array ['Wi-Fi', 'Парковка'], 1),
    (2, 'Skala', 'Адрес Skala', array ['Wi-Fi'], 2),
    (3, 'Ару-Кёль', 'республика, район, улица, дом', array ['Парковка'], 3),
    (4, 'Гостиница Сыктывкар', 'Коми, адрес', array ['Тренажёрный зал'], 4),
    (5, 'Palace', 'Республика Коми, адрес', array ['Кондиционер'], 5),
    (6, 'Bridge Resort', 'Поселок Сириус, улица, дом', array ['Wi-Fi'], 6);

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

INSERT INTO
    users (id, email, roles, hashed_password)
VALUES
    (1, 'user@example.com', array ['admin', 'manager'], '07ab59f4731b0790d0acfded6a52d2c53e7e3c6a1e241f6dfe3a41f3072e07fb'),
    (2, 'fedor@moloko.ru', array []::varchar[], 'tut_budet_hashed_password_1'),
    (3, 'sharik@moloko.ru', array []::varchar[], 'tut_budet_hashed_password_2');

INSERT INTO
    bookings (room_id, user_id, date_from, date_to, price)
VALUES
    (1, 3, '2023-06-15', '2023-06-30', 24500),
    (7, 2, '2024-07-12', '2024-07-21', 4300),
    (3, 1, '2024-07-01', '2024-07-14', 5300);
