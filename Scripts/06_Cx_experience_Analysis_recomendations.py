import mysql.connector
import pandas as pd
from textblob import TextBlob
import os

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="456123",
    database="ShopEasy"
)
cursor = conn.cursor()

# Dictionary to store SQL queries
queries = {
    "negative_reviews": """SELECT cr.ReviewID, cr.ProductID, p.ProductName, cr.ReviewText, cr.Rating
                           FROM customer_reviews cr
                           JOIN products p ON cr.ProductID = p.ProductID
                           WHERE cr.Rating <= 2;""",

    "lowest_rated_products": """SELECT cr.ProductID, p.ProductName, AVG(cr.Rating) AS AvgRating, COUNT(*) AS ReviewCount
                                FROM customer_reviews cr
                                JOIN products p ON cr.ProductID = p.ProductID
                                GROUP BY cr.ProductID, p.ProductName
                                ORDER BY AvgRating ASC LIMIT 5;""",

    "low_repeat_customers": """SELECT c.CustomerID, COUNT(DISTINCT cj.JourneyID) AS PurchaseCount
                               FROM customers c
                               JOIN customer_journey cj ON c.CustomerID = cj.CustomerID
                               WHERE cj.Action = 'purchase'
                               GROUP BY c.CustomerID
                               HAVING PurchaseCount = 1;""",

    "common_complaints": """SELECT cr.ReviewText, p.ProductName, COUNT(*) AS Frequency
                            FROM customer_reviews cr
                            JOIN products p ON cr.ProductID = p.ProductID
                            WHERE cr.Rating <= 2
                            GROUP BY cr.ReviewText, p.ProductName
                            ORDER BY Frequency DESC LIMIT 10;"""
}

recommendations = []

# 1️⃣ **Sentiment Analysis on Negative Reviews**
cursor.execute(queries["negative_reviews"])
reviews = cursor.fetchall()
negative_review_count = len(reviews)

if negative_review_count > 0:
    review_sentiments = [TextBlob(row[3]).sentiment.polarity for row in reviews]  # Analyzing the ReviewText
    avg_sentiment = sum(review_sentiments) / negative_review_count

    if avg_sentiment < -0.2:  # Strong negative sentiment
        recommendations.append("Customer sentiment analysis indicates dissatisfaction. Address common complaints and improve product quality.")

# 2️⃣ **Identify Lowest-Rated Products**
cursor.execute(queries["lowest_rated_products"])
lowest_products = cursor.fetchall()

if lowest_products:
    recommendations.append("The following products have the lowest ratings and need quality improvement:")
    for product in lowest_products:
        recommendations.append(f"- {product[1]} (Product ID: {product[0]}): Avg Rating {round(product[2],2)} (Reviews: {product[3]})")

# 3️⃣ **Find Customers with Only One Purchase**
cursor.execute(queries["low_repeat_customers"])
low_repeat_customers = cursor.fetchall()

if low_repeat_customers:
    recommendations.append(f"{len(low_repeat_customers)} customers made only one purchase. Consider implementing loyalty rewards or personalized follow-ups to increase retention.")

# 4️⃣ **Identify Most Common Complaints**
cursor.execute(queries["common_complaints"])
common_complaints = cursor.fetchall()

if common_complaints:
    recommendations.append("Top recurring customer complaints:")
    for complaint in common_complaints:
        recommendations.append(f"- {complaint[0]} (Product: {complaint[1]} | Mentioned {complaint[2]} times)")

# Close database connection
cursor.close()
conn.close()


# Save recommendations to a text file
output_file = "../results/customer_experience_recommendations.txt"
with open(output_file, "w") as file:
    for rec in recommendations:
        file.write(rec + "\n")
