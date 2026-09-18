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
        with open("noticias.json", "w", encoding="utf-8") as f:
            f.write(dados_json_str)
        print("Arquivo noticias.json atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar notícias: {e}")
