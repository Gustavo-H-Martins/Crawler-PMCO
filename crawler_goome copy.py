# libs
import asyncio
from playwright.sync_api import sync_playwright
import logging
import os
from time import sleep
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pandas as pd

def coleta_url_titulo(consulta:str="site:goomer.app+inurl:https://*&hl=pt-BR"):
    # Inicia o navegador e página
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Define o contexto
        context = browser.new_context()
        page = context.new_page()

        # Abre o navegador com a página do Google Search
        page.goto("https://www.google.com")

        # Digita e pesquisa o valor procurado
        page.fill("input[name=q]", consulta)
        page.press("input[name=q]","Enter")
        
        # Dicionário com os campos a serem consumidos no crawler
        resultado = {"url" : [], "titulo": []}

        # Aguardando a página atualizar
        page.wait_for_load_state()

        # Loop para passar de página em página do resultdo da pesquisa
        while True:
            page.wait_for_selector("#search")

            # Pega os links e títulos dos resultadso
            links = page.query_selector_all("#search a")
            for link in links:
                url = link.get_attribute("href")
                titulo = link.inner_text()
                if url and titulo:
                    resultado["url"].append(url) ,resultado["titulo"].append(titulo)
            
            # Verifica se há um botão para próxima página
            proxima_pagina = page.query_selector("#pnnext")
            if proxima_pagina:
                # Clica no botão e espera atualizar
                proxima_pagina.click()
                page.wait_for_load_state()
            else:
                # Se não houver a presença do botão mais na página
                break
        
        browser.close()

        # Retorna o resultado da consulta
        return resultado

# Chamando a função
dados = pd.DataFrame(coleta_url_titulo())

# Salvando em um csv
dados.to_csv("./lista_cardapios_goomer.csv", index=False, sep=";")