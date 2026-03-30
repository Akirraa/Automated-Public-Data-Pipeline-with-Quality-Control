from fpdf import FPDF
import os
import json
import logging
from datetime import datetime

class DataQualityReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Universal Auto-ETL Quality Report', border=0, new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_line_width(0.5)
        self.line(10, 22, 200, 22)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', border=0, new_x="RIGHT", new_y="TOP", align='C')

def generate_pdf_report(stats_path: str, output_path: str):
    """
    Generate a detailed PDF report from cleaning statistics.
    """
    try:
        if not os.path.exists(stats_path):
            logging.error(f"Stats file not found: {stats_path}. Baseline report will be empty.")
            return

        with open(stats_path, "r") as f:
            stats = json.load(f)

        pdf = DataQualityReport()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)

        # 1. Summary Section
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(200, 10, "1. Executive Summary", border=0, new_x="LMARGIN", new_y="NEXT", align='L')
        pdf.set_font("helvetica", '', 12)
        pdf.ln(5)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.multi_cell(0, 10, f"Analysis executed at {timestamp}. The dataset was processed through the automated ETL pipeline with multi-phase quality checks.")
        pdf.ln(5)

        # 2. Statistics Table
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(200, 10, "2. Processing Statistics", border=0, new_x="LMARGIN", new_y="NEXT", align='L')
        pdf.set_font("helvetica", '', 12)
        pdf.ln(5)

        pdf.cell(100, 10, "Metric", border=1)
        pdf.cell(0, 10, "Value", border=1, new_x="LMARGIN", new_y="NEXT")

        pdf.cell(100, 10, "Initial Records Count", border=1)
        pdf.cell(0, 10, format(stats.get('initial_rows', 0), ','), border=1, new_x="LMARGIN", new_y="NEXT")

        pdf.cell(100, 10, "Final Processed Rows", border=1)
        pdf.cell(0, 10, format(stats.get('final_rows', 0), ','), border=1, new_x="LMARGIN", new_y="NEXT")

        pdf.cell(100, 10, "Sparse Records Pruned", border=1)
        pdf.cell(0, 10, format(stats.get('pruned_rows', 0), ','), border=1, new_x="LMARGIN", new_y="NEXT")

        pdf.cell(100, 10, "Outliers Normalized (IQR)", border=1)
        pdf.cell(0, 10, str(stats.get('outliers_handled', 0)), border=1, new_x="LMARGIN", new_y="NEXT")

        pdf.cell(100, 10, "Total Features Loaded", border=1)
        pdf.cell(0, 10, str(stats.get('columns', 0)), border=1, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # 3. Decision Support
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(200, 10, "3. Pipeline Actions & Improvements", border=0, new_x="LMARGIN", new_y="NEXT", align='L')
        pdf.set_font("helvetica", '', 12)
        pdf.ln(5)
        
        improvement_msg = (
            "The pipeline successfully performed the following automated improvements:\n"
            "- Pruned observations with over 50% missing data points.\n"
            "- Identified and clamped extreme outliers using Interquartile Range (IQR) method.\n"
            "- Normalized categorical domains and inferred temporal data types.\n"
            "- Imputed missing numerical values with their respective feature means to preserve distribution integrity."
        )
        pdf.multi_cell(0, 10, improvement_msg)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        logging.info(f"PDF Quality Report successfully generated at {output_path}")

    except Exception as e:
        logging.error(f"Failed to generate PDF Report: {e}")
