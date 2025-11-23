import docx
from structure import get_sections


def item_12(manuscript_path):
    description = "A identificação de autoria do trabalho foi removida do arquivo e da opção Propriedades no Word"
    status = "A"

    document = docx.Document(str(manuscript_path))
    if document.core_properties.author:
        status = "NA"

    return {"item": 12,
            "description": description,
            "status": status,
            "comments": ""}


def item_13(manuscript_path):
    description = "Está em formato Microsoft Word, digitado em .docx, até 2MB"
    status = "A"

    if manuscript_path.suffix.lower() != ".docx" or manuscript_path.stat().st_size > 2 * 1024 * 1024:
        status = "NA"

    return {"item": 13,
            "description": description,
            "status": status,
            "comments": ""}


def item_14(manuscript_path):
    description = """Redigido na ortografia oficial, fonte Times New Roman 12, com espaçamento 1,5, sem espaçamento entre parágrafos (exceto: Resumo, Figuras, Tabelas e Referências – espaçamento simples)."""
    status = "-"

    return {"item": 14,
            "description": description,
            "status": status,
            "comments": ""}


def item_16(manuscript_text):
    description = "Artigos originais: deverão ser divididos nas seguintes seções: Introdução, Métodos, Resultados, Discussão, Agradecimentos (opcional) e Referências."
    status = "NA"

    sections = get_sections(manuscript_text)
    section_names = {
        "INTRODUCTION": "Introdução",
        "METHODS": "Métodos",
        "RESULTS": "Resultados",
        "DISCUSSION": "Discussão",
        "REFERENCES": "Referências"
    }
    required_sections = ["INTRODUCTION", "METHODS",
                         "RESULTS", "DISCUSSION", "REFERENCES"]
    if all(sections.get(section) for section in required_sections):
        status = "A"

    missing = [section_names.get(key)
               for key in required_sections if not sections.get(key)]
    comments = ""
    if missing:
        comments = f"Seções não encontradas: {', '.join(missing)}"

    return {"item": 16,
            "description": description,
            "status": status,
            "comments": comments}


def item_18(manuscript_text):
    description = "Apresenta no máximo 4.000 palavras (da Introdução à Discussão/Conclusão)."
    status = "A"

    sections = get_sections(manuscript_text)
    introduction_words = len((sections.get("INTRODUCTION") or "").split())
    methods_words = len((sections.get("METHODS") or "").split())
    results_words = len((sections.get("RESULTS") or "").split())
    discussion_words = len((sections.get("DISCUSSION") or "").split())
    total_words = introduction_words + methods_words + results_words + discussion_words
    if total_words > 4000:
        status = "NA"

    comments = f"Total de palavras ({total_words}): "
    comments += f"Introdução ({introduction_words}), "
    comments += f"Métodos ({methods_words}), "
    comments += f"Resultados ({results_words}), "
    comments += f"Discussão ({discussion_words})"

    return {"item": 18,
            "description": description,
            "status": status,
            "comments": comments}
