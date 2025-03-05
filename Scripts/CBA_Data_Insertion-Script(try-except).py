import pandas as pd
from sqlalchemy import create_engine, text
import mysql.connector

try:
    # Load data from CSV files
    customer_journeyDf = pd.read_csv("../data/customer_journey.csv")
    customer_reviewsDf = pd.read_csv("../data/customer_reviews.csv")
    customersDf = pd.read_csv("../data/customers.csv")
    engagement_dataDf = pd.read_csv("../data/engagement_data.csv")
    geographyDf = pd.read_csv("../data/geography.csv")
    productsDf = pd.read_csv("../data/products.csv")

    # Data cleaning and preprocessing
    customer_journeyDf['Duration'] = customer_journeyDf['Duration'].fillna(0)
    customer_journeyDf['Stage'] = customer_journeyDf['Stage'].str.lower()
    customer_journeyDf['Action'] = customer_journeyDf['Action'].str.lower()
    customer_journeyDf = customer_journeyDf.drop_duplicates()

    customer_reviewsDf['ReviewText'] = customer_reviewsDf['ReviewText'].fillna("No review")
    customer_reviewsDf['ReviewText'] = customer_reviewsDf['ReviewText'].str.strip()
    customer_reviewsDf = customer_reviewsDf.drop_duplicates()

    customersDf['Gender'] = customersDf['Gender'].str.capitalize()
    customersDf['Age'] = customersDf['Age'].clip(lower=18, upper=100)
    customersDf = customersDf.drop_duplicates(subset=['CustomerID'])

    engagement_dataDf['ContentType'] = engagement_dataDf['ContentType'].str.upper()
    engagement_dataDf[['Views', 'Clicks']] = engagement_dataDf['ViewsClicksCombined'].str.split('-', expand=True).astype(int)
    engagement_dataDf = engagement_dataDf.drop(columns=['ViewsClicksCombined'])
    engagement_dataDf = engagement_dataDf.drop_duplicates()

    geographyDf = geographyDf.drop_duplicates()

    productsDf = productsDf[productsDf['Price'] > 0]
    productsDf = productsDf.drop_duplicates()

    # Create database and tables
    engine = create_engine("mysql+mysqlconnector://root:456123@localhost")

    with engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS ShopEasy"))

    engine = create_engine("mysql+mysqlconnector://root:456123@localhost/ShopEasy")

    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='456123',
        database='ShopEasy'
    )
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS customer_journey(
        JourneyID INT PRIMARY KEY,
        CustomerID INT,
        ProductID INT,
        VisitDate DATE,
        Stage VARCHAR(50),
        Action VARCHAR(50),
        Duration FLOAT
    );""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS customer_reviews(
        ReviewID INT PRIMARY KEY,
        CustomerID INT,
        ProductID INT,
        ReviewDate DATE,
        Rating INT,
        ReviewText VARCHAR(255)
    );""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS customers(
        CustomerID INT PRIMARY KEY,
        CustomerName VARCHAR(255),
        Email VARCHAR(255),
        Gender VARCHAR(10),
        Age INT,
        GeographyID INT
    );""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS engagement_data(
        EngagementID INT PRIMARY KEY,
        ContentID INT,
        ContentType VARCHAR(50),
        Likes INT,
        EngagementDate DATE,
        CampaignID INT,
        ProductID INT,
        Views INT,
        Clicks INT
    );""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS geography(
        GeographyID INT PRIMARY KEY,
        Country VARCHAR(50),
        City VARCHAR(50)
    );""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS products(
        ProductID INT PRIMARY KEY,
        ProductName VARCHAR(255),
        Category VARCHAR(50),
        Price DECIMAL(10, 2)
    );""")

    conn.commit()

    # Insert data into tables
    dfs = {
        "customer_journey": customer_journeyDf,
        "customer_reviews": customer_reviewsDf,
        "customers": customersDf,
        "engagement_data": engagement_dataDf,
        "geography": geographyDf,
        "products": productsDf
    }

    def insert_data(df, table_name, engine):
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)

    for table_name, df in dfs.items():
        try:
            insert_data(df, table_name, engine)
            print(f"Data inserted successfully into {table_name}")
        except Exception as e:
            print(f"Error inserting data into {table_name}: {e}")

    conn.commit()

    print("Database & Tables created, and Data insertion completed successfully!\n")
    print("Rows inserted:\n"
          f"- customer_journey: {len(customer_journeyDf)}\n"
          f"- customer_reviews: {len(customer_reviewsDf)}\n"
          f"- customers: {len(customersDf)}\n"
          f"- engagement_data: {len(engagement_dataDf)}\n"
          f"- geography: {len(geographyDf)}\n"
          f"- products: {len(productsDf)}")

except Exception as e:
    print(f"An error occurred: {e}")

input("Press Enter to exit...")
