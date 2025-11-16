import re

AUTHORS_PATTERN = r"^Autor\s*:\s*(.*)"


def item_1(text, authors_pattern=AUTHORS_PATTERN, max_authors=10):
    authors = re.findall(authors_pattern, text, re.MULTILINE)

    status = "NA"
    if len(authors) <= max_authors:
        status = "A"

    return {"item": 1,
            "description": "A autoria é composta de, no máximo, 10 autores (exceção em multicêntricos)",
            "status": status,
            "comments": ""}


def item_2(text, authors_pattern=AUTHORS_PATTERN):
    authors = re.findall(authors_pattern, text, re.MULTILINE)

    status = "A"
    for author in authors:
        if (re.search(r"\.", author) or len(author.split()) < 2):
            status = "NA"

    return {"item": 2,
            "description": "Nomes completos s/ abreviações",
            "status": status,
            "comments": ""}


def item_3(text):
    authors = re.findall(AUTHORS_PATTERN, text, re.MULTILINE)

    orcid_pattern = r"ORCID:\s*https://orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[\dX]"
    orcids = re.findall(orcid_pattern, text, re.MULTILINE)

    lattes_pattern = r"Currículo lattes:\s*http://lattes\.cnpq\.br/\d+"
    lattes = re.findall(lattes_pattern, text, re.MULTILINE)

    status = "NA"
    if len(authors) == len(orcids) == len(lattes):
        status = "A"

    return {"item": 3,
            "description": "Links ORCID e Lattes",
            "status": status,
            "comments": ""}


def item_4(text):
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

    return {"item": 4,
            "description": "Instituição/Afiliação (com cidade e UF)",
            "status": status,
            "comments": ""}


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
