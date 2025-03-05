WITH review_analysis AS (
    SELECT 
        cr.ReviewID, 
        cr.CustomerID, 
        cr.ProductID, 
        p.ProductName, 
        cr.Rating, 
        cr.ReviewText,
        CASE 
            WHEN Rating <= 2 THEN 'Negative'
            WHEN Rating = 3 THEN 'Neutral'
            ELSE 'Positive'
        END AS Sentiment
    FROM customer_reviews cr
    JOIN products p ON cr.ProductID = p.ProductID
)
-- Customer Reviews Sentiment & Satisfaction Trends


SELECT 
    Sentiment,
    COUNT(*) AS Total_Reviews,
    ROUND(AVG(Rating), 2) AS Avg_Rating
FROM review_analysis
GROUP BY Sentiment
ORDER BY Avg_Rating DESC;
