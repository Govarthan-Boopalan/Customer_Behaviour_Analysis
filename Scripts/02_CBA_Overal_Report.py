# -*- coding: utf-8 -*-
import pandas as pd
from sqlalchemy import create_engine
from textblob import TextBlob
from datetime import datetime
from reportlab.lib.colors import HexColor  # for custom colors if needed

# ReportLab imports for PDF generation
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    PageBreak,
    Paragraph,
    Spacer,
    KeepTogether
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Connect to MySQL Database
engine = create_engine('mysql+mysqlconnector://root:456123@localhost/ShopEasy')


def analyze_customer_trends():
    """Analyze product popularity, regional sales, and retention"""
    product_query = """
    SELECT p.ProductName, COUNT(cj.JourneyID) AS Total_Interactions
    FROM customer_journey cj
    JOIN products p ON cj.ProductID = p.ProductID
    GROUP BY p.ProductName
    ORDER BY Total_Interactions DESC
    LIMIT 5;
    """
    top_products = pd.read_sql(product_query, engine)
    
    region_query = """
    SELECT g.Country, COUNT(cj.JourneyID) AS Total_Purchases
    FROM customer_journey cj
    JOIN customers c ON cj.CustomerID = c.CustomerID
    JOIN geography g ON c.GeographyID = g.GeographyID
    WHERE cj.Action = 'Purchase'
    GROUP BY g.Country
    ORDER BY Total_Purchases DESC
    LIMIT 5;
    """
    top_regions = pd.read_sql(region_query, engine)
    
    retention_query = """
    WITH retention AS (
        SELECT CustomerID, COUNT(DISTINCT VisitDate) AS Visits
        FROM customer_journey
        GROUP BY CustomerID
    )
    SELECT CASE WHEN Visits > 1 THEN 'Retained' ELSE 'One-Time' END AS Customer_Type,
           COUNT(*) AS Count
    FROM retention
    GROUP BY Customer_Type;
    """
    retention = pd.read_sql(retention_query, engine)
    
    return top_products, top_regions, retention


def analyze_segment_performance():
    """Analyze demographic performance"""
    demographics_query = """
    WITH customer_conversion_age AS (
        SELECT CASE 
                 WHEN c.Age < 30 THEN '<30'
                 WHEN c.Age BETWEEN 30 AND 45 THEN '30-45'
                 ELSE '>45'
               END AS Age_Range,
               COUNT(DISTINCT cj.CustomerID) AS Total_Customers,
               SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.Action = 'Purchase' THEN 1 ELSE 0 END) AS Total_Purchases,
               ROUND((SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.Action = 'Purchase' THEN 1 ELSE 0 END) * 100.0)
               / COUNT(DISTINCT cj.CustomerID), 2) AS Conversion_Rate
        FROM customer_journey cj
        JOIN customers c ON cj.CustomerID = c.CustomerID
        GROUP BY Age_Range
    )
    SELECT 'Age Range' AS Group_By, Age_Range AS Group_Value, Total_Customers, Total_Purchases, Conversion_Rate
    FROM customer_conversion_age
    UNION ALL
    SELECT 'Gender' AS Group_By, Gender AS Group_Value,
           COUNT(DISTINCT cj.CustomerID) AS Total_Customers,
           SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.Action = 'Purchase' THEN 1 ELSE 0 END) AS Total_Purchases,
           ROUND((SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.Action = 'Purchase' THEN 1 ELSE 0 END) * 100.0)
           / COUNT(DISTINCT cj.CustomerID), 2) AS Conversion_Rate
    FROM customer_journey cj
    JOIN customers c ON cj.CustomerID = c.CustomerID
    GROUP BY Gender
    UNION ALL
    SELECT 'Country' AS Group_By, g.Country AS Group_Value,
           COUNT(DISTINCT cj.CustomerID) AS Total_Customers,
           SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.Action = 'Purchase' THEN 1 ELSE 0 END) AS Total_Purchases,
           ROUND((SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.Action = 'Purchase' THEN 1 ELSE 0 END) * 100.0)
           / COUNT(DISTINCT cj.CustomerID), 2) AS Conversion_Rate
    FROM customer_journey cj
    JOIN customers c ON cj.CustomerID = c.CustomerID
    JOIN geography g ON c.GeographyID = g.GeographyID
    GROUP BY g.Country;
    """
    return pd.read_sql(demographics_query, engine)


