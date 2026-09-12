import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

os.makedirs("data/sample_test_issues", exist_ok=True)

def create_pdf(filename, title, description, steps, expected, actual, env, logs):
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e1b4b'),
        spaceAfter=12
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4338ca'),
        spaceBefore=10,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#dc2626'),
        backColor=colors.HexColor('#f8fafc'),
        borderColor=colors.HexColor('#e2e8f0'),
        borderWidth=1,
        borderPadding=6,
        spaceBefore=6,
        spaceAfter=6
    )

    elements = []
    
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("Issue Description", section_heading))
    elements.append(Paragraph(description, body_style))
    elements.append(Spacer(1, 8))
    
    if steps:
        elements.append(Paragraph("Steps to Reproduce", section_heading))
        elements.append(Paragraph(steps.replace('\n', '<br/>'), body_style))
        elements.append(Spacer(1, 8))

    if expected or actual:
        elements.append(Paragraph("Expected vs Actual Behavior", section_heading))
        elements.append(Paragraph(f"<b>Expected:</b> {expected}", body_style))
        elements.append(Paragraph(f"<b>Actual:</b> {actual}", body_style))
        elements.append(Spacer(1, 8))

    if env:
        elements.append(Paragraph("Environment Metadata", section_heading))
        elements.append(Paragraph(env, body_style))
        elements.append(Spacer(1, 8))

    if logs:
        elements.append(Paragraph("Error Stack Trace / System Logs", section_heading))
        elements.append(Paragraph(logs.replace('\n', '<br/>'), code_style))

    doc.build(elements)
    print(f"[PDF Generator] Successfully created {filename}")


# 1. Bug PDF
create_pdf(
    "data/sample_test_issues/sample_bug_upload_crash.pdf",
    "Application crashes when uploading large file",
    "When uploading a PNG image larger than 5MB, the backend service throws a NullPointerException in FileHandler.java line 42. The upload progress freezes and returns HTTP 500 server error.",
    "1. Navigate to file upload dashboard\n2. Select 10MB test PNG image\n3. Click Submit Upload button",
    "File uploads cleanly and thumbnail displays in preview pane.",
    "System freezes and returns HTTP 500 Internal Server Error exception.",
    "Windows 11, Chrome 120, Python 3.14, FastAPI",
    "java.lang.NullPointerException: File parameter is null at FileHandler.upload(FileHandler.java:42)\n  at org.springframework.web.servlet.DispatcherServlet.doDispatch(DispatcherServlet.java:1067)"
)

# 2. Feature Request PDF
create_pdf(
    "data/sample_test_issues/sample_feature_dark_mode.pdf",
    "Please add dark mode toggle to navigation header",
    "Add dark mode support with automatic system preference detection. Users should be able to toggle themes and persist settings in local storage across browser sessions.",
    "N/A - Feature Enhancement Proposal",
    "Header includes theme toggle button with light/dark/system mode options.",
    "Only default light theme is currently supported across user dashboards.",
    "All modern desktop and mobile browsers",
    ""
)

# 3. Database Deadlock Bug PDF
create_pdf(
    "data/sample_test_issues/sample_database_deadlock.pdf",
    "Database connection pool exhausted under spike load",
    "During peak traffic hours, the PostgreSQL backend database throws OperationalError too many connections and transaction deadlocks occur on high concurrency write workloads.",
    "1. Execute 100 concurrent PATCH requests to user settings endpoint\n2. Observe database lock contention",
    "Database handles locks sequentially without throwing OperationalError.",
    "Database transaction deadlocks with PGError 40P01.",
    "PostgreSQL 16, SQLAlchemy 2.0, FastAPI",
    "sqlalchemy.exc.OperationalError: (psycopg2.errors.DeadlockDetected) ERROR: deadlock detected\nDETAIL: Process 1820 waits for ShareLock on transaction 94820; blocked by process 1821."
)
