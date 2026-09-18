import os
import json
from datetime import datetime
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def buscar_noticias_contabeis():
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    prompt = (
        f"Aja como um editor-chefe e jornalista sênior especializado em contabilidade, tributação e finanças no Brasil. "
        f"Hoje é dia {data_atual}. "
        "Elabore exatamente 12 notícias altamente relevantes e recentes sobre o cenário contábil, fiscal e tributário brasileiro atual "
        "(incluindo Reforma Tributária, novidades da Receita Federal, obrigações acessórias, CFC e legislação fiscal).\n\n"
        "REQUISITO OBRIGATÓRIO PARA AS URLS: Para cada notícia, inclua o link URL direto correspondente na fonte original oficial ou portal especializado "
        "(por exemplo, URLs reais do Portal Contábeis em https://www.contabeis.com.br/noticias/... ou portais equivalentes). Nuse links genéricos.\n\n"
        "Retorne a resposta EXATAMENTE no formato JSON puro, contendo um array de objetos com esta estrutura exata:\n"
        "[\n"
        "  {\n"
        "    \"id\": 1,\n"
        "    \"category\": \"Reforma Tributária\",\n"
        "    \"title\": \"Título real e chamativo da notícia\",\n"
        "    \"summary\": \"Resumo objetivo e atrativo de até 2 linhas.\",\n"
        "    \"content\": \"Conteúdo detalhado explicando os desdobramentos da notícia, o contexto e os impactos práticos para os profissionais da contabilidade e empresas.\",\n"
        "    \"sourceUrl\": \"https://www.contabeis.com.br/noticias/exemplo\"\n"
        "  }\n"
        "]"
    )
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )
    return response.text

if __name__ == "__main__":
    try:
        print("Gerando lote de notícias atualizadas...")
        dados_json_str = buscar_noticias_contabeis()
        
        # Limpeza rigorosa de crases
        dados_limpos = dados_json_str.strip()
        if dados_limpos.startswith("```json"):
            dados_limpos = dados_limpos[7:]
        elif dados_limpos.startswith("```"):
            dados_limpos = dados_limpos[3:]
        if dados_limpos.endswith("```"):
            dados_limpos = dados_limpos[:-3]
        dados_limpos = dados_limpos.strip()

        parsed_json = json.loads(dados_limpos)

        # Salvar na raiz do repositório
        caminho_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'noticias.json'))
        with open(caminho_raiz, "w", encoding="utf-8") as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=4)
            
        print(f"Sucesso! {len(parsed_json)} notícias geradas e salvas com sucesso.")
    except Exception as e:
        print(f"ERRO CRÍTICO AO ATUALIZAR: {e}")
        raise e