def analyze_purchase_drivers():
    """Analyze product and engagement conversions"""
    product_query = """
    SELECT p.ProductName,
           ROUND(AVG(p.Price), 2) AS Avg_Price,
           COUNT(DISTINCT cj.CustomerID) AS Unique_Customers,
           SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.Action = 'Purchase' THEN 1 ELSE 0 END) AS Total_Purchases,
           ROUND(SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.Action = 'Purchase' THEN 1 ELSE 0 END) * 100.0 
           / COUNT(DISTINCT cj.CustomerID), 2) AS Conversion_Rate
    FROM customer_journey cj
    JOIN products p ON cj.ProductID = p.ProductID
    GROUP BY p.ProductName
    ORDER BY Conversion_Rate DESC;
    """
    product_conversions = pd.read_sql(product_query, engine)
    
    engagement_query = """
    SELECT e.ContentType,
           COUNT(DISTINCT e.EngagementID) AS Total_Engagements,
           SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.Action = 'Purchase' THEN 1 ELSE 0 END) AS Total_Purchases,
           ROUND(SUM(CASE WHEN cj.Stage = 'Checkout' AND cj.Action = 'Purchase' THEN 1 ELSE 0 END) * 100.0 
           / COUNT(DISTINCT e.EngagementID), 2) AS Conversion_Rate
    FROM engagement_data e
    JOIN customer_journey cj ON e.ProductID = cj.ProductID
    GROUP BY e.ContentType
    ORDER BY Conversion_Rate DESC;
    """
    engagement_conversions = pd.read_sql(engagement_query, engine)
    
    return product_conversions, engagement_conversions


def analyze_reviews():
    """Analyze customer reviews for sentiment"""
    reviews_query = """
    SELECT r.ProductID,
           p.ProductName,
           r.ReviewText,
           r.Rating,
           CASE WHEN r.Rating > 3 THEN 1
                WHEN r.Rating = 3 THEN 0
                ELSE -1
           END AS Sentiment
    FROM customer_reviews r
    JOIN products p ON r.ProductID = p.ProductID;
    """
    return pd.read_sql(reviews_query, engine)


def df_to_table(df, col_widths=None):
    """
    Convert a pandas DataFrame to a ReportLab Table with visible borders
    and using a uniform very light background for data rows.
    """
    data = [df.columns.tolist()] + df.values.tolist()
    t = Table(data, colWidths=col_widths)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.aliceblue),  # Header background
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke)
    ])
    t.setStyle(style)
    return t


def series_to_table(series, title=""):
    """
    Convert a pandas Series into a two-column table.
    """
    df = series.reset_index()
    df.columns = ['Category', 'Percentage']
    return df_to_table(df)


def generate_strategic_recommendations(product_conversions, engagement_conversions, reviews, demographics):
    """
    Automatically generate strategic recommendations based on the analysis.
    """
    recommendations = []
    if not product_conversions.empty:
        top_products = product_conversions.sort_values(by="Conversion_Rate", ascending=False).head(3)
        product_names = ", ".join(top_products["ProductName"].astype(str))
        recommendations.append(f"Focus marketing on top converting products: {product_names}.")
    if not engagement_conversions.empty:
        top_content = engagement_conversions.sort_values(by="Conversion_Rate", ascending=False).iloc[0]["ContentType"]
        recommendations.append(f"Prioritize {top_content} content, as it shows the highest engagement conversion.")
    if not demographics.empty:
        age_rows = demographics[demographics["Group_By"] == "Age Range"]
        if not age_rows.empty:
            top_age = age_rows.sort_values(by="Conversion_Rate", ascending=False).iloc[0]["Group_Value"]
            recommendations.append(f"Target customers in the age group {top_age}, who demonstrate the highest conversion rate.")
    neg_reviews = reviews[reviews["Sentiment"] < 0]
    if not neg_reviews.empty:
        negative_products = neg_reviews["ProductName"].unique()
        recommendations.append(f"Address negative reviews for products: {', '.join(negative_products)}.")
    recommendations.append("Improve the checkout process to reduce high drop-off rates and increase conversions.")
    return recommendations


