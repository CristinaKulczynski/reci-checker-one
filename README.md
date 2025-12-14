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

  ou 
  
  .\.venv\Scripts\Activate.ps1  

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

### Explicação dos principais pacotes

| Pacote (pip)  | Import no código | Finalidade principal                                                                 |
|---------------|------------------|--------------------------------------------------------------------------------------|
| `python-docx` | `docx`           | Leitura e manipulação de arquivos `.docx` (texto, tabelas, parágrafos, propriedades) |
| `nltk`        | `nltk`           | Processamento de linguagem natural (stopwords, detecção de idioma em títulos)       |
| `tabulate`    | `tabulate`       | Renderização da tabela de resultados no terminal                                    |
| `reportlab`   | `reportlab...`   | Geração do relatório final em PDF                                                   |
| `ollama`      | `ollama`         | Chamada ao LLM local (qwen2.5:7b-instruct) para validações semânticas               |

## 🧩 Estrutura do projeto

``` bash
reci-checker/
├─ pyproject.toml
├─ README.md
├─ src/
│  ├─ abstracts.py
│  ├─ cli.py
│  ├─ conclusion.py
│  ├─ cover_page.py
│  ├─ descriptors.py
│  ├─ docx_utils.py
│  ├─ main.py
│  ├─ manuscript_general_formatting.py
│  ├─ metadata.py
│  ├─ ollaminha.py
│  ├─ pdf_render.py
│  ├─ references.py
│  ├─ render.py
│  ├─ structure.py
│  ├─ tables_and_figures.py
│  └─ titles.py
└─ resources/
   └─ ... 
```

## ▶️ Como executar

Na pasta do projeto:

```bash
# Formato de execução:
python src/main.py <caminho/manuscrito.docx> <caminho/folha_de_rosto.docx>

# Exemplo de execução (utilizando os arquivos de exemplo):
python src/main.py resources/Texto.docx resources/teste_folha_de_rosto.docx

```


### Tabela com as ferramentas e bibliotecas utilizadas

