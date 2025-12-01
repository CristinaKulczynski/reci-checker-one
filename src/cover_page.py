from metadata import *
import re
import xml.etree.ElementTree as ET

AUTHORS_PATTERN = r"^Autor\s*:\s*(.*)"


def authors(text, authors_pattern=AUTHORS_PATTERN, max_authors=10):
    authors = re.findall(authors_pattern, text, re.MULTILINE)

    status = "NA"
    if len(authors) <= max_authors:
        status = "A"

    return {"status": status,
            "comments": ""}


def complete_names(text, authors_pattern=AUTHORS_PATTERN):
    authors = re.findall(authors_pattern, text, re.MULTILINE)

    status = "A"
    for author in authors:
        if (re.search(r"\.", author) or len(author.split()) < 2):
            status = "NA"

    return {"status": status,
            "comments": ""}


def orcid_and_lattes(text):
    authors = re.findall(AUTHORS_PATTERN, text, re.MULTILINE)

    orcid_pattern = r"ORCID:\s*https://orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[\dX]"
    orcids = re.findall(orcid_pattern, text, re.MULTILINE)

    lattes_pattern = r"Currículo lattes:\s*http://lattes\.cnpq\.br/\d+"
    lattes = re.findall(lattes_pattern, text, re.MULTILINE)

    status = "NA"
    if len(authors) == len(orcids) == len(lattes):
        status = "A"

    return {"status": status,
            "comments": ""}


def afiliation(text):
    afiliation_pattern = r"Afiliação:\s*(.*?)\."
    afiliations = re.findall(afiliation_pattern, text, re.MULTILINE)

    valid_ufs = {
        'Acre', 'Alagoas', 'Amapá', 'Amazonas', 'Bahia', 'Ceará',
        'Distrito Federal', 'Espírito Santo', 'Goiás', 'Maranhão',
        'Mato Grosso', 'Mato Grosso do Sul', 'Minas Gerais', 'Pará',
        'Paraíba', 'Paraná', 'Pernambuco', 'Piauí', 'Rio de Janeiro',
        'Rio Grande do Norte', 'Rio Grande do Sul', 'Rondônia',
        'Roraima', 'Santa Catarina', 'São Paulo', 'Sergipe', 'Tocantins'
    }

    status = "A"
    for afiliation in afiliations:
        if not any(uf in afiliation for uf in valid_ufs):
            status = "NA"

    return {"status": status,
            "comments": ""}


def bigraphy(text):
    biography_summary_pattern = r"Resumo da Biografia:\s*((?:(?!Autor(?:\s+Correspondente)?:|Contribuições dos autores:).)+)"
    biography_summaries = re.findall(
        biography_summary_pattern, text, re.MULTILINE | re.DOTALL)
    biography_summaries = [bio.strip() for bio in biography_summaries]

    professional_categories = [
        r'\bMestrando\b', r'\bMestre\b', r'\bDoutorando\b', r'\bDoutor\b',
        r'\bGraduando\b', r'\bGraduado\b', r'\bEspecialista\b',
        r'\bProfessor\b', r'\bProfessora\b', r'\bPós-Doutorando\b',
        r'\bPós-Doutor\b', r'\bEnfermeiro\b', r'\bEnfermeira\b',
        r'\bFarmacêutico\b', r'\bMédico\b', r'\bMédica\b',
        r'\bTécnico\b', r'\bTécnica\b'
    ]

    titulations = [
        r'\bMestrado\b', r'\bDoutorado\b', r'\bGraduação\b',
        r'\bEspecialização\b', r'\bEspecialista\b',
        r'\bPós-Graduação\b', r'\bPós-Doutorado\b',
        r'\bBacharelado\b', r'\bLicenciatura\b',
        r'\bGraduando\b', r'\bGraduado\b'
    ]

    authors = re.findall(AUTHORS_PATTERN, text, re.MULTILINE)

    status = "A"
    missing_info = []

    # Check if we have biographies for all authors
    if len(biography_summaries) != len(authors):
        status = "NA"
        missing_info.append(
            f"Encontradas {len(biography_summaries)} biografias para {len(authors)} autores")

    # Validate each biography
    for i, bio in enumerate(biography_summaries):
        has_category = any(re.search(pattern, bio, re.IGNORECASE)
                           for pattern in professional_categories)
        has_titulation = any(re.search(pattern, bio, re.IGNORECASE)
                             for pattern in titulations)

        if not has_category:
            status = "NA"
            missing_info.append(
                f"Biografia {i+1}: falta categoria profissional")

        if not has_titulation:
            status = "NA"
            missing_info.append(f"Biografia {i+1}: falta maior titulação")

    description = "; ".join(missing_info) if missing_info else ""

    return {"status": status,
            "comments": description}


