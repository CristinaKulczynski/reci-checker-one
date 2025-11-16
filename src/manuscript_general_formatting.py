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


# TODO: finish using the required sections
def item_14(manuscript_path):
    description = """Redigido na ortografia oficial, fonte Times New Roman 12, com espaçamento 1,5,
sem espaçamento entre parágrafos (exceto: Resumo, Figuras, Tabelas e Referências – espaçamento simples)."""
    status = "A"

    document = docx.Document(str(manuscript_path))
    font_info = []

    # Iterate through paragraphs
    for para in document.paragraphs:
        for run in para.runs:
            font_name = run.font.name
            if font_name:  # Check if a specific font name is set for the run
                font_info.append((run.text, font_name))
            else:
                # If run.font.name is None, it inherits from the paragraph style,
                # or document defaults. You might want to get the style's font name.
                style_font_name = para.style.font.name
                if style_font_name:
                    font_info.append((run.text, style_font_name))
                else:
                    # Fallback if no explicit font is found at run or paragraph style level
                    font_info.append(
                        (run.text, "Default/Inherited (No specific font found)"))

    # print(font_info)

    return {"item": 14,
            "description": description,
            "status": status,
            "comments": ""}


def item_17(manuscript_text):
    description = """Artigos de revisão: deverão ser divididos em Introdução, Métodos, Resultados e Discussão, Conclusão,
Agradecimentos (opcional) e Referências."""
    status = "NA"

    sections = get_sections(manuscript_text)
    section_names = {
        "INTRODUCTION": "Introdução",
        "METHODS": "Métodos",
        "RESULTS": "Resultados",
        "DISCUSSION": "Discussão",
        "CONCLUSION": "Conclusão",
        "REFERENCES": "Referências"
    }
    required_sections = ["INTRODUCTION", "METHODS",
                         "RESULTS", "DISCUSSION", "CONCLUSION"]
    if all(sections.get(section) for section in required_sections):
        status = "A"

    missing = [f"Não encontrado: {section_names.get(key)}\n"
               for key in required_sections if not sections.get(key)]
    comments = "".join(missing)

    return {"item": 17,
            "description": description,
            "status": status,
            "comments": comments}
