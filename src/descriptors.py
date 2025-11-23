import re
import xml.etree.ElementTree as ET
from structure import get_sections


def item_30(manuscript_text):
    description = "Apresentados abaixo de cada versão do resumo, citados nos idiomas português, inglês e espanhol."
    status = "A"
    comments = []

    sections = get_sections(manuscript_text)
    resumo = sections.get("RESUMO", "")
    abstract = sections.get("ABSTRACT", "")
    resumen = sections.get("RESUMEN", "")

    descritores_pattern = r"Descritores\s*:\s*[A-ZÀ-Ú]"
    if not re.search(descritores_pattern, resumo, re.IGNORECASE):
        status = "NA"
        comments.append("RESUMO não contém 'Descritores:' no formato esperado")

    keywords_pattern = r"Keywords\s*:\s*[A-Z]"
    if not re.search(keywords_pattern, abstract, re.IGNORECASE):
        status = "NA"
        comments.append("ABSTRACT não contém 'Keywords:' no formato esperado")

    palabras_pattern = r"Palabras\s+Clave\s*:\s*[A-ZÀ-Ú]"
    if not re.search(palabras_pattern, resumen, re.IGNORECASE):
        status = "NA"
        comments.append(
            "RESUMEN não contém 'Palabras Clave:' no formato esperado")

    if status == "A":
        comments.append(
            "Descritores, Keywords e Palabras Clave encontrados nas três versões")

    return {
        "item": 30,
        "description": description,
        "status": status,
        "comments": "; ".join(comments)
    }


