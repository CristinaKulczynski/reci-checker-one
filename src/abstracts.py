import re
import xml.etree.ElementTree as ET


def _is_bold(run, ns):
    run_props = run.find('.//w:rPr', ns)
    return run_props is not None and run_props.find('.//w:b', ns) is not None


def _get_para_text(runs, ns):
    return ''.join([
        t.text for r in runs
        for t in [r.find('.//w:t', ns)]
        if t is not None and t.text is not None
    ])


def _find_abstract_section(paragraphs, section_name, ns):
    """Find paragraphs belonging to an abstract section."""
    end_markers = ['RESUMO', 'ABSTRACT',
                   'RESUMEN', 'INTRODUÇÃO', 'INTRODUCTION']

    for i, para in enumerate(paragraphs):
        para_text = _get_para_text(para.findall('.//w:r', ns), ns)

        if re.match(r'^\s*' + re.escape(section_name) + r'\s*$', para_text, re.IGNORECASE):
            # Find end of this abstract section
            for j in range(i + 1, len(paragraphs)):
                next_text = _get_para_text(
                    paragraphs[j].findall('.//w:r', ns), ns).strip()
                for marker in end_markers:
                    if marker != section_name and re.match(r'^\s*' + re.escape(marker) + r'\s*$', next_text, re.IGNORECASE):
                        return paragraphs[i:j]
            return paragraphs[i:]

    return []


def _check_section_bold_with_colon(abstract_paras, section_with_colon, ns):
    """Check if section header with colon is bold."""
    for para in abstract_paras:
        runs = para.findall('.//w:r', ns)
        para_text = _get_para_text(runs, ns)

        if section_with_colon not in para_text:
            continue

        # Check if all runs containing the section are bold
        accumulated = ""
        for run in runs:
            text_elem = run.find('.//w:t', ns)
            if text_elem is None or text_elem.text is None:
                continue

            prev_len = len(accumulated)
            accumulated += text_elem.text

            # If we've accumulated the full section header, check boldness
            if section_with_colon in accumulated:
                section_start = accumulated.find(section_with_colon)
                section_end = section_start + len(section_with_colon)

                # Check if current run overlaps with section header
                if prev_len < section_end and len(accumulated) > section_start:
                    if not _is_bold(run, ns):
                        return False

                return True  # Found and all parts are bold

    return False  # Not found


def _check_abstract_sections(xml_path, abstract_name, sections, item_number, description):
    """Helper function to check abstract sections for a specific language."""
    status = "A"
    comments = []

    try:
        tree = ET.parse(xml_path)
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = tree.findall('.//w:p', ns)

        abstract_paras = _find_abstract_section(paragraphs, abstract_name, ns)

        if not abstract_paras:
            status = "NA"
            comments.append(f"{abstract_name} não encontrado")
        else:
            for section in sections:
                if not _check_section_bold_with_colon(abstract_paras, section, ns):
                    status = "NA"
                    comments.append(
                        f"'{section}' não encontrado ou não está em negrito")

        if status == "A":
            comments.append(f"{abstract_name} estruturado corretamente")

    except Exception as e:
        return {
            "item": item_number,
            "description": description,
            "status": "-",
            "comments": f"Erro ao processar XML: {str(e)}"
        }

    return {
        "item": item_number,
        "description": description,
        "status": status,
        "comments": "; ".join(comments) if comments else ""
    }