def item_10(cover_page_text):
    description = """Apresenta título, nome completo dos autores, afiliação, ORCID, lattes, endereço e e-mail do autor correspondente e contribuições de autoria"""

    item_1 = authors(cover_page_text)
    item_2 = complete_names(cover_page_text)
    item_3 = orcid_and_lattes(cover_page_text)
    item_4 = afiliation(cover_page_text)
    item_5 = bigraphy(cover_page_text)

    status = "A"

    for item in [item_1, item_2, item_3, item_4, item_5]:
        if item["status"] == "NA":
            status = "NA"

    comments = ""
    for item in [item_1, item_2, item_3, item_4, item_5]:
        if item["comments"]:
            comments += f"{item['comments']}\n"

    return {"item": 10,
            "description": description,
            "status": status,
            "comments": comments}


def _is_bold(run, ns):
    run_props = run.find('.//w:rPr', ns)
    return run_props is not None and run_props.find('.//w:b', ns) is not None


def _get_para_text(runs, ns):
    return ''.join([
        t.text for r in runs
        for t in [r.find('.//w:t', ns)]
        if t is not None and t.text is not None
    ])


def item_11(xml_path):
    description = "São especificadas quais foram as contribuições individuais de cada autor na elaboração do artigo, no seguinte formato: nome completo de cada autor (em negrito e escrito por extenso), seguido das contribuições."
    status = "A"
    comments = []

    try:
        cover_page_xml = str(xml_path).replace(
            "manuscript_document.xml", "cover_page_document.xml")
        tree = ET.parse(cover_page_xml)
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs = tree.findall('.//w:p', ns)

        contrib_start_idx = -1
        for i, para in enumerate(paragraphs):
            para_text = _get_para_text(para.findall('.//w:r', ns), ns)
            if re.search(r'Contribuições\s+dos\s+autores:', para_text, re.IGNORECASE):
                contrib_start_idx = i
                break

        if contrib_start_idx == -1:
            return {
                "item": 11,
                "description": description,
                "status": "NA",
                "comments": "Seção 'Contribuições dos autores:' não encontrada"
            }

        authors = []
        for para in paragraphs[:contrib_start_idx]:
            para_text = _get_para_text(para.findall('.//w:r', ns), ns)
            autor_match = re.match(r'^\s*Autor\s*:\s*(.+)', para_text)
            if autor_match:
                author_name = re.sub(
                    r'\d+$', '', autor_match.group(1).strip()).strip()
                if author_name:
                    authors.append(author_name)

        author_contributions = []
        authors_found_in_contributions = []

        for i in range(contrib_start_idx + 1, len(paragraphs)):
            runs = paragraphs[i].findall('.//w:r', ns)
            para_text = _get_para_text(runs, ns).strip()

            if para_text and (para_text.startswith('Autor Correspondente') or
                              para_text.startswith('Endereço') or
                              para_text.startswith('Todos os autores')):
                break

            if not para_text:
                continue

            bold_text = ""
            for run in runs:
                text_elem = run.find('.//w:t', ns)
                if text_elem is None or text_elem.text is None:
                    continue
                if _is_bold(run, ns):
                    bold_text += text_elem.text
                else:
                    break

            if bold_text:
                bold_name = bold_text.strip()

                contribution_text = ""
                found_bold = False
                for run in runs:
                    text_elem = run.find('.//w:t', ns)
                    if text_elem is None or text_elem.text is None:
                        continue
                    if _is_bold(run, ns):
                        found_bold = True
                    elif found_bold:
                        contribution_text += text_elem.text

                author_contributions.append({
                    'bold_name': bold_name,
                    'contribution_text': contribution_text.strip()
                })

                if ' e ' in bold_name:
                    authors_found_in_contributions.extend(
                        [n.strip() for n in bold_name.split(' e ')])
                else:
                    authors_found_in_contributions.append(bold_name)

        if not author_contributions:
            status = "NA"
            comments.append("Nenhuma contribuição de autor encontrada")
        else:
            for contrib in author_contributions:
                if not contrib['bold_name']:
                    status = "NA"
                    comments.append("Contribuição sem nome em negrito")
                    break
                elif len(contrib['bold_name'].split()) < 2 and ' e ' not in contrib['bold_name']:
                    status = "NA"
                    comments.append(
                        f"Nome muito curto ou incompleto: '{contrib['bold_name']}'")
                    break
                elif not contrib['contribution_text']:
                    status = "NA"
                    comments.append(
                        f"Autor '{contrib['bold_name']}' não possui descrição de contribuição")
                    break

            if authors and status == "A":
                def normalize(name): return name.lower().strip()
                normalized_authors = [normalize(a) for a in authors]
                normalized_found = [normalize(a)
                                    for a in authors_found_in_contributions]

                missing = [a for a in normalized_authors
                           if not any(a in f or f in a for f in normalized_found)]

                if missing:
                    status = "NA"
                    comments.append(
                        f"Autores não encontrados nas contribuições: {', '.join(missing)}")

        if status == "A":
            comments.append(
                f"Seção 'Contribuições dos autores' está correta ({len(author_contributions)} parágrafo(s), {len(authors_found_in_contributions)} autor(es))")

    except Exception as e:
        return {
            "item": 11,
            "description": description,
            "status": "-",
            "comments": f"Erro ao processar XML: {str(e)}"
        }

    return {
        "item": 11,
        "description": description,
        "status": status,
        "comments": "; ".join(comments) if comments else ""
    }
