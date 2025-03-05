#!/usr/bin/env python
# coding: utf-8

# In[42]:


import mysql.connector
import pandas as pd

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="456123",
    database="ShopEasy"
)
cursor = conn.cursor()

# Queries for business insights
queries = {
    "underperforming_products": """SELECT ProductName, AvgRating, PurchaseCount 
                                   FROM (SELECT p.ProductName, AVG(cr.Rating) AS AvgRating, 
                                                 COUNT(cj.JourneyID) AS PurchaseCount
                                         FROM products p
                                         LEFT JOIN customer_reviews cr ON p.ProductID = cr.ProductID
                                         LEFT JOIN customer_journey cj ON p.ProductID = cj.ProductID AND cj.Action = 'purchase'
                                         GROUP BY p.ProductName
                                         ORDER BY AvgRating ASC, PurchaseCount ASC
                                         LIMIT 5) subquery;""",

    "best_marketing_channels": """SELECT ContentType, AVG(Views) AS AvgViews, AVG(Clicks) AS AvgClicks, COUNT(cj.JourneyID) AS Purchases
                                  FROM engagement_data e
                                  LEFT JOIN customer_journey cj ON e.ProductID = cj.ProductID AND cj.Action = 'purchase'
                                  GROUP BY e.ContentType
                                  ORDER BY Purchases DESC;"""
}

recommendations = []

# Execute queries
for key, query in queries.items():
    cursor.execute(query)
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
    
    # Generate recommendations
    if key == "underperforming_products":
        for _, row in df.iterrows():
            recommendations.append(f"Consider improving or marketing {row['ProductName']} (Rating: {row['AvgRating']}, Sales: {row['PurchaseCount']}).")
    
    elif key == "best_marketing_channels":
        for _, row in df.iterrows():
            recommendations.append(f"Boost marketing in {row['ContentType']} campaigns (Avg Views: {row['AvgViews']}, Avg Clicks: {row['AvgClicks']}, Purchases: {row['Purchases']}).")

# Save recommendations
with open("../results/Marketing_recommendations.txt", "w") as file:
    for rec in recommendations:
        file.write(rec + "\n")

print("Marketing recommendations saved.")

