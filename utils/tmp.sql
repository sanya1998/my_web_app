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


SELECT pid,
       to_char(query_start, 'HH24:MI:SS') as start,
       to_char(now() - pg_stat_activity.query_start,'MI:SS') as duration,
       query,
       state,
       client_addr
FROM pg_stat_activity
WHERE state is not null
ORDER BY query_start desc
LIMIT 500;