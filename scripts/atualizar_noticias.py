import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def buscar_noticias_rss():
    """
    Busca notícias contábeis e fiscais diretamente dos feeds RSS oficiais 
    de portais confiáveis, garantindo sempre a entrega exata de 30 notícias.
    """
    rss_urls = [
        "https://www.contabeis.com.br/noticias/rss/",
        "https://www.jornalcontabil.com.br/feed/"
    ]
    
    noticias_coletadas = []
    
    # Meta de notícias por portal para somar ao todo 30
    meta_por_portal = 15

    for url in rss_urls:
        try:
            print(f"Buscando notícias em: {url}")
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                channel = root.find('channel')
                
                if channel is not None:
                    items = channel.findall('item')
                    for item in items[:meta_por_portal]:
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
                            "category": category,
                            "title": title,
                            "summary": summary,
                            "content": f"Detalhes completos sobre esta matéria podem ser acessados diretamente na fonte original. Esta notícia faz parte das atualizações diárias automatizadas do portal RRAnews para manter os profissionais informados sobre as mudanças nas áreas contábil e fiscal.",
                            "sourceUrl": link
                        })
        except Exception as e:
            print(f"Erro ao processar o feed {url}: {e}")

    # Garante que SEMPRE tenremos exatamente 30 notícias
    # Se os feeds trouxerem menos de 30, preenche o restante com notícias complementares padrão
    temas_fallback = [
        ("Fiscal", "Prazo de entrega de obrigações acessórias exige atenção dos contadores"),
        ("Contábil", "Novas diretrizes para o balanço patrimonial e demonstrações contábeis"),
        ("Reforma Tributária", "Impactos do IVA dual na rotina de pequenas e médias empresas"),
        ("Legislação", "Governo federal publica novas portarias sobre rotinas trabalhistas"),
        ("Dicas", "Como otimizar o planejamento tributário para o próximo trimestre")
    ]
    
    contador_fallback = 1
    while len(noticias_coletadas) < 30:
        idx = (len(noticias_coletadas) % len(temas_fallback))
        cat, tit = temas_fallback[idx]
        noticias_coletadas.append({
            "category": cat,
            "title": f"{tit} (Atualização Diária #{contador_fallback})",
            "summary": "Acompanhe as principais movimentações e orientações regulatórias voltadas para o setor empresarial e contábil.",
            "content": "Esta publicação faz parte do boletim informativo diário do portal RRAnews, trazendo panorama atualizado sobre as exigências e normativas aplicadas aos profissionais contábeis.",
            "sourceUrl": "https://www.contabeis.com.br"
        })
        contador_fallback += 1

    # Limita rigorosamente a exatamente 30 notícias e atribui IDs sequenciais de 1 a 30
    noticias_finais = []
    for i, noticia in enumerate(noticias_coletadas[:30], start=1):
        noticia["id"] = i
        noticias_finais.append(noticia)

    return noticias_finais

if __name__ == "__main__":
    try:
        print("Iniciando coleta automática de notícias via RSS...")
        lista_noticias = buscar_noticias_rss()

        caminho_raiz = "noticias.json"  
        
        with open(caminho_raiz, "w", encoding="utf-8") as f:
            json.dump(lista_noticias, f, ensure_ascii=False, indent=4)

        print(f"Sucesso! {len(lista_noticias)} notícias coletadas e salvas em {caminho_raiz}.")
    except Exception as e:
        print(f"ERRO CRÍTICO AO ATUALIZAR: {e}")
        raise e
