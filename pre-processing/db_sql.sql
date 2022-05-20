-- This holds the SQL queries used for the DB.


-- Generating travel times for day time trips
INSERT INTO public.travel_times_day_time(
	pulocationid, dolocationid, travel_time)
SELECT 
	pulocationid,
	dolocationid,
	extract(epoch FROM (dropoff_datetime - pickup_datetime)) AS travel_time 
FROM public.trip_data_day_time