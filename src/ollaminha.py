import json
import ollama  # type: ignore
import re

DEFAULT_MODEL = "qwen2.5:7b-instruct"

PROMPT_METHODS = PROMPT_METHODS = """
ATUE COMO UM ESPECIALISTA EM METODOLOGIA CIENTÍFICA.
Analise a seção MÉTODOS do texto abaixo e extraia os dados solicitados em formato JSON.

TEXTO MÉTODOS:
\"\"\"{metodos}\"\"\"

DIRETRIZES GERAIS PARA OS COMENTÁRIOS:
- Seja DETALHADO: Use espostas bem curtas. Se a informação existir, transcreva os detalhes, datas e nomes exatos citados no texto.
- STATUS: Use "A" (Atende) se a informação estiver presente (mesmo que por sinônimos ou descrição de processo) e "NA" (Não Atende) se estiver totalmente ausente.

GERE APENAS O JSON ABAIXO, SEGUINDO AS REGRAS ESPECÍFICAS DE CADA CAMPO:

{{
    "1": {{
        "description": "Delineamento",
        "status": "A ou NA",
        "comentario": "Qual o termo EXATO usado pelos autores? Extraia literalmente (entre aspas) o que está no texto. REGRA CRÍTICA: É PROIBIDO inferir classificações. Se o texto diz 'time-series analysis', escreva 'time-series analysis'. NÃO substitua por termos guarda-chuva não citados."
    }},
    "2": {{
        "description": "Cenário",
        "status": "A ou NA",
        "comentario": "Descreva detalhadamente onde o estudo aconteceu: país, região, cidades, tipo de instituição ou contexto assistencial mencionado."
    }},
    "3": {{
        "description": "População",
        "status": "A ou NA",
        "comentario": "Descreva detalhadamente quem ou o que foi estudado (ex: 'populações indígenas das 10 localidades com maior número...', 'prontuários de pacientes com X')."
    }},
    "4": {{
        "description": "Critérios de Seleção",
        "status": "A ou NA", 
        "comentario": "Verifique se há critérios de inclusão/exclusão. REGRA DE OURO: Se o texto menciona uso de dados secundários (sistemas oficiais) ou a frase 'all vaccination schedules'/'all records', considere que ATENDE. Neste caso, o seu comentário deve ser EXATAMENTE: 'Estudo baseou-se na totalidade dos registros da base de dados mencionada'."
    }},
    "5": {{
        "description": "Fonte de Dados",
        "status": "A ou NA",
        "comentario": "De onde vieram os dados brutos? Cite nominalmente os sistemas (ex: SI-PNI, DataSUS, Prontuários Eletrônicos) ou o método de coleta (entrevistas, questionários). Escreva apenas o nome EXATO citado no texto. Nada a mais."
    }},
    "6": {{
        "description": "Período",
        "status": "A ou NA",
        "comentario": "Liste TODOS os intervalos de tempo citados (anos e datas completas). Se houver comparação (ex: pré e pós), liste as datas de todos os períodos mencionados separadamente.Extraia os pequenos trechos de texto que contenham essas informações (ex: 'de janeiro de 2010 a dezembro de 2020', 'entre 2015 e 2018', 'foi em 2015', '2 meses','mês janeiro até maio', '3 dias', Mostre expecificamente apenas as datas, não o texto entre elas)."
    }},
    "7": {{
        "description": "Análise",
        "status": "A ou NA",
        "comentario": "Descreva detalhadamente como os dados foram tratados. (Ex: cálculo de taxas por 100 mil hab., comparação entre períodos X e Y, testes estatísticos se houver). Lembre-se: Análise descritiva ou cálculo de taxas TAMBÉM conta como análise (Status A)."
    }}
}}
"""


def item_generico(methods_text: str, model: str = DEFAULT_MODEL) -> str:
    prompt = PROMPT_METHODS.format(metodos=methods_text)

    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0.0,
            "num_ctx": 8192
        }
    )

    content = response["message"]["content"].strip()

    try:
        json.loads(content)
    except json.JSONDecodeError:
        print("Resposta não está em JSON válido. Conteúdo bruto:")
        print(content)

    return content


def parse_ollama_results(ollama_text):
    item_mapping = {
        "1": {"item": 36, "description": "Delineamento."},
        "2": {"item": 37, "description": "Cenário estudado."},
        "3": {"item": 38, "description": "População."},
        "4": {"item": 39, "description": "Critérios de seleção (inclusão/exclusão)."},
        "5": {"item": 40, "description": "Fonte de dados."},
        "6": {"item": 41, "description": "Período de coleta dos dados."},
        "7": {"item": 42, "description": "Tipo de análise realizada."}
    }

    json_match = re.search(r'\{[\s\S]*\}', ollama_text)
    if not json_match:
        print("Warning: Could not extract JSON from Ollama results")
        return []

    try:
        json_data = json.loads(json_match.group(0))
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse JSON from Ollama results: {e}")
        return []

    results_list = []
    for key, value in json_data.items():
        if key in item_mapping:
            result = {
                "item": item_mapping[key]["item"],
                "description": item_mapping[key]["description"],
                "status": value.get("status", ""),
                "comments": value.get("comentario", "")
            }
            results_list.append(result)

    return results_list
