WITH booked_rooms AS (
    WITH args (check_into, check_out) AS (
        VALUES ('2025-07-10'::date, '2025-07-20'::date)
    )
    SELECT bookings.room_id
    FROM bookings, args
    WHERE
        date_from >= check_into AND date_from < check_out OR
        date_from < check_into AND date_to > check_into
)
SELECT
    rooms.id, rooms.quantity - COUNT(booked_rooms.room_id) AS lost
FROM rooms
LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id -- Показать остаток во всех комнатах
-- INNER JOIN booked_rooms ON booked_rooms.room_id = rooms.id  -- Показать остаток только в тех комнатах, которые есть в booked_rooms
GROUP BY rooms.id, rooms.quantity;




