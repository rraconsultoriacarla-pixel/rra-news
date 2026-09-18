import os
import json
from datetime import datetime
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def buscar_noticias_contabeis():
    data_atual = datetime.now().strftime("%d/%m/%Y")
    prompt = f"""
    Aja como um editor-chefe e jornalista sênior especializado em contabilidade, tributação e finanças no Brasil.
    Hoje é dia {data_atual}. 
    Faça uma pesquisa profunda e abrangente na web utilizando fontes e portais de referência confiáveis como 'Portal Contábeis' (contabeis.com.br), 'Jornal Contábil' (jornalcontabil.com.br), 'IOB', 'Receita Federal' (gov.br/receitafederal) e 'CFC' (cfc.org.br).
    
    Busque e selecione exatamente 6 notícias recentes, relevantes e imperdíveis publicadas nos portais acima sobre: Reforma Tributária, novidades da Receita Federal, obrigações acessórias, CFC ou legislação fiscal.
    Certifique-se de incluir links reais e funcionais correspondentes às fontes originais em cada notícia.
    
    Retorne a resposta EXATAMENTE no formato JSON puro, sem blocos de markdown adicionais, contendo um array de objetos com esta estrutura exata:
    [
      {
        "id": 1,
        "category": "Reforma Tributária",
        "title": "Título real e chamativo da notícia",
        "summary": "Resumo objetivo e atrativo de até 2 linhas.",
        "content": "Conteúdo detalhado explicando os desdobramentos da notícia, o contexto e os impactos práticos para os profissionais da contabilidade e empresas.",
        "sourceUrl": "https://www.contabeis.com.br"
      }
    ]
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            "tools": [{"google_search": {}}],
            "response_mime_type": "application/json"
        }
    )
    return response.text

if __name__ == "__main__":
    try:
        dados_json_str = buscar_noticias_contabeis()
        
        # Limpeza rigorosa de eventuais crases de markdown
        dados_limpos = dados_json_str.strip()
        if dados_limpos.startswith("```json"):
            dados_limpos = dados_limpos[7:]
        elif dados_limpos.startswith("```"):
            dados_limpos = dados_limpos[3:]
        if dados_limpos.endswith("```"):
            dados_limpos = dados_limpos[:-3]
        dados_limpos = dados_limpos.strip()

        # Validar integridade do JSON retornado pela IA
        parsed_json = json.loads(dados_limpos)

        # Salvar na raiz do repositório para o GitHub Pages atualizar o site
        caminho_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'noticias.json'))
        with open(caminho_raiz, "w", encoding="utf-8") as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=4)
            
        print("Portal atualizado com sucesso com notícias frescas da web!")
    except Exception as e:
        print(f"Erro ao atualizar notícias da web: {e}")
