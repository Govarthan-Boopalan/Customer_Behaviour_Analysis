-- Product Influence on Conversions (By Product Name)

WITH product_conversion AS (
    SELECT 
        p.ProductName,
        ROUND(AVG(p.Price), 2) AS Avg_Price,
        COUNT(DISTINCT cj.CustomerID) AS Unique_Customers,
        SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.`Action` = 'Purchase' THEN 1 ELSE 0 END) AS Total_Purchases,
        ROUND(
            (SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.`Action` = 'Purchase' THEN 1 ELSE 0 END) * 100.0) / COUNT(DISTINCT cj.CustomerID), 2
        ) AS Conversion_Rate
    FROM customer_journey cj
    JOIN products p ON cj.ProductID = p.ProductID
    GROUP BY p.ProductName
)
SELECT * FROM product_conversion
ORDER BY Conversion_Rate DESC, Total_Purchases DESC;
