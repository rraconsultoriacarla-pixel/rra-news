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
        "Faça uma pesquisa exaustiva na web utilizando fontes e portais de referência confiáveis como 'Portal Contábeis' (contabeis.com.br), "
        "'Jornal Contábil' (jornalcontabil.com.br), 'IOB', 'Receita Federal' (gov.br/receitafederal) e 'CFC' (cfc.org.br).\n\n"
        "Busque e selecione exatamente 12 notícias recentes, relevantes e imperdíveis publicadas nestes portais sobre: "
        "Reforma Tributária, novidades da Receita Federal, obrigações acessórias, CFC, auditoria ou legislação fiscal.\n"
        "Certifique-se de incluir links reais e funcionais correspondentes às fontes originais em cada notícia.\n\n"
        "Retorne a resposta EXATAMENTE no formato JSON puro, contendo um array de objetos com esta estrutura exata:\n"
        "[\n"
        "  {\n"
        "    \"id\": 1,\n"
        "    \"category\": \"Reforma Tributária\",\n"
        "    \"title\": \"Título real e chamativo da notícia\",\n"
        "    \"summary\": \"Resumo objetivo e atrativo de até 2 linhas.\",\n"
        "    \"content\": \"Conteúdo detalhado explicando os desdobramentos da notícia, o contexto e os impactos práticos para os profissionais da contabilidade e empresas.\",\n"
        "    \"sourceUrl\": \"https://www.contabeis.com.br\"\n"
        "  }\n"
        "]"
    )
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
        config={
            "tools": [{"google_search": {}}],
            "response_mime_type": "application/json"
        }
    )
    return response.text

if __name__ == "__main__":
    try:
        print("Iniciando busca de notícias na web com Gemini 3.6...")
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
            
        print(f"Sucesso! {len(parsed_json)} notícias fresquinhas salvas em {caminho_raiz}")
    except Exception as e:
        print(f"ERRO CRÍTICO AO ATUALIZAR: {e}")
        raise e
