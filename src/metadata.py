import re

AUTHORS_PATTERN = r"^Autor\s*:\s*(.*)"


def extract_metadata_from_manuscript(text, start_word, end_word):
    pattern = rf"{re.escape(start_word)}(.*?){re.escape(end_word)}"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        return match.group(1).strip()
    return ""


def authors_from_manuscript(text):
    # Pattern to match: Name + number + ORCID + ORCID number
    # Handles names with particles like "de", "da", "do", "dos", "das"
    author_pattern = r"^([A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞß][a-zàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ]+(?:\s+(?:de|da|do|dos|das|e|van|von)?\s*[A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞß][a-zàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ]+)+)\d+\s+ORCID\s+\d{4}-\d{4}-\d{4}-\d{3}[\dX]"

    return re.findall(author_pattern, text, re.MULTILINE)


def item_1(text, max_authors=10):
    metadata = extract_metadata_from_manuscript(
        text, "ARTIGO ORIGINAL", "RESUMO")
    authors = authors_from_manuscript(metadata)

    status = "A"
    comments = ""
    if len(authors) > max_authors:
        status = "NA"
        comments = f"Autores: {', '.join(authors)}"

    return {"item": 1,
            "description": "A autoria é composta de, no máximo, 10 autores (exceção em multicêntricos)",
            "status": status,
            "comments": comments}


def item_2(text):
    metadata = extract_metadata_from_manuscript(
        text, "ARTIGO ORIGINAL", "RESUMO")
    authors = authors_from_manuscript(metadata)

    status = "A"
    invalid_authors = []

    for author in authors:
        words = author.split()
        if re.search(r"\.", author):
            invalid_authors.append(f"{author} (abreviação)")
            status = "NA"

        elif any(len(word) == 1 for word in words):
            invalid_authors.append(f"{author} (abreviação)")
            status = "NA"

        elif len(words) < 2:
            invalid_authors.append(f"{author} (nome único)")
            status = "NA"

    comments = "; ".join(invalid_authors) if invalid_authors else ""

    return {"item": 2,
            "description": "Nomes completos s/ abreviações",
            "status": status,
            "comments": comments}


def item_3(text):
    metadata = extract_metadata_from_manuscript(
        text, "ARTIGO ORIGINAL", "RESUMO")
    authors = authors_from_manuscript(metadata)

    orcid_pattern = r"ORCID\s+\d{4}-\d{4}-\d{4}-\d{3}[\dX]"
    orcids = re.findall(orcid_pattern, text, re.MULTILINE)

    lattes_pattern = r"Currículo lattes:\s*http://lattes\.cnpq\.br/\d+"
    lattes = re.findall(lattes_pattern, text, re.MULTILINE)

    status = "A"
    comments = []

    # Each author needs at least one ORCID or Lattes
    if len(orcids) < len(authors) and len(lattes) < len(authors):
        status = "NA"
        comments.append(
            f"{len(authors)} autores, {len(orcids)} ORCIDs, {len(lattes)} Lattes")

    return {"item": 3,
            "description": "Links ORCID e Lattes",
            "status": status,
            "comments": "; ".join(comments) if comments else ""}


def item_4(text):
    metadata = extract_metadata_from_manuscript(
        text, "ARTIGO ORIGINAL", "RESUMO")

    # Pattern to match affiliation lines:
    # Starts with digit(s), followed by institution name, city, state, country
    # Example: "1Universidade Estadual de Ponta Grossa, Ponta Grossa, Paraná, Brasil."
    # Must contain institution keywords and end with a location pattern
    affiliation_pattern = r"^\d+((?:Universidade|University|Instituto|Institute|Faculdade|Faculty|Escola|School|Hospital|Centro|Center|Centre|Fundação|Foundation|Laboratório|Laboratory)[^\.]+(?:,\s*[^,\.]+){1,}(?:,\s*(?:Brasil|Brazil|Argentina|Chile|Uruguai|Uruguay|Paraguai|Paraguay|Peru|Colômbia|Colombia|Venezuela|Equador|Ecuador|Bolívia|Bolivia|México|Mexico|Estados Unidos|United States|Portugal|Espanha|Spain|França|France|Itália|Italy|Reino Unido|United Kingdom|Alemanha|Germany|Canadá|Canada|Acre|Alagoas|Amapá|Amazonas|Bahia|Ceará|Distrito Federal|Espírito Santo|Goiás|Maranhão|Mato Grosso|Mato Grosso do Sul|Minas Gerais|Pará|Paraíba|Paraná|Pernambuco|Piauí|Rio de Janeiro|Rio Grande do Norte|Rio Grande do Sul|Rondônia|Roraima|Santa Catarina|São Paulo|Sergipe|Tocantins))\.?)$"
    
    affiliations = re.findall(affiliation_pattern, metadata, re.MULTILINE)
    affiliations = [aff.strip().rstrip('.') for aff in affiliations]

    valid_ufs = {
        'Acre', 'Alagoas', 'Amapá', 'Amazonas', 'Bahia', 'Ceará',
        'Distrito Federal', 'Espírito Santo', 'Goiás', 'Maranhão',
        'Mato Grosso', 'Mato Grosso do Sul', 'Minas Gerais', 'Pará',
        'Paraíba', 'Paraná', 'Pernambuco', 'Piauí', 'Rio de Janeiro',
        'Rio Grande do Norte', 'Rio Grande do Sul', 'Rondônia',
        'Roraima', 'Santa Catarina', 'São Paulo', 'Sergipe', 'Tocantins'
    }

    status = "A"
    comments = []
    
    if not affiliations:
        status = "NA"
        comments.append("Nenhuma afiliação encontrada")
    else:
        for affiliation in affiliations:
            has_brazilian_uf = any(uf in affiliation for uf in valid_ufs)
            
            if not has_brazilian_uf:
                status = "NA"
                comments.append(f"Afiliação sem cidade/UF válida: {affiliation}")

    return {"item": 4,
            "description": "Instituição/Afiliação (com cidade e UF)",
            "status": status,
            "comments": "; ".join(comments) if comments else ""}


# TODO: Refatorar para buscar texto do manuscrito
def item_5(text):
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

    return {"item": 5,
            "description": "Resumo da Biografia (categoria profissional e maior titulação)",
            "status": status,
            "comments": description}
