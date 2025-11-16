import xml.etree.ElementTree as ET
from docx_utils import docx_to_text
from metadata import *
from manuscript_general_formatting import *
from render import render_result
from cli import *

def main():
    manuscript_path, cover_page_path = init()

    manuscript_text = docx_to_text("manuscript", manuscript_path)
    cover_page_text = docx_to_text("cover_page", cover_page_path)

    # stripped_text = text.replace("\n", "").replace("\r", "")
    # characters_count = len(stripped_text.replace("\n", "").replace("\r", ""))
    # characters_no_space_count = sum(1 for caractere in stripped_text if not caractere.isspace())
    # pages_count = docx_pages_count(Path(__file__).resolve().parent / "app.xml")
    # images_count = docx_images_count(path)
    # sections = detectar_secoes(text)
    # metadata = validar_metadados(text)

    results = [item_1(cover_page_text),
               item_2(cover_page_text),
               item_3(cover_page_text),
               item_4(cover_page_text),
               item_5(cover_page_text),
               item_12(manuscript_path),
               item_13(manuscript_path),
               item_14(manuscript_path),
               item_17(manuscript_text)]

    render_result(results)

    return 0

if __name__ == "__main__":
    sys.exit(main())
