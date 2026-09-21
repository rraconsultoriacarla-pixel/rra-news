import os
import json
import time
from datetime import datetime
from google import genai
from google.genai.errors import APIError

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def buscar_noticias_contabeis():
    data_atual = datetime.now().strftime("%d/%m/%Y")

    prompt = (
        f"Aja como um editor-chefe e jornalista sênior especializado em contabilidade, tributação e finanças no Brasil. "
        f"Hoje é dia {data_atual}.\n\n"
        "Utilize a ferramenta de pesquisa na web para buscar exatamente 12 notícias reais, recentes e publicadas em portais "
        "confiáveis como 'Portal Contábeis' (contabeis.com.br), 'Jornal Contábil' (jornalcontabil.com.br) ou fontes equivalentes.\n\n"
        "REQUISITOS OBRIGATÓRIOS:\n"
        "1. O título, o resumo e o conteúdo devem ser baseados estritamente na notícia real encontrada na web.\n"
        "2. No campo 'sourceUrl', você DEVE colocar a URL exata e direta da página daquela notícia específica obtida na pesquisa web "
        "(ex: https://www.contabeis.com.br/noticias/...). NUNCA utilize URLs genéricas da página inicial.\n\n"
        "Retorne a resposta EXATAMENTE em formato JSON puro (sem blocos de código markdown como ```json), contendo um array de objetos com esta estrutura exata:\n"
        "[\n"
        "  {\n"
        "    \"id\": 1,\n"
        "    \"category\": \"Reforma Tributária\",\n"
        "    \"title\": \"Título real e chamativo da notícia\",\n"
        "    \"summary\": \"Resumo objetivo e atrativo de até 2 linhas.\",\n"
        "    \"content\": \"Conteúdo detalhado explicando os desdobramentos da notícia, o contexto e os impactos práticos para os profissionais da contabilidade e empresas.\",\n"
        "    \"sourceUrl\": \"[https://www.contabeis.com.br/noticias/exemplo-link-direto](https://www.contabeis.com.br/noticias/exemplo-link-direto)\"\n"
        "  }\n"
        "]"
    )

    max_tentativas = 5
    for tentativa in range(max_tentativas):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',  # Corrigido para um modelo válido e atual
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
                print(f"Servidor ocupado ou limite atingido. Tentativa {tentativa+1}/{max_tentativas}. Aguardando {tempo_espera}s...")
                time.sleep(tempo_espera)
            else:
                raise e

if __name__ == "__main__":
    try:
        print("Gerando lote de notícias atualizadas...")
        print("Buscando notícias reais com links diretos na web...")
        dados_json_str = buscar_noticias_contabeis()

        # Limpeza rigorosa de crases caso venham no texto
        dados_limpos = dados_json_str.strip()
        if dados_limpos.startswith("```json"):
            dados_limpos = dados_limpos[7:]
        elif dados_limpos.startswith("```"):
            dados_limpos = dados_limpos[3:]
        if dados_limpos.endswith("```"):
            dados_limpos = dados_limpos[:-3]
        dados_limpos = dados_limpos.strip()

        parsed_json = json.loads(dados_limpos)

        # Caminho onde o JSON será salvo no seu repositório do GitHub Pages / site
        caminho_raiz = "noticias.json" # Ajuste o caminho se necessário (ex: assets/noticias.json)
        
        with open(caminho_raiz, "w", encoding="utf-8") as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=4)

        print(f"Sucesso! {len(parsed_json)} notícias com links diretos salvas.")
    except Exception as e:
        print(f"ERRO CRÍTICO AO ATUALIZAR: {e}")
        raise e
