-- 2. Marketing Effectiveness: Engagement vs. Conversion

WITH engagement_analysis AS (
    SELECT 
        e.EngagementID, 
        e.ProductID, 
        e.ContentType, 
        e.Likes, 
        e.ViewsClicksCombined, 
        cj.Stage, 
        cj.Action AS UserAction
    FROM engagement_data e
    LEFT JOIN customer_journey cj ON e.ProductID = cj.ProductID
)
SELECT 
    ContentType,
    COUNT(DISTINCT EngagementID) AS Total_Engagements,
    SUM(Likes) AS Total_Likes,
    SUM(CASE WHEN Stage = 'Checkout' AND UserAction = 'Purchase' THEN 1 ELSE 0 END) AS Total_Purchases,
    ROUND(
        (SUM(CASE WHEN Stage = 'Checkout' AND UserAction = 'Purchase' THEN 1 ELSE 0 END) * 100.0) / COUNT(DISTINCT EngagementID), 2
    ) AS Conversion_Rate
FROM engagement_analysis
GROUP BY ContentType
ORDER BY Conversion_Rate DESC;




