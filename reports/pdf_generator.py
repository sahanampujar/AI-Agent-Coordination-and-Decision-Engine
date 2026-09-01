from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import darkblue
from reportlab.lib.units import inch
import os


def generate_pdf(report_text, filename="Business_Report.pdf"):
    """
    Generate a PDF report. `filename` defaults to the original fixed
    name for backward compatibility, but callers (e.g. the REST API,
    which may generate many reports for many runs) can pass a unique
    path such as f"reports_output/{run_id}.pdf" to avoid overwriting
    previous reports.
    """

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    title_style.textColor = darkblue

    heading_style = styles["Heading2"]

    normal_style = styles["BodyText"]

    story = []

    # -----------------------
    # Title
    # -----------------------

    story.append(
        Paragraph(
            "Development of Enterprise Workflow Platform with Decision Automation system",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Business Analysis Report",
            heading_style
        )
    )

    story.append(
        Paragraph("<br/><br/>", normal_style)
    )

    # -----------------------
    # Convert Markdown
    # -----------------------

    lines = report_text.split("\n")

    for line in lines:

        line = line.strip()

        if not line:
            continue

        line = line.replace("**", "")

        if line.endswith(":"):
            story.append(
                Paragraph(
                    f"<b>{line}</b>",
                    heading_style
                )
            )

        else:
            story.append(
                Paragraph(
                    line,
                    normal_style
                )
            )

    doc.build(story)

    return filename