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

WITH anon_1 AS (
    SELECT bookings.room_id AS room_id, count(bookings.room_id) AS occupied
    FROM bookings
    WHERE bookings.date_from >= '2025-07-07' AND bookings.date_from < '2025-07-08' OR
          bookings.date_from < '2025-07-07' AND bookings.date_to > '2025-07-07' GROUP BY bookings.room_id
)
SELECT DISTINCT hotels.name, hotels.location, hotels.services, hotels.image_id, hotels.id
FROM hotels
    LEFT OUTER JOIN anon_1 ON anon_1.room_id = rooms.id
    LEFT OUTER JOIN rooms ON rooms.hotel_id = hotels.id
WHERE rooms.quantity > coalesce(anon_1.occupied, 0) AND rooms.price <= 7700
LIMIT 10 OFFSET 0