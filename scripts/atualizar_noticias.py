import os
import json
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def buscar_noticias_contabeis():
    prompt = """
    Aja como um jornalista contábil e fiscal sênior no Brasil. 
    Pesquise e liste exatamente 6 das notícias mais recentes e importantes sobre contabilidade, 
    reforma tributária, Receita Federal, CFC ou legislação fiscal publicadas recentemente.
    
    Retorne a resposta EXATAMENTE no formato JSON puro, sem textos adicionais, contendo um array de objetos com esta estrutura exata:
    [
      {
        "id": 1,
        "category": "Reforma Tributária",
        "title": "Título da notícia",
        "summary": "Resumo curto de até 2 linhas.",
        "content": "Conteúdo detalhado explicando a notícia e os impactos práticos para os profissionais e empresas.",
        "sourceUrl": "https://www.gov.br"
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
        
        # Limpar eventuais crases de markdown caso o modelo as inclua
        dados_limpos = dados_json_str.strip()
        if dados_limpos.startswith("```json"):
            dados_limpos = dados_limpos[7:]
        elif dados_limpos.startswith("```"):
            dados_limpos = dados_limpos[3:]
        if dados_limpos.endswith("```"):
            dados_limpos = dados_limpos[:-3]
        dados_limpos = dados_limpos.strip()

        # Validar se é um JSON válido antes de salvar
        parsed_json = json.loads(dados_limpos)

        # Salvar na raiz do repositório (garantindo o caminho correto a partir da pasta scripts)
        caminho_raiz = os.path.join(os.path.dirname(__file__), '..', 'noticias.json')
        with open(caminho_raiz, "w", encoding="utf-8") as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=4)
            
        print("Arquivo noticias.json atualizado e validado com sucesso na raiz!")
    except Exception as e:
        print(f"Erro ao atualizar notícias: {e}")
