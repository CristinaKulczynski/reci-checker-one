import re
from typing import Dict


def get_sections(texto: str) -> Dict[str, str]:
    texto = re.sub(r"\s+", " ", texto.strip())

    patterns = {
        "TÍTULO / ORIGINAL ARTICLE": r"(?:(?:^|[\n\r\s])(?:ARTIGO\s*ORIGINAL|ORIGINAL\s*ARTICLE|T[ÍI]TULO))(?=\s|$)",
        "RESUMO": r"(?:(?:^|[\n\r\s])RESUMO)(?=\s|$)",
        "ABSTRACT": r"(?:(?:^|[\n\r\s])ABSTRACT)(?=\s|$)",
        "RESUMEN": r"(?:(?:^|[\n\r\s])RESUMEN)(?=\s|$)",
        "RESUMEN": r"(?:^|[\.\n])\s*RESUMEN\s+(?=[A-Z])",
        "INTRODUCTION": r"(?:^|[\.\n])\s*INTRODU[CÇ][AÃ]O\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])|(?:^|[\.\n])\s*INTRODUCTION\s+(?=[A-Z])",
        "METHODS": r"(?:^|[\.\n])\s*M[ÉE]TODOS?\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])|(?:^|[\.\n])\s*METHODS?\s+(?=[A-Z])",
        "RESULTS": r"(?:^|[\.\n])\s*RESULTADOS?\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])|(?:^|[\.\n])\s*RESULTS?\s+(?=[A-Z])",
        "DISCUSSION": r"(?:^|[\.\n])\s*DISCUSS[AÃ]O\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])|(?:^|[\.\n])\s*DISCUSSION\s+(?=[A-Z])",
        "CONCLUSION": r"(?:^|[\.\n])\s*CONCLUS[AÃ]O\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])|(?:^|[\.\n])\s*CONCLUSION\s+(?=[A-Z])|(?:^|[\.\n])\s*CONSIDERA[CÇ][OÕ]ES\s*FINAIS\s+(?=[A-Z])",
        "REFERENCES": r"(?:^|[\.\n])\s*REFER[ÊE]NCIAS\s*(?=$|\s)|(?:^|[\.\n])\s*REFERENCE[S]?\s*(?=$|\s)|(?:^|[\.\n])\s*BIBLIOGRAFIA\s*(?=$|\s)",
    }

    indices = []
    for nome, regex in patterns.items():
        for m in re.finditer(regex, texto, flags=re.IGNORECASE):
            indices.append((m.start(), nome))
    indices.sort(key=lambda x: x[0])

    secoes = {}
    for i, (pos, nome) in enumerate(indices):
        fim = indices[i + 1][0] if i + 1 < len(indices) else len(texto)
        bloco = texto[pos:fim].strip()
        secoes[nome] = bloco

    return secoes


# Execução isolada: python src/structure.py caminho.txt
if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Uso: python src/structure.py caminho_arquivo.txt")
        sys.exit(1)

    caminho = Path(sys.argv[1])
    if not caminho.is_file():
        print("Arquivo não encontrado.")
        sys.exit(1)

    conteudo = caminho.read_text(encoding="utf-8", errors="ignore")
    secoes = get_sections(conteudo)

    for nome, trecho in secoes.items():
        print(f"\n=== {nome} ===")
        print(trecho[:600], "..." if len(trecho) > 600 else "")
