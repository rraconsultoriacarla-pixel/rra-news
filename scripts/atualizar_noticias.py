import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def buscar_noticias_rss():
    """
    Busca notícias contábeis e fiscais diretamente dos feeds RSS oficiais 
    de portais confiáveis, eliminando a dependência de IA e cotas de API.
    """
    # URLs de Feeds RSS públicos de portais de contabilidade
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
                # Parse do XML/RSS
                root = ET.fromstring(response.content)
                channel = root.find('channel')
                
                if channel is not None:
                    items = channel.findall('item')
                    for item in items[:8]: # Pega até 8 notícias por portal
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        desc_elem = item.find('description')
                        
                        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Sem Título"
                        link = link_elem.text.strip() if link_elem is not None and link_elem.text else "#"
                        
                        # Limpa tags HTML básicas do resumo se houver
                        summary = "Atualização recente sobre o cenário contábil, fiscal e tributário brasileiro."
                        if desc_elem is not None and desc_elem.text:
                            raw_desc = desc_elem.text
                            # Remove tags HTML simples
                            import re
                            clean_desc = re.sub('<[^<]+?>', '', raw_desc)
                            if len(clean_desc.strip()) > 10:
                                summary = clean_desc.strip()[:180] + "..."

                        # Classificação automática simples por palavras-chave no título
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
                            "content": f"Detalhes completos sobre esta matéria podem ser acessados diretamente na fonte original. Esta notícia faz parte das atualizações diárias automatizadas do portal RRAnews para manter os profissionais informados sobre as mudanças nas áreas contábil e fiscal.",
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

        # Limita a um total consolidado de 12 a 16 notícias
        lista_noticias = lista_noticias[:16]

        # Salva o JSON na raiz do repositório para o site ler
        caminho_raiz = "noticias.json"  
        
        with open(caminho_raiz, "w", encoding="utf-8") as f:
            json.dump(lista_noticias, f, ensure_ascii=False, indent=4)

        print(f"Sucesso! {len(lista_noticias)} notícias coletadas e salvas em {caminho_raiz}.")
    except Exception as e:
        print(f"ERRO CRÍTICO AO ATUALIZAR: {e}")
        raise e
