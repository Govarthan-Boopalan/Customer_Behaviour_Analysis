-- Calculate Average Duration per Stage for Engagement Insights
SELECT 
    Stage,
    COUNT(*) AS Total_Visits,
    ROUND(AVG(Duration), 2) AS Avg_Duration_Seconds
FROM customer_journey
WHERE Duration IS NOT NULL
GROUP BY Stage
ORDER BY Avg_Duration_Seconds DESC;
