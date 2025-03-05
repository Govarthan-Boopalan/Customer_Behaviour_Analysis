-- 1️⃣ Identifying Drop-Off Points in the Customer Journey

WITH journey_data AS (
    SELECT 
        Stage,
        COUNT(*) AS Total_Visits,
        SUM(CASE WHEN `Action` = 'Drop-off' THEN 1 ELSE 0 END) AS Dropoffs
    FROM customer_journey
    GROUP BY Stage
)
SELECT 
    Stage,
    Total_Visits,
    Dropoffs,
    ROUND((Dropoffs * 100.0) / Total_Visits, 2) AS Dropoff_Rate
FROM journey_data
ORDER BY Dropoff_Rate DESC;