| Item | Regra (Descrição) | Ferramenta Principal | Bibliotecas Utilizadas |
| :--- | :--- | :--- | :--- |
| **1** | A autoria é composta de, no máximo, 10 autores | Regex + Contagem de lista | `re` |
| **2** | Nomes completos s/ abreviações | Regex + Análise de String | `re` |
| **3** | Links ORCID e Lattes | Regex + Contagem | `re` |
| **4** | Instituição/Afiliação (com cidade e UF) | Regex + Listas de validação | `re` |
| **10** | Apresenta título, nome completo dos autores, afiliação, ORCID, Lattes, endereço, e-mail e contribuições (Checagem agregada da Folha de Rosto) | Regex + Agregação de resultados | `re` |
| **11** | Contribuições individuais: nome completo de cada autor (em negrito e por extenso), seguido das contribuições. | XML Parsing (Docx XML) | `xml.etree.ElementTree`, `re` |
| **12** | A identificação de autoria foi removida das Propriedades do Word | `docx` (acesso a Core Properties) | `docx` |
| **13** | Formato `.docx`, até 2MB | Python File System/Path | `pathlib` |
| **14** | Redigido na ortografia oficial, fonte Times New Roman 12, com espaçamento 1,5, sem espaçamento entre parágrafos. | Manual/Não Implementado | (Retorna status "-") |
| **16** | Artigos originais: seções Introdução, Métodos, Resultados, Discussão e Referências. | Regex (via `get_sections` para encontrar seções) | `re` |
| **18** | Apresenta no máximo 4.000 palavras (da Introdução à Discussão/Conclusão). | Regex (`get_sections`) + Contagem de palavras | `re` |
| **19** | Título com no máximo 15 palavras. | NLTK (detecção de idioma) + Regex | `re`, `nltk` |
| **20** | Título Principal em negrito, centralizado, fonte 12, e espaçamento simples. | `docx` (análise de formatação) | `docx` |
| **21** | Títulos secundários em itálico, centralizado, fonte 12, e espaçamento simples. | `docx` (análise de formatação) | `docx` |
| **23** | Títulos nos três idiomas (Português, Inglês e Espanhol). | NLTK (detecção de idioma) + Regex | `re`, `nltk` |
| **24** | RESUMO: Limite máximo de 250 palavras, em parágrafo único, com espaçamento simples. | XML Parsing (Docx XML) | `xml.etree.ElementTree`, `re` |
| **25** | RESUMO: Estrutura em Português (Justificativa e Objetivos, Métodos, Resultados e Conclusão - em negrito) | XML Parsing (Docx XML) | `xml.etree.ElementTree`, `re` |
| **26** | ABSTRACT: Estrutura em Inglês (Background and Objectives, Methods, Results e Conclusion - em negrito) | XML Parsing (Docx XML) | `xml.etree.ElementTree`, `re` |
| **27** | RESUMEN: Estrutura em Espanhol (Justificación y Objetivos, Métodos, Resultados e Conclusión - em negrito) | XML Parsing (Docx XML) | `xml.etree.ElementTree`, `re` |
| **28** | Artigos originais: Resumos estruturados nas 3 versões (agrega 25, 26, 27). | XML Parsing + Agregação | `xml.etree.ElementTree`, `re` |
| **30** | Rótulos 'Descritores', 'Keywords' e 'Palabras Clave' apresentados abaixo de cada resumo. | Regex (via `get_sections`) | `re` |
| **31** | Apresenta de três (3) a cinco (5) descritores (separados por ponto). | Regex (extração e contagem) | `re` |
| **32** | Rótulos 'Descritores', 'Keywords' e 'Palabras Clave' em negrito e primeira letra maiúscula. | XML Parsing (Docx XML) | `xml.etree.ElementTree`, `re` |
| **33** | Descritores (o conteúdo) em itálico, separados por ponto final. | XML Parsing (Docx XML) | `xml.etree.ElementTree`, `re` |
| **36** | Delineamento. | LMM (Ollama) + Prompt Engineering | `ollama`, `json`, `re` |
| **37** | Cenário estudado. | LMM (Ollama) + Prompt Engineering | `ollama`, `json`, `re` |
| **38** | População. | LMM (Ollama) + Prompt Engineering | `ollama`, `json`, `re` |
| **39** | Critérios de seleção (inclusão/exclusão). | LMM (Ollama) + Prompt Engineering | `ollama`, `json`, `re` |
| **40** | Fonte de dados. | LMM (Ollama) + Prompt Engineering | `ollama`, `json`, `re` |
| **41** | Período de coleta dos dados. | LMM (Ollama) + Prompt Engineering | `ollama`, `json`, `re` |
| **42** | Tipo de análise realizada. | LMM (Ollama) + Prompt Engineering | `ollama`, `json`, `re` |
| **53** | Artigos originais não levam conclusão em seção separada. | Regex (via `get_sections`) | `re` |
| **54** | Apresenta no máximo 5 figuras e/ou tabelas. | `docx` (contagem de tabelas e imagens) | `docx` |
| **58** | Tabelas são elaboradas no Word (não como imagens). | XML Parsing (Docx XML) | `xml.etree.ElementTree` |
| **61** | Legendas de figuras: abaixo, alinhadas à esquerda, fonte 10. | XML Parsing (Docx XML) | `xml.etree.ElementTree`, `re` |
| **66** | Referências nas Normas de Vancouver. | Regex (Complexa - validação de formato) | `re` |
| **69** | Referências: fonte 12, espaçamento simples, justificado. | XML Parsing (Docx XML) | `xml.etree.ElementTree`, `re` |
| **71** | Apresentam DOI nas referências ou endereço eletrônico. | Regex (DOI/URL) | `re` |
| **72** | Referencia-se o(s) autor(e)s pelo sobrenome, Iniciais s/ ponto. | Regex (Validação de formato de autor) | `re` |
| **73** | Citam pelo menos três nomes dos autores antes da expressão 'et al'. | Regex (Contagem de autores antes de `et al.`) | `re` |

### Autor

  [@CristinaKulczynski](https://github.com/CristinaKulczynski)
