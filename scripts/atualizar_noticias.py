import os
import json
import time
from datetime import datetime
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def buscar_noticias_contabeis():
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    prompt = (
        f"Aja como um editor-chefe e jornalista sênior especializado em contabilidade e tributação no Brasil. "
        f"Hoje é dia {data_atual}. "
        "Utilize a ferramenta de pesquisa na web para buscar exatamente 12 notícias reais e recentes publicadas em portais "
        "como 'Portal Contábeis' (contabeis.com.br), 'Jornal Contábil' (jornalcontabil.com.br) ou 'Receita Federal'.\n\n"
        "OBRIGATÓRIO PARA CADA NOTÍCIA:\n"
        "1. O título e o conteúdo devem ser baseados na notícia real encontrada.\n"
        "2. No campo 'sourceUrl', você DEVE colocar a URL exata e direta da página daquela notícia específica obtida na pesquisa web (ex: https://www.contabeis.com.br/noticias/...).\n"
        "NUNCA utilize a URL genérica da página inicial (como apenas 'contabeis.com.br').\n\n"
        "Retorne a resposta EXATAMENTE no formato JSON puro, contendo um array de objetos com esta estrutura:\n"
        "[\n"
        "  {\n"
        "    \"id\": 1,\n"
        "    \"category\": \"Reforma Tributária\",\n"
        "    \"title\": \"Título real da notícia\",\n"
        "    \"summary\": \"Resumo objetivo de até 2 linhas.\",\n"
        "    \"content\": \"Conteúdo detalhado da notícia.\",\n"
        "    \"sourceUrl\": \"https://www.contabeis.com.br/noticias/link-exato-da-materia\"\n"
        "  }\n"
        "]"
    )
    
    max_tentativas = 5
    for tentativa in range(max_tentativas):
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config={
                    "tools": [{"google_search": {}}],
                    "response_mime_type": "application/json"
                }
            )
            return response.text
        except Exception as e:
            erro_str = str(e)
            if ("429" in erro_str or "503" in erro_str or "UNAVAILABLE" in erro_str) and tentativa < max_tentativas - 1:
                tempo_espera = (tentativa + 1) * 12
                print(f"Servidor ocupado ou limite atingido. Tentativa {tentativa+1}. Aguardando {tempo_espera}s...")
                time.sleep(tempo_espera)
            else:
                raise e

if __name__ == "__main__":
    try:
        print("Buscando notícias reais com links diretos na web...")
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
            
        print(f"Sucesso! {len(parsed_json)} notícias com links diretos salvas.")
    except Exception as e:
        print(f"ERRO CRÍTICO AO ATUALIZAR: {e}")
        raise e
