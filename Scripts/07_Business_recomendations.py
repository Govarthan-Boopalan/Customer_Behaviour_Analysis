# -*- coding: utf-8 -*-
import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from sqlalchemy import create_engine

# Configure output directory (CHANGE THIS TO YOUR PREFERRED LOCATION)
OUTPUT_DIR = "../results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Database connection
engine = create_engine('mysql+mysqlconnector://root:456123@localhost/ShopEasy')

# Custom styles
styles = getSampleStyleSheet()
style_heading = ParagraphStyle(
    'Heading1',
    parent=styles['Heading1'],
    fontSize=16,
    leading=20,
    spaceAfter=12,
    textColor=colors.darkblue
)
style_body = styles['BodyText']
style_recommendation = ParagraphStyle(
    'Recommendation',
    parent=styles['BodyText'],
    bulletIndent=12,
    spaceBefore=6,
    spaceAfter=6
)
footnote_style = ParagraphStyle(
    'Footnote',
    parent=styles['BodyText'],
    fontSize=8,
    textColor=colors.grey
)

def get_dynamic_recommendations():
    """
    Generate dynamic recommendations by querying the database.

    The recommendations are built using insights on:
      1. Product Performance
      2. Demographic Targeting
      3. Regional Performance
      4. Marketing ROI
      5. Discount Candidates

    Each recommendation comes from live insights and is later complemented by
    detailed business analysis.
    """
    recommendations = []
    
    # 1. Product Performance Analysis
    product_query = """
    SELECT p.ProductName, 
           ROUND(
               (SUM(CASE WHEN cj.Action = 'purchase' THEN 1 ELSE 0 END) * 100.0) 
               / COUNT(cj.JourneyID), 
               2
           ) AS conversion_rate
    FROM customer_journey cj
    JOIN products p ON cj.ProductID = p.ProductID
    GROUP BY p.ProductName
    ORDER BY conversion_rate DESC
    LIMIT 1;
    """
    top_product = pd.read_sql(product_query, engine).iloc[0]
    recommendations.append(
        f"Promote **{top_product['ProductName']}** as the flagship product (Conversion rate: {top_product['conversion_rate']}%)."
    )

    # 2. Demographic Targeting
    demo_query = """
    SELECT 
        CASE WHEN Age < 30 THEN '18-29'
             WHEN Age BETWEEN 30 AND 45 THEN '30-45'
             ELSE '46+' END AS age_group,
        Gender,
        g.Country,
        ROUND(
            (SUM(CASE WHEN Action = 'purchase' THEN 1 ELSE 0 END) * 100.0) 
            / COUNT(DISTINCT cj.CustomerID), 
            2
        ) AS conversion_rate
    FROM customer_journey cj
    JOIN customers c ON cj.CustomerID = c.CustomerID
    JOIN geography g ON c.GeographyID = g.GeographyID
    GROUP BY age_group, Gender, Country
    ORDER BY conversion_rate DESC
    LIMIT 1;
    """
    top_demo = pd.read_sql(demo_query, engine).iloc[0]
    recommendations.append(
        f"Focus marketing on **{top_demo['age_group']} {top_demo['Gender']}s** in **{top_demo['Country']}** (Conversion rate: {top_demo['conversion_rate']}%)."
    )

    # 3. Regional Performance
    region_query = """
    SELECT g.Country, p.ProductName, COUNT(*) AS sales
    FROM customer_journey cj
    JOIN customers c ON cj.CustomerID = c.CustomerID
    JOIN geography g ON c.GeographyID = g.GeographyID
    JOIN products p ON cj.ProductID = p.ProductID
    WHERE Action = 'purchase'
    GROUP BY g.Country, p.ProductName
    ORDER BY sales DESC
    LIMIT 1;
    """
    top_region = pd.read_sql(region_query, engine).iloc[0]
    recommendations.append(
        f"Prioritize **{top_region['ProductName']}** in **{top_region['Country']}** (Sales: {top_region['sales']} units)."
    )

    # 4. Marketing ROI
    roi_query = """
    SELECT ContentType,
           ROUND(
               (SUM(CASE WHEN cj.Action = 'purchase' THEN 1 ELSE 0 END) * 100.0) 
               / SUM(Clicks), 
               2
           ) AS conversion_rate
    FROM engagement_data e
    JOIN customer_journey cj ON e.ProductID = cj.ProductID
    GROUP BY ContentType
    ORDER BY conversion_rate DESC
    LIMIT 1;
    """
    top_channel = pd.read_sql(roi_query, engine).iloc[0]
    recommendations.append(
        f"Increase budget for **{top_channel['ContentType']}** campaigns (Conversion rate: {top_channel['conversion_rate']}%)."
    )

    # 5. Discount Candidates
    discount_query = """
    SELECT p.ProductName,
           AVG(Rating) AS avg_rating,
           COUNT(ReviewID) AS review_count
    FROM products p
    LEFT JOIN customer_reviews r ON p.ProductID = r.ProductID
    LEFT JOIN (
        SELECT ProductID 
        FROM customer_journey 
        WHERE Action = 'purchase'
        GROUP BY ProductID
        ORDER BY COUNT(*) DESC
        LIMIT 3
    ) AS top_products ON p.ProductID = top_products.ProductID
    WHERE top_products.ProductID IS NULL
    GROUP BY p.ProductName
    HAVING avg_rating < 3.5 AND review_count > 5
    ORDER BY avg_rating ASC
    LIMIT 1;
    """
    discount_candidate = pd.read_sql(discount_query, engine)
    if not discount_candidate.empty:
        rec = discount_candidate.iloc[0]
        recommendations.append(
            f"Introduce discounts for **{rec['ProductName']}** (Rating: {rec['avg_rating']}/5, Reviews: {rec['review_count']})."
        )
    else:
        recommendations.append("No discount candidates identified – maintain current pricing strategy.")

    return recommendations

