SELECT p.ProductID, p.ProductName, COUNT(r.ReviewID) AS ReviewCount, 
       AVG(r.Rating) AS AvgRating
FROM customer_reviews r
JOIN products p ON r.ProductID = p.ProductID
GROUP BY p.ProductID, p.ProductName
ORDER BY ReviewCount DESC;
