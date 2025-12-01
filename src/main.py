from docx_utils import docx_to_text
from metadata import *
from cover_page import *
from manuscript_general_formatting import *
from ollaminha import *
from tables_and_figures import *
from conclusion import *
from render import render_result
from cli import *
from references import *
from descriptors import *
from abstracts import *
from pdf_render import export_results_to_pdf
from titles import *


def main():
    manuscript_path, cover_page_path, xml_path = init()

    manuscript_text = docx_to_text("manuscript", manuscript_path)
    cover_page_text = docx_to_text("cover_page", cover_page_path)

    results = [
        item_1(manuscript_text),
        item_2(manuscript_text),
        item_3(manuscript_text),
        item_4(manuscript_text),
        item_10(cover_page_text),
        item_11(xml_path),
        item_12(manuscript_path),
        item_13(manuscript_path),
        item_14(manuscript_path),
        item_16(manuscript_text),
        item_18(manuscript_text),
        item_19(manuscript_text),
        item_20(manuscript_path),
        item_21(manuscript_path),
        item_23(manuscript_text),
        item_24(xml_path),
        *(item_28(xml_path)),
        item_30(manuscript_text),
        item_31(manuscript_text),
        item_32(xml_path),
        item_33(xml_path),
        item_53(manuscript_text),
        item_54(manuscript_path),
        item_58(xml_path),
        item_61(xml_path),
        item_66(manuscript_text),
        item_69(xml_path),
        item_71(manuscript_text),
        item_72(manuscript_text),
        item_73(manuscript_text),
    ]

    render_result(results)
    # export_results_to_pdf(results)
    # ollama_results = parse_ollama_results(item_generico(manuscript_text))
    # render_result(ollama_results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
