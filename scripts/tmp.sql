-- Показать, сколько осталось свободных номеров для каждого типа комнат на указанный период
WITH
    dates (check_into, check_out) AS (VALUES ('2024-07-10'::date, '2024-07-20'::date)),
    booked_rooms AS (
        SELECT bookings.room_id
        FROM bookings, dates
        WHERE
            date_from >= check_into AND date_from < check_out OR
            date_from < check_into AND date_to > check_into
)
SELECT rooms.id AS room_id, rooms.quantity - COUNT(booked_rooms.room_id) AS remain
FROM rooms
LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id -- Показать остаток во всех комнатах
-- INNER JOIN booked_rooms ON booked_rooms.room_id = rooms.id  -- Показать остаток только в тех комнатах, которые есть в booked_rooms
GROUP BY rooms.id;

-- TODO: в sqlalchemy возвращает неизмененные total_cost, а в SQL все норм
UPDATE bookings
SET price=6000
WHERE bookings.id = 1
RETURNING
    bookings.id,
    bookings.price,
    bookings.total_cost;

SELECT bookings.room_id, bookings.user_id, bookings.date_from, bookings.date_to, bookings.price, bookings.total_days, bookings.total_cost, bookings.id
FROM bookings LEFT OUTER JOIN rooms ON rooms.id = bookings.room_id