def create_dynamic_pdf(recommendations):
    """
    Generate a PDF report with two pages:
    
      1. The first page contains the report title, immediate actionable insights integrated
         with detailed business analysis commentary, and a footnote (placed at the bottom) explaining the analysis methodology.
         
      2. The second page contains all supporting data analysis tables.
    """
    output_path = os.path.join(OUTPUT_DIR, "ShopEasy_Business_Recommendations.pdf")
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    
    # ----- Page 1: Title, Immediate Actions, Integrated Business Insights, and Footnote -----
    elements.append(Paragraph("ShopEasy Data-Driven Business Report", style_heading))
    elements.append(Spacer(1, 12))
    intro_text = (
        "This report merges critical insights from customer behavior, product performance, and marketing channel effectiveness. "
        "Each actionable item is complemented with analytic commentary to support strategic decisions and drive business growth."
    )
    elements.append(Paragraph(intro_text, style_body))
    elements.append(Spacer(1, 12))
    
    # Analysis commentary for each actionable insight
    analysis_comments = [
        "<b>Product Performance:</b> The flagship product's conversion rate is a strong indicator of product-market fit. "
        "Elevating its profile with targeted promotions can multiply revenue impact.",
        
        "<b>Demographic Insights:</b> The conversion trend within the specified age and gender segment suggests that personalized "
        "marketing and localized messaging can drive higher engagement.",
        
        "<b>Regional Dynamics:</b> Robust sales in the highlighted region indicate a promising market; "
        "local promotions and expansion into adjacent areas might be advantageous.",
        
        "<b>Marketing Channel Effectiveness:</b> The disciplined marketing channel delivers exceptional ROI. "
        "Increasing the budget here is likely to yield further conversion growth.",
        
        "<b>Pricing & Promotions:</b> Products with moderate ratings and high review counts could benefit from strategic discounts, "
        "improving customer perception while boosting sales."
    ]
    
    elements.append(Paragraph("Actionable Business Insights", style_heading))
    elements.append(Spacer(1, 12))
    for idx, (rec, comment) in enumerate(zip(recommendations, analysis_comments), 1):
        elements.append(Paragraph(f"Insight {idx}: {rec}", style_recommendation))
        elements.append(Paragraph(comment, style_body))
        elements.append(Spacer(1, 12))
    
    # Add a spacer to simulate filling the rest of the page (tweak height as needed)
    elements.append(Spacer(1, 100))
    
    # Add footnote to cover the empty space at the bottom of page 1
    footnote_text = (
        "Note: This analysis was performed by executing dynamic SQL queries against the ShopEasy database. "
        "Insights were derived from aggregating data from customer journeys, product performance metrics, and marketing engagement records."
    )
    elements.append(Paragraph(footnote_text, footnote_style))
    
    # Add a page break to begin page 2
    elements.append(PageBreak())
    
    # ----- Page 2: Supporting Data Analysis -----
    elements.append(Paragraph("Supporting Data Analysis", style_heading))
    elements.append(Spacer(1, 12))
    
    tables = [
        (
            "Top Converting Products", 
            """
            SELECT p.ProductName, 
                   COUNT(*) AS purchases,
                   ROUND(
                       (SUM(CASE WHEN Action = 'purchase' THEN 1 ELSE 0 END) * 100.0) 
                       / COUNT(*), 
                       2
                   ) AS conversion_rate
            FROM customer_journey cj
            JOIN products p ON cj.ProductID = p.ProductID
            GROUP BY p.ProductName
            ORDER BY conversion_rate DESC
            LIMIT 5;
            """,
            "This table displays the top converting products with total purchases and conversion rates, revealing which products drive sales."
        ),
        (
            "Demographic Performance", 
            """
            SELECT 
                CASE WHEN Age < 30 THEN '18-29'
                     WHEN Age BETWEEN 30 AND 45 THEN '30-45'
                     ELSE '46+' END AS age_group,
                Gender,
                Country,
                COUNT(*) AS purchases,
                ROUND(
                    (SUM(CASE WHEN Action = 'purchase' THEN 1 ELSE 0 END) * 100.0) 
                    / COUNT(DISTINCT CustomerID), 
                    2
                ) AS conversion_rate
            FROM customer_journey
            JOIN customers USING(CustomerID)
            JOIN geography USING(GeographyID)
            GROUP BY age_group, Gender, Country
            ORDER BY conversion_rate DESC
            LIMIT 5;
            """,
            "This table breaks down purchase behavior by demographics, helping to pinpoint segments with higher conversion rates."
        ),
        (
            "Marketing Channel ROI", 
            """
            SELECT ContentType,
                   SUM(Clicks) AS total_clicks,
                   SUM(CASE WHEN Action = 'purchase' THEN 1 ELSE 0 END) AS conversions,
                   ROUND(
                       (SUM(CASE WHEN Action = 'purchase' THEN 1 ELSE 0 END) * 100.0) 
                       / SUM(Clicks), 
                       2
                   ) AS conversion_rate
            FROM engagement_data
            JOIN customer_journey USING(ProductID)
            GROUP BY ContentType
            ORDER BY conversion_rate DESC;
            """,
            "This table compares clicks and conversions across marketing channels to guide budget allocation for improved ROI."
        )
    ]
    
    # Add each supporting data table along with its explanation
    for title, query, comment in tables:
        elements.append(Paragraph(title, style_heading))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"<i>{comment}</i>", styles['Italic']))
        elements.append(Spacer(1, 6))
        
        df = pd.read_sql(query, engine)
        if df.empty:
            elements.append(Paragraph("No data available.", style_body))
        else:
            data = [df.columns.tolist()] + df.values.tolist()
            table = Table(data, hAlign='CENTER')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        elements.append(Spacer(1, 12))
    
    # Build the PDF document without using page-callbacks
    doc.build(elements)
    print(f"PDF report generated at: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    # Generate dynamic recommendations from live insights
    recommendations = get_dynamic_recommendations()
    # Create the comprehensive PDF report featuring integrated actionable insights (with footnote on page 1)
    # and supporting data analysis on page 2.
    create_dynamic_pdf(recommendations)
