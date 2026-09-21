import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import re

def buscar_noticias_rss():
    rss_urls = [
        "https://www.contabeis.com.br/noticias/rss/",
        "https://www.jornalcontabil.com.br/feed/"
    ]
    
    noticias_coletadas = []
    id_contador = 1

    for url in rss_urls:
        try:
            print(f"Buscando notícias em: {url}")
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                channel = root.find('channel')
                
                if channel is not None:
                    items = channel.findall('item')
                    for item in items[:10]:
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        desc_elem = item.find('description')
                        
                        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Sem Título"
                        link = link_elem.text.strip() if link_elem is not None and link_elem.text else "#"
                        
                        summary = "Atualização recente sobre o cenário contábil e fiscal brasileiro."
                        if desc_elem is not None and desc_elem.text:
                            clean_desc = re.sub('<[^<]+?>', '', desc_elem.text)
                            if len(clean_desc.strip()) > 10:
                                summary = clean_desc.strip()[:180] + "..."

                        # Padronização restrita para bater com os botões do site:
                        # 'Reforma Tributária', 'Fiscal', 'Contábil', 'Legislação', 'Auditoria', 'Dicas'
                        category = "Fiscal" # Categoria padrão caso não encaixe nas outras
                        t_lower = title.lower()
                        
                        if "reforma" in t_lower or "tributári" in t_lower or "ibs" in t_lower or "cbs" in t_lower:
                            category = "Reforma Tributária"
                        elif "contábil" in t_lower or "contabilidade" in t_lower or "balanço" in t_lower or "escritório" in t_lower:
                            category = "Contábil"
                        elif "auditoria" in t_lower:
                            category = "Auditoria"
                        elif "lei" in t_lower or "decreto" in t_lower or "norma" in t_lower or "trabalhista" in t_lower or "clt" in t_lower:
                            category = "Legislação"
                        elif "dica" in t_lower or "guia" in t_lower or "passo" in t_lower:
                            category = "Dicas"
                        else:
                            category = "Fiscal"

                        noticias_coletadas.append({
                            "id": id_contador,
                            "category": category,
                            "title": title,
                            "summary": summary,
                            "content": f"Detalhes completos sobre esta matéria podem ser acessados diretamente na fonte original. Esta notícia faz parte das atualizações diárias automatizadas do portal RRAnews.",
                            "sourceUrl": link
                        })
                        id_contador += 1
        except Exception as e:
            print(f"Erro ao processar o feed {url}: {e}")

    return noticias_coletadas

if __name__ == "__main__":
    try:
        print("Iniciando coleta automática de notícias via RSS...")
        lista_noticias = buscar_noticias_rss()

        if not lista_noticias:
            raise Exception("Nenhuma notícia foi encontrada nos feeds RSS.")

        lista_noticias = lista_noticias[:16]

        with open("noticias.json", "w", encoding="utf-8") as f:
            json.dump(lista_noticias, f, ensure_ascii=False, indent=4)

        print(f"Sucesso! {len(lista_noticias)} notícias coletadas e salvas.")
    except Exception as e:
        print(f"ERRO CRÍTICO AO ATUALIZAR: {e}")
        raise e