def generate_pdf_report():
    # Collect all data.
    top_products, top_regions, retention = analyze_customer_trends()
    demographics = analyze_segment_performance()
    product_conversions, engagement_conversions = analyze_purchase_drivers()
    reviews = analyze_reviews()
    
    sentiment_counts = reviews['Sentiment'].apply(
        lambda x: 'Positive' if x > 0 else ('Neutral' if x == 0 else 'Negative')
    ).value_counts(normalize=True) * 100
    sentiment_counts = sentiment_counts.sort_index()  # consistent order
    
    pdf_path = "../results/ShopEasy_Final_Report.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    header_style = styles["Heading1"]
    subheader_style = styles["Heading3"]
    normal_style = styles["Normal"]
    
    # Custom styles:
    subtopic_style = ParagraphStyle(
        'Subtopic',
        parent=normal_style,
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.teal,
        spaceAfter=6,
        leading=14
    )
    # Comments: dark grey (for more readability)
    comment_style = ParagraphStyle(
        'Comment',
        parent=normal_style,
        fontName='Helvetica-Oblique',
        fontSize=12,
        textColor=colors.darkgrey,
        spaceAfter=10,
        leading=14
    )
    # Quote in italics and dark grey.
    quote_style = ParagraphStyle(
        'QuoteStyle',
        parent=normal_style,
        alignment=1,
        fontSize=16,
        textColor=colors.darkgrey,
        leading=20,
        fontName='Helvetica-Oblique'
    )
    # Group titles: left aligned and navy blue.
    group_title_style = ParagraphStyle(
        'GroupTitle',
        parent=styles["Heading2"],
        alignment=0,
        fontSize=16,
        textColor=HexColor("#000080"),
        spaceAfter=12
    )
    # Footnote: increased visibility - dark grey.
    footnote_style = ParagraphStyle(
        'Footnote',
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.darkgrey,
        spaceBefore=20
    )
    # Title Page styles.
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles["Heading1"],
        alignment=1,
        fontSize=36,
        textColor=colors.darkblue
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles["Heading2"],
        alignment=1,
        fontSize=20,
        textColor=colors.teal
    )
    normal_center = ParagraphStyle(
        'NormalCenter',
        parent=normal_style,
        alignment=1
    )
    
    story = []
    
    # ----- Page 1: Title Page -----
    title_page = []
    title_page.append(Spacer(1, 150))
    title_page.append(Paragraph("ShopEasy", title_style))
    title_page.append(Spacer(1, 20))
    title_page.append(Paragraph("Customer Behavior Analysis Report", subtitle_style))
    title_page.append(Spacer(1, 20))
    today_date = datetime.today().strftime("%B %d, %Y")
    title_page.append(Paragraph("Date: " + today_date, normal_center))
    title_page.append(Paragraph("Reporter: Govarthan", normal_center))
    title_page.append(Spacer(1, 50))
    title_page.append(Paragraph('“Understanding your customers is key to elevating your business strategy.”', quote_style))
    title_page.append(Spacer(1, 100))
    story.extend(title_page)
    story.append(PageBreak())
    
    # ----- Page 2: Customer Trends -----
    story.append(Paragraph("A: Customer Trends", group_title_style))
    block1 = [
        Paragraph("Top 5 Products by Engagement:", subtopic_style),
        Spacer(1, 6),
        df_to_table(top_products),
        Spacer(1, 6),
        Paragraph("💡 This table displays the top 5 products generating the highest customer interactions.", comment_style),
        Spacer(1, 12)
    ]
    block2 = [
        Paragraph("Top 5 Regions by Sales:", subtopic_style),
        Spacer(1, 6),
        df_to_table(top_regions),
        Spacer(1, 6),
        Paragraph("💡 This table highlights regions with the highest purchase volumes.", comment_style),
        Spacer(1, 12)
    ]
    block3 = [
        Paragraph("Customer Retention:", subtopic_style),
        Spacer(1, 6),
        df_to_table(retention),
        Spacer(1, 6),
        Paragraph("💡 This table summarizes customer retention by distinguishing between retained and one-time visitors.", comment_style),
        Spacer(1, 12)
    ]
    story.append(KeepTogether(block1))
    story.append(KeepTogether(block2))
    story.append(KeepTogether(block3))
    story.append(PageBreak())
    
    # ----- Page 3: Segment Performance & Customer Sentiment Analysis -----
    story.append(Paragraph("B: Segment Performance & Customer Sentiment Analysis", group_title_style))
    block4 = [
        Paragraph("Conversion Rates by Demographic:", subtopic_style),
        Spacer(1, 6),
        df_to_table(demographics),
        Spacer(1, 6),
        Paragraph("💡 This table breaks down conversion metrics by age, gender, and country.", comment_style),
        Spacer(1, 12)
    ]
    block7 = [
        Paragraph("Sentiment Distribution (%):", subtopic_style),
        Spacer(1, 6),
        series_to_table(sentiment_counts),
        Spacer(1, 6),
        Paragraph("💡 This table shows the percentage breakdown of customer sentiment.", comment_style),
        Spacer(1, 12)
    ]
    story.append(KeepTogether(block4))
    story.append(KeepTogether(block7))
    story.append(PageBreak())
    
    # ----- Page 4: Key Purchase Drivers & Strategic Recommendations -----
    story.append(Paragraph("C: Key Purchase Drivers & Strategic Recommendations", group_title_style))
    block5 = [
        Paragraph("Top Performing Products:", subtopic_style),
        Spacer(1, 6),
        df_to_table(product_conversions.head(5)),
        Spacer(1, 6),
        Paragraph("💡 This table lists the top products by conversion rate.", comment_style),
        Spacer(1, 12)
    ]
    block6 = [
        Paragraph("Engagement Effectiveness:", subtopic_style),
        Spacer(1, 6),
        df_to_table(engagement_conversions),
        Spacer(1, 6),
        Paragraph("💡 This table displays conversion rates for various content types.", comment_style),
        Spacer(1, 12)
    ]
    recommendations_block = []
    recommendations_block.append(Paragraph("Strategic Recommendations:", group_title_style))
    recommendations_block.append(Spacer(1, 6))
    auto_recommendations = generate_strategic_recommendations(product_conversions, engagement_conversions, reviews, demographics)
    for rec in auto_recommendations:
        recommendations_block.append(Paragraph("👉 " + rec, normal_style))
        recommendations_block.append(Spacer(1, 4))
    
    story.append(KeepTogether(block5))
    story.append(KeepTogether(block6))
    story.append(KeepTogether(recommendations_block))
    
    # Add footnote with technical details.
    footnote_text = (
        "🔧 Technical Details: This analysis is generated using SQL queries via SQLAlchemy, "
        "data manipulation with pandas, sentiment analysis with TextBlob, and rendered using ReportLab. "
        "All conversion metrics are computed directly from our customer journey data."
    )
    story.append(Paragraph(footnote_text, footnote_style))
    
    doc.build(story)
    print(f"PDF report generated successfully as {pdf_path}")


if __name__ == "__main__":
    generate_pdf_report()
