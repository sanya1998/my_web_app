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

SELECT hotels.name, hotels.location, hotels.services, hotels.image_id, hotels.id, sum(rooms.quantity - coalesce(occupied, 0)) AS remain_by_hotel
FROM hotels LEFT OUTER JOIN rooms ON rooms.hotel_id = hotels.id GROUP BY hotels.name, hotels.location, hotels.services, hotels.image_id, hotels.id
 LIMIT 10 OFFSET 0

WITH booked_rooms AS
(SELECT bookings.room_id AS room_id, count(bookings.room_id) AS occupied
FROM bookings
WHERE bookings.date_from >= '2024-07-12' AND bookings.date_from < '2024-07-20' OR bookings.date_from < '2024-07-12' AND bookings.date_to > '2024-07-12' GROUP BY bookings.room_id)
 SELECT hotels.name, hotels.location, hotels.services, hotels.image_id, hotels.id, rooms.quantity - coalesce(booked_rooms.occupied, 0) AS remain_by_room
FROM hotels LEFT OUTER JOIN rooms ON rooms.hotel_id = hotels.id LEFT OUTER JOIN booked_rooms ON booked_rooms.room_id = rooms.id
WHERE rooms.quantity - coalesce(booked_rooms.occupied, 0) > 0 GROUP BY hotels.name, hotels.location, hotels.services, hotels.image_id, hotels.id;