import io
import qrcode
import os
import openai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from PIL import Image

openai.api_key = "your-api-key-here"

def get_ai_summary(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a medical assistant that summarizes patient diagnosis notes."},
                {"role": "user", "content": f"Summarize the following medical diagnosis for a discharge summary:\n{text}"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error fetching AI summary: {e}")
        return "AI Summary generation failed."

def generate_qr_code(data_string, box_size=5, border=4):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data_string)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white")
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

def create_discharge_summary_pdf(data, logo_path="hospital_logo.png"):
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(name='TitleStyle', fontSize=20, leading=24, alignment=1, spaceAfter=20, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='FooterStyle', fontSize=10, alignment=1, spaceBefore=0, spaceAfter=0, textColor=colors.gray))

        Story = []

        if os.path.exists(logo_path):
            try:
                logo = ReportLabImage(logo_path, width=2.0*inch, height=0.5*inch)
                Story.append(logo)
                Story.append(Spacer(1, 0.2 * inch))
            except Exception as e:
                print(f"Error loading logo image: {e}")
        else:
            Story.append(Spacer(1, 0.7 * inch))

        Story.append(Paragraph("Green Valley Hospital - Discharge Summary", styles['TitleStyle']))
        Story.append(Spacer(1, 0.2 * inch))

        Story.append(Paragraph(f"<b>Patient Name:</b> {data.get('patient_name', 'N/A')} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>ID:</b> {data.get('patient_id', 'N/A')}", styles['Normal']))
        Story.append(Paragraph(f"<b>Age/Gender:</b> {data.get('patient_age', 'N/A')} / {data.get('patient_gender', 'N/A')} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Discharge:</b> {data.get('discharge_date', 'N/A')} {data.get('discharge_time', 'N/A')}", styles['Normal']))
        Story.append(Spacer(1, 0.1 * inch))

        Story.append(Paragraph(f"<b>Diagnosis:</b> {data.get('diagnosis_summary', 'No diagnosis provided.')}", styles['Normal']))
        Story.append(Spacer(1, 0.05 * inch))

        Story.append(Paragraph(f"<b>Procedure:</b> {data.get('procedures_done', 'No procedures performed.')}", styles['Normal']))
        Story.append(Spacer(1, 0.2 * inch))

        Story.append(Paragraph("<b>Prescribed Medications:</b>", styles['Normal']))
        med_data = [["Name", "Dosage", "Frequency", "Duration"]]
        for med in data.get('medications', []):
            med_data.append([med.get('name', ''), med.get('dose', ''), med.get('frequency', ''), med.get('duration', '')])

        med_table = Table(med_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F0F0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        Story.append(med_table)
        Story.append(Spacer(1, 0.2 * inch))

        Story.append(Paragraph("<b>Lab Tests Performed:</b>", styles['Normal']))
        lab_tests = data.get('lab_test_results', 'No lab tests performed.').split('\n')
        for test in lab_tests:
            if test.strip():
                Story.append(Paragraph(f"- {test.strip()}", styles['Normal']))
        Story.append(Spacer(1, 0.2 * inch))

        Story.append(Paragraph("<b>Post Discharge Instructions:</b>", styles['Normal']))
        instructions = data.get('post_care_instructions', 'No instructions provided.').split('\n')
        for instr in instructions:
            if instr.strip():
                Story.append(Paragraph(f"- {instr.strip()}", styles['Normal']))
        Story.append(Spacer(1, 0.2 * inch))

        Story.append(Paragraph(f"<b>Doctor:</b> {data.get('doctor_name', 'N/A')} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Signature:</b> ____________", styles['Normal']))
        Story.append(Spacer(1, 0.5 * inch))

        qr_data_string = f"PatientID: {data.get('patient_id', 'N/A')}\nName: {data.get('patient_name', 'N/A')}\nDischarge Date: {data.get('discharge_date', 'N/A')}"
        qr_img_pil = generate_qr_code(qr_data_string)

        if qr_img_pil:
            img_byte_arr = io.BytesIO()
            qr_img_pil.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            qr_image = ReportLabImage(img_byte_arr, width=1.0 * inch, height=1.0 * inch)
            Story.append(qr_image)
        else:
            Story.append(Paragraph("QR Code Unavailable", styles['Normal']))

        Story.append(Spacer(1, 0.2 * inch))

        footer_text = "Green Valley Hospital | www.greenvalleyhospital.example | +92-123-4567890"
        Story.append(Paragraph(footer_text, styles['FooterStyle']))

        doc.build(Story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None
