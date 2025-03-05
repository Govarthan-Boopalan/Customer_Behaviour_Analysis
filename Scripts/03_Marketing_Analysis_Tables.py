


import os
import datetime
import mysql.connector
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    HRFlowable  # Added for a nice horizontal rule on the title page
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_pdf_report():
    try:
        # ========= MySQL Connection =========
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="456123",
            database="ShopEasy"
        )
        cursor = conn.cursor()

        # ========= Output Directory Setup =========
        output_dir = "../results"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "Marketing_Analysis_SQL__Table.pdf")

        # ========= PDF Document Setup =========
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=70,
            bottomMargin=60
        )
        elements = []
        styles = getSampleStyleSheet()

        # ========= Custom Styles =========
        # Adjust ReportTitle to be larger for a standout main title.
        styles.add(ParagraphStyle(
            name="ReportTitle",
            fontSize=36,
            leading=42,
            alignment=1,  # Centered
            spaceAfter=14,
            fontName="Helvetica-Bold"
        ))
        
        styles.add(ParagraphStyle(
            name="ReportSubtitle",
            fontSize=22,
            leading=26,
            alignment=1,  # Centered
            spaceAfter=40,
            fontName="Helvetica"
        ))
        
        # Date and Reporter styles remain as before.
        date_style = ParagraphStyle(
            name="DateStyle",
            fontSize=12,
            alignment=0  # Left aligned
        )
        reporter_style = ParagraphStyle(
            name="ReporterStyle",
            fontSize=12,
            alignment=2  # Right aligned
        )
        
        footnote_style = ParagraphStyle(
            name="Footnote",
            fontSize=8,
            leading=10,
            alignment=1,
            textColor=colors.grey
        )
        
        # ========= Page 1: Title Page =========
        # Add extra vertical spacing to center the content more elegantly
        elements.append(Spacer(1, 100))
        
        # Main Title and Subtitle (centered and styled)
        elements.append(Paragraph("ShopEasy", styles["ReportTitle"]))
        elements.append(Paragraph("Marketing Analysis", styles["ReportSubtitle"]))
        
        # Add a horizontal rule to visually separate title from footer details
        elements.append(HRFlowable(width="50%", thickness=1, color=colors.darkgrey, spaceBefore=10, spaceAfter=10))
        
        # Spacer to move footer details to lower half of the page
        elements.append(Spacer(1, 100))
        
        # Date and Reporter in a 2-column table
        col_widths = [doc.width/2, doc.width/2]
        footer_table = Table([
            [
                Paragraph(datetime.datetime.now().strftime("%B %d, %Y"), date_style),
                Paragraph("Analytics Team", reporter_style)
            ]
        ], colWidths=col_widths)
        elements.append(footer_table)
        elements.append(Spacer(1, 30))

        # Footnote at the bottom of the title page
        footnote_text = (
            "Tools used: Python, mysql-connector, pandas, ReportLab | "
            "SQL tables generated through an ETL process from customer journey data, "
            "engagement metrics, and geographic information."
        )
        elements.append(Paragraph(footnote_text, footnote_style))
        elements.append(PageBreak())

        # ========= Page 2: Underperforming Products + Demographic Performance =========
        # Underperforming Products: Query and Description.
        cursor.execute("""
            SELECT ProductName, AvgRating, PurchaseCount 
            FROM (
                SELECT p.ProductName, AVG(cr.Rating) AS AvgRating, COUNT(cj.JourneyID) AS PurchaseCount
                FROM products p
                LEFT JOIN customer_reviews cr ON p.ProductID = cr.ProductID
                LEFT JOIN customer_journey cj ON p.ProductID = cj.ProductID AND cj.Action = 'purchase'
                GROUP BY p.ProductName
                ORDER BY AvgRating ASC, PurchaseCount ASC
                LIMIT 5
            ) subquery;
        """)
        underperforming_data = cursor.fetchall()
        under_cols = [desc[0] for desc in cursor.description]
        
        # Demographic Performance: Query and Description.
        cursor.execute("""
            SELECT g.Country, g.City, COUNT(cj.JourneyID) AS Purchases, AVG(cr.Rating) AS AvgRating
            FROM geography g
            LEFT JOIN customers c ON g.GeographyID = c.GeographyID
            LEFT JOIN customer_journey cj ON c.CustomerID = cj.CustomerID AND cj.Action = 'purchase'
            LEFT JOIN customer_reviews cr ON cj.ProductID = cr.ProductID
            GROUP BY g.Country, g.City
            ORDER BY Purchases DESC, AvgRating DESC;
        """)
        demo_data = cursor.fetchall()
        demo_cols = [desc[0] for desc in cursor.description]

        # Page 2 header
        elements.append(Paragraph("Product & Demographic Analysis", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        
        # Underperforming Products section
        elements.append(Paragraph("Top 5 Underperforming Products", styles["Heading3"]))
        under_explanation = Paragraph(
            "This table represents the top 5 products with the lowest average ratings and purchase counts. "
            "A low average rating indicates customer dissatisfaction, while a low purchase count suggests "
            "poor market performance. Use these numbers to identify potential issues in product quality or promotion.",
            styles["BodyText"]
        )
        elements.append(under_explanation)
        elements.append(Spacer(1, 12))
        elements.append(create_table(underperforming_data, under_cols))
        elements.append(Spacer(1, 24))
        
        # Demographic Performance section
        elements.append(Paragraph("Marketing Performance Demographically", styles["Heading3"]))
        demo_explanation = Paragraph(
            "This table showcases how marketing efforts perform across different regions. "
            "It breaks down purchases and average customer ratings by country and city, "
            "providing insight into potential geographic trends. Use this data to tailor localized strategies.",
            styles["BodyText"]
        )
        elements.append(demo_explanation)
        elements.append(Spacer(1, 12))
        elements.append(create_table(demo_data, demo_cols))
        elements.append(PageBreak())

        # ========= Page 3: Badly Marketed Products =========
        cursor.execute("""
            SELECT p.ProductName, SUM(e.Clicks) AS TotalClicks, COUNT(cj.JourneyID) AS Purchases
            FROM products p
            LEFT JOIN engagement_data e ON p.ProductID = e.ProductID
            LEFT JOIN customer_journey cj ON p.ProductID = cj.ProductID AND cj.Action = 'purchase'
            GROUP BY p.ProductName
            HAVING TotalClicks > 0 AND Purchases < 0.1 * TotalClicks
            ORDER BY Purchases ASC, TotalClicks DESC;
        """)
        bad_mkt_data = cursor.fetchall()
        bad_mkt_cols = [desc[0] for desc in cursor.description]

        elements.append(Paragraph("Poorly Converting Products", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        bad_mkt_explanation = Paragraph(
            "This table highlights products with high online engagement (clicks) but low conversion (purchases). "
            "Such a gap often indicates issues like misleading advertising, poor product information, or barriers "
            "in the buying process. Review these figures to pinpoint where marketing efforts may need improvement.",
            styles["BodyText"]
        )
        elements.append(bad_mkt_explanation)
        elements.append(Spacer(1, 12))
        elements.append(create_table(bad_mkt_data, bad_mkt_cols))
        elements.append(PageBreak())

        # ========= Page 4: Marketing Channels Analysis =========
        # Best Channels
        cursor.execute("""
            SELECT ContentType, AVG(Views) AS AvgViews, AVG(Clicks) AS AvgClicks, COUNT(cj.JourneyID) AS Purchases
            FROM engagement_data e
            LEFT JOIN customer_journey cj ON e.ProductID = cj.ProductID AND cj.Action = 'purchase'
            GROUP BY e.ContentType
            ORDER BY Purchases DESC;
        """)
        best_chnl_data = cursor.fetchall()
        
        # Bad Channels
        cursor.execute("""
            SELECT ContentType, AVG(Views) AS AvgViews, AVG(Clicks) AS AvgClicks, COUNT(cj.JourneyID) AS Purchases
            FROM engagement_data e
            LEFT JOIN customer_journey cj ON e.ProductID = cj.ProductID AND cj.Action = 'purchase'
            GROUP BY e.ContentType
            HAVING (COUNT(cj.JourneyID)/AVG(Clicks)) < 0.05
            ORDER BY (COUNT(cj.JourneyID)/AVG(Clicks)) ASC;
        """)
        bad_chnl_data = cursor.fetchall()

        elements.append(Paragraph("Marketing Channel Effectiveness", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        
        # Best Channels section and explanation
        elements.append(Paragraph("Top Performing Channels", styles["Heading3"]))
        best_chnl_explanation = Paragraph(
            "This table displays average views, clicks, and purchase counts by channel. "
            "Higher purchase numbers typically indicate a more effective channel. "
            "Review these metrics to focus on channels that yield the best customer engagement.",
            styles["BodyText"]
        )
        elements.append(best_chnl_explanation)
        elements.append(Spacer(1, 12))
        elements.append(create_table(best_chnl_data, ["Channel", "Avg Views", "Avg Clicks", "Purchases"]))
        elements.append(Spacer(1, 24))
        
        # Underperforming Channels section and explanation
        elements.append(Paragraph("Underperforming Channels", styles["Heading3"]))
        bad_chnl_explanation = Paragraph(
            "This table identifies channels with low conversion rates relative to clicks. "
            "Such a ratio may indicate a need to review content quality or targeting strategies. "
            "Interpreting these metrics can help refine overall marketing efforts.",
            styles["BodyText"]
        )
        elements.append(bad_chnl_explanation)
        elements.append(Spacer(1, 12))
        elements.append(create_table(bad_chnl_data, ["Channel", "Avg Views", "Avg Clicks", "Purchases"]))
        
        # ========= Build PDF =========
        doc.build(elements)
        cursor.close()
        conn.close()
        print(f"PDF report generated at: {output_path}")

    except Exception as e:
        print(f"Error: {str(e)}")
        try:
            cursor.close()
            conn.close()
        except:
            pass

def create_table(data, columns):
    """Helper function to create styled tables"""
    df = pd.DataFrame(data, columns=columns)
    table_data = [df.columns.tolist()] + df.values.tolist()
    
    table = Table(table_data, hAlign="CENTER")
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F81BD')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F7F7F7')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,1), (-1,-1), 8),
    ])
    table.setStyle(table_style)
    return table

if __name__ == "__main__":
    create_pdf_report()

