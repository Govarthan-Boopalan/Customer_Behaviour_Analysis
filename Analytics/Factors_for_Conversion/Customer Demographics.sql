-- ⃣ Finding Common Actions Leading to Successful Conversions

-- Customer Demographics & Conversion Analysis>> Find out which customer segments have the highest conversion rates.


WITH customer_conversion_age AS (
    SELECT 
        CASE 
            WHEN c.Age < 30 THEN '<30'
            WHEN c.Age BETWEEN 30 AND 45 THEN '30-45'
            ELSE '>45'
        END AS Age_Range,
        COUNT(DISTINCT cj.CustomerID) AS Total_Customers,
        SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.`Action` = 'Purchase' THEN 1 ELSE 0 END) AS Total_Purchases,
        ROUND(
            (SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.`Action` = 'Purchase' THEN 1 ELSE 0 END) * 100.0) / COUNT(DISTINCT cj.CustomerID), 2
        ) AS Conversion_Rate
    FROM customer_journey cj
    JOIN customers c ON cj.CustomerID = c.CustomerID
    GROUP BY Age_Range
),

customer_conversion_gender AS (
    SELECT 
        c.Gender,
        COUNT(DISTINCT cj.CustomerID) AS Total_Customers,
        SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.`Action` = 'Purchase' THEN 1 ELSE 0 END) AS Total_Purchases,
        ROUND(
            (SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.`Action` = 'Purchase' THEN 1 ELSE 0 END) * 100.0) / COUNT(DISTINCT cj.CustomerID), 2
        ) AS Conversion_Rate
    FROM customer_journey cj
    JOIN customers c ON cj.CustomerID = c.CustomerID
    GROUP BY c.Gender
),

customer_conversion_country AS (
    SELECT 
        g.Country,
        COUNT(DISTINCT cj.CustomerID) AS Total_Customers,
        SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.`Action` = 'Purchase' THEN 1 ELSE 0 END) AS Total_Purchases,
        ROUND(
            (SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.`Action` = 'Purchase' THEN 1 ELSE 0 END) * 100.0) / COUNT(DISTINCT cj.CustomerID), 2
        ) AS Conversion_Rate
    FROM customer_journey cj
    JOIN customers c ON cj.CustomerID = c.CustomerID
    JOIN geography g ON c.GeographyID = g.GeographyID
    GROUP BY g.Country
)

-- Corrected UNION statement
SELECT 'Age Range' AS Group_By, Age_Range AS Group_Value, Total_Customers, Total_Purchases, Conversion_Rate FROM customer_conversion_age
UNION ALL
SELECT 'Gender' AS Group_By, Gender AS Group_Value, Total_Customers, Total_Purchases, Conversion_Rate FROM customer_conversion_gender
UNION ALL
SELECT 'Country' AS Group_By, Country AS Group_Value, Total_Customers, Total_Purchases, Conversion_Rate FROM customer_conversion_country;

