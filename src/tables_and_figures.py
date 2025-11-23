from docx_utils import docx_images_count
import xml.etree.ElementTree as ET
import docx


def item_54(manuscript_path):
    description = "Apresenta no máximo 5 figuras e/ou tabelas que devem estar apresentadas no corpo do texto."
    status = "A"

    document = docx.Document(str(manuscript_path))
    table_count = len(document.tables)
    images_count = docx_images_count(manuscript_path)

    if table_count + images_count > 5:
        status = "NA"

    comments = f"{table_count} tabela(s) e {images_count} imagem(s)"

    return {"item": 54,
            "description": description,
            "status": status,
            "comments": comments}


def item_58(xml_path):
    description = "Tabelas são elaboradas no Word."
    status = "A"
    comments = []

    try:
        tree = ET.parse(xml_path)
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

        tables = tree.findall('.//w:tbl', namespaces)
        table_count = len(tables)

        drawings = tree.findall('.//w:drawing', namespaces)
        pictures = tree.findall('.//w:pict', namespaces)
        images_count = len(drawings) + len(pictures)

        if table_count == 0 and images_count > 0:
            status = "NA"
            comments.append(
                f"Nenhuma tabela editável encontrada, mas há {images_count} imagem(s) no documento. Tabelas devem ser criadas no Word, não como imagens.")
        elif table_count == 0 and images_count == 0:
            status = "A"
            comments.append("Nenhuma tabela ou imagem encontrada no documento")
        else:
            if images_count > 0:
                comments.append(
                    f"{table_count} tabela(s) editável(is) encontrada(s); {images_count} imagem(s) no documento")
            else:
                comments.append(
                    f"{table_count} tabela(s) editável(is) encontrada(s)")

    except Exception as e:
        return {
            "item": 58,
            "description": description,
            "status": "-",
            "comments": f"Erro ao processar documento: {str(e)}"
        }

    return {
        "item": 58,
        "description": description,
        "status": status,
        "comments": "; ".join(comments)
    }


def item_61(xml_path):
    description = "Legendas de figuras devem estar abaixo da figura, alinhadas à esquerda e com fonte tamanho 10."
    status = "A"
    comments = []

    try:
        tree = ET.parse(xml_path)
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

        paragraphs = tree.findall('.//w:p', namespaces)
        figure_count = 0

        for i, para in enumerate(paragraphs):
            if para.find('.//w:drawing', namespaces) is None:
                continue

            figure_count += 1

            # Search for caption in nearby paragraphs (within 20 paragraphs range)
            # Figures with complex elements may have the caption further away
            caption_before_idx = _find_caption_in_range(
                paragraphs, i - 20, i, namespaces)
            caption_after_idx = _find_caption_in_range(
                paragraphs, i + 1, i + 21, namespaces)

            if caption_before_idx is not None and caption_after_idx is None:
                status = "NA"
                comments.append(
                    f"Figura {figure_count}: legenda acima (deve estar abaixo)")
            elif caption_after_idx is None:
                status = "NA"
                comments.append(
                    f"Figura {figure_count}: legenda não encontrada abaixo")
            else:
                # Validate caption formatting
                issues = _validate_caption_format(
                    paragraphs[caption_after_idx], namespaces)
                if issues:
                    status = "NA"
                    comments.append(
                        f"Figura {figure_count}: {', '.join(issues)}")

        if not comments:
            comments.append(
                f"{figure_count} figura(s) formatadas corretamente" if figure_count else "Nenhuma figura encontrada")

    except Exception as e:
        return {"item": 61, "description": description, "status": "-", "comments": f"Erro: {str(e)}"}

    return {"item": 61, "description": description, "status": status, "comments": "; ".join(comments)}


def _find_caption_in_range(paragraphs, start_idx, end_idx, namespaces):
    """Search for a figure caption within a range of paragraphs. Returns index or None."""
    start_idx = max(0, start_idx)
    end_idx = min(len(paragraphs), end_idx)

    for i in range(start_idx, end_idx):
        if _is_figure_caption(paragraphs[i], namespaces):
            return i
    return None


def _is_figure_caption(para, namespaces):
    """Check if paragraph is a figure caption - either with 'Legenda' style or starts with 'Figura' + number."""
    import re

    # Get paragraph text
    text = ''.join([t.text for t in para.findall(
        './/w:t', namespaces) if t.text]).strip()

    # Check if text starts with "Figura" followed by a number (e.g., "Figura 1", "Figura 2.")
    if re.match(r'^Figura\s+\d+', text, re.IGNORECASE):
        return True

    # Also check for 'Legenda' style (old format)
    pStyle = para.find('.//w:pStyle', namespaces)
    if pStyle is not None and pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') == 'Legenda':
        return 'Figura' in text or 'figura' in text

    return False


def _validate_caption_format(para, namespaces):
    """Validate caption alignment and font size. Returns list of issues."""
    issues = []

    # Check alignment (must be left or unspecified)
    jc = para.find('.//w:jc', namespaces)
    if jc is not None:
        alignment = jc.get(
            '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
        if alignment != 'left':
            issues.append(f"alinhamento {alignment} (deve ser esquerda)")

    # Check font size (must be 20 half-points = 10pt)
    sz = para.find('.//w:sz', namespaces)
    if sz is not None:
        size_val = sz.get(
            '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
        if size_val != '20':
            issues.append(f"fonte {int(size_val) / 2}pt (deve ser 10pt)")
    else:
        issues.append("fonte não especificada")

    return issues
