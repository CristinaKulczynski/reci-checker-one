from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)


def export_results_to_pdf(results, pdf_path=None):
    """
    Gera um PDF a partir da lista de resultados.

    results: lista de dicts no formato:
        {
            "item": ...,
            "description": ...,
            "status": ...,
            "comments": ...
        }

    pdf_path: caminho opcional para o PDF.
              Se None, gera um nome automático.
    """

    headers = ["Item", "Descrição", "Status", "Comentários"]

    styles = getSampleStyleSheet()

    title_style = styles["Title"]

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
    )

    data = []

    for result in results:
        item = str(result.get("item", ""))
        status = str(result.get("status", ""))

        description_text = escape(str(result.get("description", "")))
        comments_text = escape(str(result.get("comments", "")))

        description_par = Paragraph(description_text, body_style)
        comments_par = Paragraph(comments_text, body_style)

        data.append(
            [
                item,
                description_par,
                status,
                comments_par,
            ]
        )

    if pdf_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = f"relatorio_reci_checker_{timestamp}.pdf"

    pdf_path = Path(pdf_path)

    doc = SimpleDocTemplate(
        pdf_path.as_posix(),
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    elements = []

    elements.append(Paragraph("Relatório de Verificação de Manuscrito", title_style))
    elements.append(Spacer(1, 12))

    table_data = [headers] + data

    table = Table(
        table_data,
        colWidths=[
            30,   # Item
            260,  # Descrição
            35,   # Status
            200,  # Comentários
        ],
        repeatRows=1,
    )

    table_style = TableStyle(
        [
            # Cabeçalho mais suave
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),

            # Corpo minimalista
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),

            # Alinhamento
            ("ALIGN", (0, 0), (0, -1), "CENTER"),   # Item
            ("ALIGN", (2, 1), (2, -1), "CENTER"),   # Status

            # Grade bem leve
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),

            # Fundo branco em todas as linhas (sem listras)
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ]
    )

    table.setStyle(table_style)
    elements.append(table)

    doc.build(elements)

    print(f"\nPDF gerado em: {pdf_path.resolve()}")
