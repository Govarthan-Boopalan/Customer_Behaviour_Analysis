import pandas as pd
import os
from sqlalchemy import create_engine
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from datetime import datetime

def create_pdf_report():
    try:
        # ---------- SQLAlchemy Connection ----------
        DB_URI = "mysql+mysqlconnector://root:456123@localhost/ShopEasy"
        engine = create_engine(DB_URI)

        # ---------- Output Directory Setup ----------
        output_dir = "../results"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "Cx_Experience_Analysis_SQL_Tables.pdf")

        # ---------- PDF Setup ----------
        doc = SimpleDocTemplate(output_path, pagesize=letter)
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
            textColor=colors.gray
        )
        
        # ========= Page 1: Title Page =========
        # Add extra vertical spacing to center the content more elegantly
        elements.append(Spacer(1, 100))
        
        # Main Title and Subtitle (centered and styled)
        elements.append(Paragraph("ShopEasy", styles["ReportTitle"]))
        elements.append(Paragraph("Customer Experience Analysis", styles["ReportSubtitle"]))
        
        # Add a horizontal rule to visually separate title from footer details
        elements.append(HRFlowable(width="50%", thickness=2, color=colors.darkgrey, spaceBefore=10, spaceAfter=10))
        
        # Spacer to move footer details to lower half of the page
        elements.append(Spacer(1, 100))
        
        # Date and Reporter in a 2-column table
        col_widths = [doc.width/2, doc.width/2]
        footer_table = Table([
            [
                Paragraph(datetime.now().strftime("%B %d, %Y"), date_style),
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


        # ---------- Define Queries and Enhanced Table Descriptions ----------
        queries = {
            "negative_reviews": """
                SELECT cr.ReviewID, cr.ProductID, p.ProductName, cr.ReviewText, cr.Rating 
                FROM customer_reviews cr 
                JOIN products p ON cr.ProductID = p.ProductID 
                WHERE cr.Rating <= 2;
            """,
            "lowest_rated_products": """
                SELECT cr.ProductID, p.ProductName, AVG(cr.Rating) AS AvgRating, COUNT(*) AS ReviewCount 
                FROM customer_reviews cr 
                JOIN products p ON cr.ProductID = p.ProductID 
                GROUP BY cr.ProductID, p.ProductName 
                ORDER BY AvgRating ASC LIMIT 5;
            """,
            "low_repeat_customers": """
                WITH customer_retention AS (
                    SELECT CustomerID, COUNT(DISTINCT VisitDate) AS Visits, 
                           SUM(CASE WHEN Stage = 'Checkout' AND Action = 'Purchase' THEN 1 ELSE 0 END) AS Purchases 
                    FROM customer_journey 
                    GROUP BY CustomerID)
                SELECT COUNT(DISTINCT CustomerID) AS Total_Customers, 
                       SUM(CASE WHEN Visits > 1 THEN 1 ELSE 0 END) AS Retained_Customers, 
                       ROUND((SUM(CASE WHEN Visits > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT CustomerID)), 2) AS Retention_Rate 
                FROM customer_retention;
            """,
            "common_complaints": """
                SELECT cr.ReviewText, p.ProductName, COUNT(*) AS Frequency 
                FROM customer_reviews cr 
                JOIN products p ON cr.ProductID = p.ProductID 
                WHERE cr.Rating <= 2 
                GROUP BY cr.ReviewText, p.ProductName 
                ORDER BY Frequency DESC LIMIT 10;
            """
        }

        table_descriptions = {
            "lowest_rated_products": (
                "This table lists the products that consistently receive the lowest ratings. "
                "It displays the Product ID, Product Name, Average Rating, and Review Count. "
                "Examine the average ratings to determine which products may require quality improvement or further evaluation."
            ),
            "negative_reviews": (
                "This table presents individual customer reviews with ratings 2 or below, indicating dissatisfaction. "
                "It includes Review ID, Product ID, Product Name, Review Text, and Rating. "
                "Carefully analyze these negative reviews to identify recurring issues or problematic products."
            ),
            "low_repeat_customers": (
                "This table summarizes customer retention metrics by counting each customer's visit frequency and purchase actions. "
                "It shows the total number of customers, the count of those returning for a second visit, and the calculated retention rate. "
                "Use these metrics to gauge customer loyalty and identify potential areas for improving repeat business."
            ),
            "common_complaints": (
                "This table aggregates frequently mentioned complaints from customer reviews with low ratings. "
                "It groups similar complaint narratives along with their frequency and the related product names. "
                "Review these common complaints to pinpoint recurring issues that may require immediate attention."
            )
        }

        # ---------- Page 2: Lowest Rated Products and Negative Reviews ----------
        page2_tables = ["lowest_rated_products", "negative_reviews"]
        for key in page2_tables:
            with engine.connect() as connection:
                df = pd.read_sql(queries[key], connection)
            # Convert the dataframe to a list format that ReportLab's Table can use.
            data = [df.columns.tolist()] + df.values.tolist()
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#DCE6F1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            heading_text = key.replace("_", " ").title()
            explanation = Paragraph(table_descriptions[key], styles["BodyText"])
            elements.append(KeepTogether([
                Paragraph(heading_text, styles["Heading2"]),
                Spacer(1, 4),
                explanation,
                Spacer(1, 4),
                table,
                Spacer(1, 8)
            ]))
        elements.append(PageBreak())

        # ---------- Page 3: Low Repeat Customers, Common Complaints and Footnote ----------
        page3_tables = ["low_repeat_customers", "common_complaints"]
        for key in page3_tables:
            with engine.connect() as connection:
                df = pd.read_sql(queries[key], connection)
            data = [df.columns.tolist()] + df.values.tolist()
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#DCE6F1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            heading_text = key.replace("_", " ").title()
            explanation = Paragraph(table_descriptions[key], styles["BodyText"])
            elements.append(KeepTogether([
                Paragraph(heading_text, styles["Heading2"]),
                Spacer(1, 4),
                explanation,
                Spacer(1, 4),
                table,
                Spacer(1, 8)
            ]))

        # Add footnote at the bottom of Page 3.
        footnote_text = (
            ">> This report was generated using ReportLab components (SimpleDocTemplate, Table, TableStyle, "
            "Paragraph, Spacer, KeepTogether) for layout, with data processed by pandas and database connectivity "
            "through SQLAlchemy. The SQL tables were derived using specific query filters to capture valuable trends "
            "and actionable insights from the ShopEasy database."
        )
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(footnote_text, styles["Normal"]))

        # ---------- Build the PDF Document ----------
        doc.build(elements)
        engine.dispose()
        print("PDF report generated successfully.")
    except Exception as e:
        print(f"Error: {str(e)}")
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    create_pdf_report()
