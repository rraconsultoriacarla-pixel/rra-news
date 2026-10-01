import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def buscar_noticias_rss():
    """
    Busca notícias contábeis e fiscais diretamente dos feeds RSS oficiais,
    garantindo a coleta de exatamente 30 notícias no total.
    """
    rss_urls = [
        "https://www.contabeis.com.br/noticias/rss/",
        "https://www.jornalcontabil.com.br/feed/"
    ]
    
    noticias_coletadas = []
    id_contador = 1
    limite_total = 30

    for url in rss_urls:
        if len(noticias_coletadas) >= limite_total:
            break
            
        try:
            print(f"Buscando notícias em: {url}")
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                channel = root.find('channel')
                
                if channel is not None:
                    items = channel.findall('item')
                    for item in items:
                        if len(noticias_coletadas) >= limite_total:
                            break
                            
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        desc_elem = item.find('description')
                        
                        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Sem Título"
                        link = link_elem.text.strip() if link_elem is not None and link_elem.text else "#"
                        
                        summary = "Atualização recente sobre o cenário contábil, fiscal e tributário brasileiro."
                        if desc_elem is not None and desc_elem.text:
                            raw_desc = desc_elem.text
                            import re
                            clean_desc = re.sub('<[^<]+?>', '', raw_desc)
                            if len(clean_desc.strip()) > 10:
                                summary = clean_desc.strip()[:180] + "..."

                        category = "Geral"
                        t_lower = title.lower()
                        if "reforma" in t_lower or "tributári" in t_lower or "ibs" in t_lower or "cbs" in t_lower:
                            category = "Reforma Tributária"
                        elif "fiscal" in t_lower or "imposto" in t_lower or "receita federal" in t_lower or "das" in t_lower:
                            category = "Fiscal"
                        elif "contábil" in t_lower or "contabilidade" in t_lower or "cfc" in t_lower:
                            category = "Contábil"
                        elif "lei" in t_lower or "decreto" in t_lower or "norma" in t_lower or "trabalhista" in t_lower:
                            category = "Legislação"
                        elif "auditoria" in t_lower:
                            category = "Auditoria"
                        else:
                            category = "Dicas"

                        noticias_coletadas.append({
                            "id": id_contador,
                            "category": category,
                            "title": title,
                            "summary": summary,
                            "content": "Detalhes completos disponíveis na fonte original.",
                            "sourceUrl": link
                        })
                        id_contador += 1
        except Exception as e:
            print(f"Erro ao processar o feed {url}: {e}")

    return noticias_coletadas[:limite_total]

if __name__ == "__main__":
    try:
        print("Iniciando coleta automática de notícias via RSS...")
        lista_noticias = buscar_noticias_rss()

        if not lista_noticias:
            raise Exception("Nenhuma notícia foi encontrada nos feeds RSS.")

        for idx, noticia in enumerate(lista_noticias, start=1):
            noticia["id"] = idx

        caminho_raiz = "noticias.json"  
        
        with open(caminho_raiz, "w", encoding="utf-8") as f:
            json.dump(lista_noticias, f, ensure_ascii=False, indent=4)

        print(f"Sucesso! {len(lista_noticias)} notícias coletadas e salvas em {caminho_raiz}.")
    except Exception as e:
        print(f"ERRO CRÍTICO AO ATUALIZAR: {e}")
        raise e