def item_24(xml_path):
    description = "Limite máximo de 250 palavras, em parágrafo único, com espaçamento simples entre as linhas."
    status = "A"
    comments = []

    try:
        tree = ET.parse(xml_path)
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = tree.findall('.//w:p', ns)

        # Find the RESUMO section
        abstract_paras = _find_abstract_section(paragraphs, 'RESUMO', ns)

        if not abstract_paras:
            return {
                "item": 24,
                "description": description,
                "status": "NA",
                "comments": "RESUMO não encontrado"
            }

        # Skip the first paragraph (the title "RESUMO")
        content_paras = abstract_paras[1:]

        # Count non-empty paragraphs (excluding the title and descriptors)
        non_empty_paras = []
        for para in content_paras:
            para_text = _get_para_text(para.findall('.//w:r', ns), ns).strip()
            # Ignore empty paragraphs and descriptors/keywords lines
            if para_text and not re.match(r'^\s*(Descritores|Unitermos|Palavras-chave):', para_text, re.IGNORECASE):
                non_empty_paras.append(para)

        # Check if it's a single paragraph
        if len(non_empty_paras) == 0:
            status = "NA"
            comments.append("RESUMO está vazio")
        elif len(non_empty_paras) > 1:
            status = "NA"
            comments.append(f"RESUMO deve ter apenas um parágrafo, encontrado {len(non_empty_paras)}")

        # Count words in all non-empty paragraphs
        total_text = ""
        for para in non_empty_paras:
            para_text = _get_para_text(para.findall('.//w:r', ns), ns)
            total_text += " " + para_text

        word_count = len(total_text.strip().split())

        if word_count > 250:
            status = "NA"
            comments.append(f"RESUMO tem {word_count} palavras, máximo permitido: 250")

        # Check line spacing for content paragraphs
        for para in non_empty_paras:
            para_props = para.find('.//w:pPr', ns)
            if para_props is not None:
                spacing = para_props.find('.//w:spacing', ns)
                if spacing is not None:
                    # Check line spacing
                    line_rule = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}lineRule')
                    line_val = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}line')
                    
                    # Simple spacing = 240 twips or line rule "auto" with line "240"
                    # Or lineRule "exact" with line "240"
                    if line_rule == "auto" and line_val and int(line_val) != 240:
                        status = "NA"
                        comments.append(f"RESUMO não tem espaçamento simples (encontrado: {line_val})")
                    elif line_rule == "exact" and line_val and int(line_val) != 240:
                        status = "NA"
                        comments.append(f"RESUMO não tem espaçamento simples (encontrado: {line_val})")

        if status == "A":
            comments.append(f"RESUMO formatado corretamente ({word_count} palavras, parágrafo único, espaçamento simples)")

    except Exception as e:
        return {
            "item": 24,
            "description": description,
            "status": "-",
            "comments": f"Erro ao processar XML: {str(e)}"
        }

    return {
        "item": 24,
        "description": description,
        "status": status,
        "comments": "; ".join(comments) if comments else ""
    }


def item_25(xml_path):
    description = "Justificativa e Objetivos, Métodos, Resultados e Conclusão (versão portuguesa)."
    sections = ['Justificativa e Objetivos:',
                'Métodos:', 'Resultados:', 'Conclusão:']
    return _check_abstract_sections(xml_path, 'RESUMO', sections, 25, description)


def item_26(xml_path):
    description = "Background and Objectives, Methods, Results e Conclusion (versão inglesa)."
    sections = ['Background and Objectives:',
                'Methods:', 'Results:', 'Conclusion:']
    return _check_abstract_sections(xml_path, 'ABSTRACT', sections, 26, description)


def item_27(xml_path):
    description = "Justificación y objetivos, Métodos, Resultados e Conclusión (versão espanhola)."
    sections = ['Justificación y Objetivos:',
                'Métodos:', 'Resultados:', 'Conclusión:']
    return _check_abstract_sections(xml_path, 'RESUMEN', sections, 27, description)


def item_28(xml_path):
    description = "Artigos originais: estruturado e separado nas seguintes seções = Justificativa e Objetivos, Métodos, Resultados, Conclusão (todos em negrito, somente a primeira letra em maiúsculo e seguido por dois pontos)."

    result_25 = item_25(xml_path)
    result_26 = item_26(xml_path)
    result_27 = item_27(xml_path)

    approved_count = sum(
        1 for r in [result_25, result_26, result_27] if r['status'] == 'A')

    if approved_count == 3:
        status = "A"
        comments = "Todos os resumos (RESUMO, ABSTRACT, RESUMEN) estão estruturados corretamente"
    elif approved_count > 0:
        status = "AP"
        approved = [r['item']
                    for r in [result_25, result_26, result_27] if r['status'] == 'A']
        comments = f"Parcialmente aprovado: {approved_count}/3 resumos estruturados corretamente (itens {approved})"
    else:
        status = "NA"
        comments = "Nenhum dos resumos está estruturado corretamente"

    result_28 = {
        "item": 28,
        "description": description,
        "status": status,
        "comments": comments
    }

    return (result_25, result_26, result_27, result_28)