def item_31(manuscript_text):
    description = "Apresenta de três (3) a cinco (5) descritores."
    status = "A"
    comments = []

    sections = get_sections(manuscript_text)
    resumo = sections.get("RESUMO", "")
    abstract = sections.get("ABSTRACT", "")
    resumen = sections.get("RESUMEN", "")

    def count_descriptors(text, label_pattern):
        """Extract descriptors text and count items separated by periods."""
        match = re.search(
            label_pattern + r"\s*:\s*(.+?)(?=\n|$)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return 0, False

        descriptors_text = match.group(1).strip()

        used_semicolon = ";" in descriptors_text

        # conta descritores quebrando por '.' ou ';'
        parts = re.split(r"[.;]", descriptors_text)
        descriptors = [d.strip() for d in parts if d.strip()]

        return len(descriptors), used_semicolon

    # RESUMO
    descritores_count, descritores_semicolon = count_descriptors(
        resumo,
        r"Descritores",
    )
    if descritores_count < 3 or descritores_count > 5 or descritores_semicolon:
        status = "NA"
        if descritores_semicolon:
            comments.append(
                f"RESUMO tem {descritores_count} descritores, porém foram separados por ponto e vírgula ao invés de ponto (esperado: 3-5 descritores)."
            )
        else:
            comments.append(
                f"RESUMO tem {descritores_count} descritores (esperado: 3-5)."
            )
    else:
        comments.append(f"RESUMO: {descritores_count} descritores.")

    # ABSTRACT
    keywords_count, keywords_semicolon = count_descriptors(
        abstract,
        r"Keywords",
    )
    if keywords_count < 3 or keywords_count > 5 or keywords_semicolon:
        status = "NA"
        if keywords_semicolon:
            comments.append(
                f"ABSTRACT tem {keywords_count} keywords, porém foram separadas por ponto e vírgula ao invés de ponto (esperado: 3-5 keywords)."
            )
        else:
            comments.append(
                f"ABSTRACT tem {keywords_count} keywords (esperado: 3-5)."
            )
    else:
        comments.append(f"ABSTRACT: {keywords_count} keywords.")

    # RESUMEN
    palabras_count, palabras_semicolon = count_descriptors(
        resumen,
        r"Palabras\s+Clave",
    )
    if palabras_count < 3 or palabras_count > 5 or palabras_semicolon:
        status = "NA"
        if palabras_semicolon:
            comments.append(
                f"RESUMEN tem {palabras_count} palabras clave, porém foram separadas por ponto e vírgula ao invés de ponto (esperado: 3-5 palabras clave)."
            )
        else:
            comments.append(
                f"RESUMEN tem {palabras_count} palabras clave (esperado: 3-5)."
            )
    else:
        comments.append(f"RESUMEN: {palabras_count} palabras clave.")

    return {
        "item": 31,
        "description": description,
        "status": status,
        "comments": "; ".join(comments),
    }


def _is_bold(run, ns):
    """Check if a run has bold formatting."""
    run_props = run.find('.//w:rPr', ns)
    return run_props is not None and run_props.find('.//w:b', ns) is not None


def _is_italic(run, ns):
    """Check if a run has italic formatting."""
    run_props = run.find('.//w:rPr', ns)
    return run_props is not None and run_props.find('.//w:i', ns) is not None


def _get_para_text(runs, ns):
    """Extract complete text from paragraph runs."""
    return ''.join([
        t.text for r in runs
        for t in [r.find('.//w:t', ns)]
        if t is not None and t.text is not None
    ])


def _check_term_bold_and_capitalized(para_text, runs, term, ns):
    """Check if a term in paragraph is bold and capitalized."""
    if term not in para_text:
        return False

    accumulated = ""
    for run in runs:
        text_elem = run.find('.//w:t', ns)
        if text_elem is None or text_elem.text is None:
            continue

        accumulated += text_elem.text

        # Check if we now have the complete term
        if term in accumulated:
            term_start = accumulated.find(term)
            term_end = term_start + len(term)

            # Check capitalization
            if not accumulated[term_start].isupper():
                return False

            # Verify all runs containing the term are bold
            check_text = ""
            for check_run in runs:
                check_elem = check_run.find('.//w:t', ns)
                if check_elem is None or check_elem.text is None:
                    continue

                prev_len = len(check_text)
                check_text += check_elem.text
                curr_len = len(check_text)

                # Check if this run overlaps with the term
                if prev_len < term_end and curr_len > term_start:
                    if not _is_bold(check_run, ns):
                        return False

            return True

    return False


def item_32(xml_path):
    description = "Utiliza as terminologias 'Descritores', 'Keywords' e 'Palabras Clave', em negrito e primeira letra maiúscula."
    status = "A"
    comments = []

    try:
        tree = ET.parse(xml_path)
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = tree.findall('.//w:p', ns)

        terms = ['Descritores', 'Keywords', 'Palabras Clave']
        found_terms = {term: False for term in terms}

        for para in paragraphs:
            runs = para.findall('.//w:r', ns)
            para_text = _get_para_text(runs, ns)

            for term in terms:
                if not found_terms[term] and _check_term_bold_and_capitalized(para_text, runs, term, ns):
                    found_terms[term] = True

        for term, found in found_terms.items():
            if not found:
                status = "NA"
                comments.append(
                    f"'{term}' não encontrado ou incorretamente formatado")

        if status == "A":
            comments.append("Todos os termos estão formatados corretamente")

        return {
            "item": 32,
            "description": description,
            "status": status,
            "comments": "; ".join(comments)
        }

    except Exception as e:
        return {
            "item": 32,
            "description": description,
            "status": "-",
            "comments": f"Erro ao processar XML: {str(e)}"
        }


def _get_descriptor_runs_after_label(runs, label, ns):
    """Get all runs containing descriptors after the label (after ':')."""
    para_text = _get_para_text(runs, ns)

    if label not in para_text or ':' not in para_text:
        return None

    found_colon = False
    descriptor_runs = []
    accumulated_text = ""

    for run in runs:
        text_elem = run.find('.//w:t', ns)
        if text_elem is None or text_elem.text is None:
            continue

        text = text_elem.text
        accumulated_text += text

        if not found_colon:
            if label in accumulated_text and ':' in accumulated_text:
                found_colon = True
                if ':' in text and text.split(':', 1)[1].strip():
                    descriptor_runs.append(run)
        elif found_colon and text.strip():
            descriptor_runs.append(run)

    return descriptor_runs if descriptor_runs else None


def item_33(xml_path):
    description = "Descritores, Keywords e Palabras Clave apresentam-se grifadas em itálico, separadas por ponto final."
    status = "A"
    comments = []

    try:
        tree = ET.parse(xml_path)
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = tree.findall('.//w:p', ns)

        labels = ['Descritores', 'Keywords', 'Palabras Clave']
        results = {}

        for label in labels:
            results[label] = {'found': False,
                              'italic': True, 'has_periods': False}

        for para in paragraphs:
            runs = para.findall('.//w:r', ns)
            para_text = _get_para_text(runs, ns)

            for label in labels:
                if label in para_text and not results[label]['found']:
                    results[label]['found'] = True

                    desc_runs = _get_descriptor_runs_after_label(
                        runs, label, ns)

                    if desc_runs:
                        for run in desc_runs:
                            if not _is_italic(run, ns):
                                results[label]['italic'] = False
                                break

                        desc_text = ''.join([
                            t.text for r in desc_runs
                            for t in [r.find('.//w:t', ns)]
                            if t is not None and t.text is not None
                        ])
                        results[label]['has_periods'] = '.' in desc_text

        # Evaluate results
        for label, checks in results.items():
            if not checks['found']:
                status = "NA"
                comments.append(f"'{label}' não encontrado")
            else:
                if not checks['italic']:
                    status = "NA"
                    comments.append(
                        f"Descritores de '{label}' não estão em itálico")
                if not checks['has_periods']:
                    status = "NA"
                    comments.append(
                        f"Descritores de '{label}' não estão separados por ponto final")

        if status == "A":
            comments.append(
                "Todos os descritores estão em itálico e separados por ponto final")

        return {
            "item": 33,
            "description": description,
            "status": status,
            "comments": "; ".join(comments)
        }

    except Exception as e:
        return {
            "item": 33,
            "description": description,
            "status": "-",
            "comments": f"Erro ao processar XML: {str(e)}"
        }
