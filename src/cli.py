import argparse
from pathlib import Path
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("reci-checker")

def validate_manuscript(manuscript_path):
    path = Path(manuscript_path)
    if not path.is_file():
        logger.error("Manuscrito não encontrado: %s", manuscript_path)
        sys.exit(2)

    extension = path.suffix.lower()
    if extension not in [".docx"]:
        logger.error("Formato inválido (%s). Use apenas .docx ou .pdf", extension)
        sys.exit(3)
        
def validate_cover_page(cover_page_path):
    path = Path(cover_page_path)
    if not path.is_file():
        logger.error("Folha de rosto não encontrado: %s", cover_page_path)
        sys.exit(2)

    extension = path.suffix.lower()
    if extension not in [".docx"]:
        logger.error("Formato inválido (%s). Use apenas .docx", extension)
        sys.exit(3)

def init():
    parser = argparse.ArgumentParser()
    parser.add_argument("manuscrito", help="Caminho para o manuscrito (.docx)")
    parser.add_argument("folha_de_rosto", help="Caminho para a folha de rosto (.docx)")
    args = parser.parse_args()

    manuscript_path = Path(args.manuscrito)
    validate_manuscript(manuscript_path);
    cover_page_path = Path(args.folha_de_rosto)
    validate_cover_page(cover_page_path);

    xml_path = Path(__file__).resolve().parent.parent / \
        "resources" / "xml" / "manuscript_document.xml"

    return manuscript_path, cover_page_path, xml_path
