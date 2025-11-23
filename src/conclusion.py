from structure import get_sections


def item_53(manuscript_text):
    description = "Artigos originais não levam conclusão em seção separada, sendo incorporada ao último parágrafo da discussão; Artigos de revisão levam conclusão em seção separada."
    status = "A"

    sections = get_sections(manuscript_text)
    if "CONCLUSION" in sections:
        status = "NA"

    return {"item": 53,
            "description": description,
            "status": status,
            "comments": ""}
