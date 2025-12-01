# 🧠 reci-checker

Sistema CLI para automatizar a verificação de conformidade de manuscritos científicos submetidos à Revista RECI.  
O projeto realiza a leitura de arquivos `.docx` e `.pdf`, extrai texto, imagens e propriedades básicas, e gera um relatório em JSON.

## 🚀 Requisitos

- Python 3.11 ou superior
- `pip` atualizado:

  ```bash
  python -m ensurepip --upgrade
  ```

- (Opcional, recomendado) ambiente virtual:

  ```bash
  # Criar o ambiente
  python -m venv .venv

  # Ativar no Windows
  .venv\Scripts\activate

  ```

## 📦 Instalação de dependências

Instale os pacotes necessários com:

```bash

python3 -m venv .venv

source .venv/bin/activate

pip install python-docx pymupdf pytest rich pydantic python-magic pdfminer.six tabulate ollama reportlab nltk

python3 src/main.py resources/Pronto.docx resources/teste_folha_de_rosto.docx

deactivate

```

**Explicação dos principais pacotes**

| Pacote           | Função                                                             |
|------------------|--------------------------------------------------------------------|
| `python-docx`    | Leitura e extração de texto e imagens de arquivos `.docx`.         |
| `pymupdf (fitz)` | Leitura de `.pdf`, contagem de páginas e imagens.                  |
| `pytest`         | Execução dos testes automatizados.                                 |
| `rich`           | Exibição de logs coloridos e formatados no terminal.               |
| `pydantic`       | Modelagem e validação de dados (usado nas próximas etapas).        |
| `python-magic`   | Detecção automática do tipo MIME do arquivo.                       |
| `pdfminer.six`   | Alternativa de parsing PDF para cenários complexos.                |

## 🧩 Estrutura do projeto

``` bash
reci-checker/
├─ programa.py
├─ pyproject.toml
├─ README.md
├─ src/
│  └─ io_reader.py
└─ tests/
   └─ test_cli.py
```

## ▶️ Como executar

Na pasta do projeto:

```bash
python programa.py caminho/arquivo.docx
# ou
python programa.py caminho/arquivo.pdf
```
