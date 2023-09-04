# libs
import asyncio
from playwright.async_api import async_playwright
import logging
import os
from time import sleep
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pandas as pd

base = {"url": [], "estabelecimento": []}
async def main():
    # Instanciando e executando o processo de coleta
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Rodando a automação no browser
        await page.goto("https://www.google.com/search?q=site:goomer.app+inurl:https://*&hl=pt-BR")
        await page.wait_for_selector('//*[@id="rso"]/div[*]/div/div/div[1]/div/div')
        
        # Aguardando a página atualizar
        await page.wait_for_load_state()

        # Obtendo o HTML da página atualizada
        html = await page.content()

        # Fazendo o parse do html
        soup = BeautifulSoup(html, "html.parser")

        # Localizando todos os elementos das divs
        # divs = soup.find_all('//*[@id="rso"]/div[*]/div/div/div[1]/div/div')
        divs = soup.select('#rso > div > div > div > div:nth-of-type(1) > div > div')

        for div in divs:
            try:
                base['url'].append(div.find("a").get('href'))
                base['estabelecimento'].append(div.find("h3").text)
            except Exception as e:
                pass

        # Clica no botão "Próxima página"
        try:
            # Espera até que o botão "Próxima página" esteja disponível
            await page.wait_for_selector('//*[@id="botstuff"]/div/div[3]/table/tbody/tr/td[5]').click()
            # await page.click('//*[@id="pnnext"]/span[2]')
        except:
            print('Busca finalizada.')

        await context.close()
        await browser.close()

    dados = pd.DataFrame(base)
    dados.to_csv("./lista_cardapios_goomer.csv", index=False, sep=";")
# Executa o loop assíncrono
asyncio.get_event_loop().run_until_complete(main())