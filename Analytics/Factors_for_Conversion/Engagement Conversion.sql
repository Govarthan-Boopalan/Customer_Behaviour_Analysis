-- 3️⃣ Customer Journey Paths Leading to Conversions

WITH engagement_conversion AS (
    SELECT 
        e.ContentType,
        COUNT(DISTINCT e.EngagementID) AS Total_Engagements,
        SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.`Action` = 'Purchase' THEN 1 ELSE 0 END) AS Total_Purchases,
        ROUND(
            (SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.`Action` = 'Purchase' THEN 1 ELSE 0 END) * 100.0) / COUNT(DISTINCT e.EngagementID), 2
        ) AS Conversion_Rate
    FROM engagement_data e
    JOIN customer_journey cj ON e.ProductID = cj.ProductID
    GROUP BY e.ContentType
)
SELECT * FROM engagement_conversion
ORDER BY Conversion_Rate DESC;
