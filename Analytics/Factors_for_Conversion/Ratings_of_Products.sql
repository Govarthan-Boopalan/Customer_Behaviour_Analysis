
-- Find Highest-Rated Products
SELECT p.ProductID, p.ProductName, AVG(r.Rating) AS AvgRating
FROM customer_reviews r
JOIN products p ON r.ProductID = p.ProductID
GROUP BY p.ProductID, p.ProductName
ORDER BY AvgRating DESC
LIMIT 5;

-- Find Lowest-Rated Products
SELECT p.ProductID, p.ProductName, AVG(r.Rating) AS AvgRating
FROM customer_reviews r
JOIN products p ON r.ProductID = p.ProductID
GROUP BY p.ProductID, p.ProductName
ORDER BY AvgRating ASC
LIMIT 5;


