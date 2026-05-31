from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from models.report_output import PhysicianBrief

class PDFExporter:
    def export(self, brief: PhysicianBrief, output_path: str, facility_name: str) -> str:
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(f"{facility_name} - Physician Brief", styles['Title']))
        story.append(Paragraph(f"Case Number: {brief.case_number}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Differential Diagnoses", styles['Heading2']))
        for diff in brief.differentials:
            story.append(Paragraph(f"- {diff.condition_name} (ICD-10: {diff.icd_10_code})", styles['Normal']))
            
        doc.build(story)
        return output_path
