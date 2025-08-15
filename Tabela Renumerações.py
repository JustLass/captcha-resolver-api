# meu_scraper_principal.py

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from capsolver_solver import CaptchaSolver

# --- CONFIGURAÇÕES ---
CAPSOLVER_API_KEY = "CHAVE_API"
URL_DO_SITE = "https://www.senado.leg.br/transparencia/rh/servidores/detalhe.asp?fcodigo=3855180&fvinculo=1"

# --- INÍCIO DO SCRIPT ---
solver = CaptchaSolver(capsolver_api_key=CAPSOLVER_API_KEY)
driver = webdriver.Chrome()
driver.get(URL_DO_SITE)
time.sleep(3)

if solver.check_and_solve_captcha(driver):
    print("\n[Scraper Principal] CAPTCHA resolvido ou ausente. A submeter o formulário...")
    
    # --- LÓGICA DE CLIQUE ADICIONADA AQUI ---
    try:
        
        # Tenta clicar no botão do reCAPTCHA
        input('foi?')
        driver.find_element(By.CSS_SELECTOR, 'input[value="Visualizar remuneração"]').click()
        print("[Scraper Principal] Botão 'Visualizar remuneração' clicado.")
    except:
        try:
            # Se não encontrar, tenta clicar no botão do CAPTCHA de imagem
            driver.switch_to.frame('captcha')
            driver.find_element(By.ID, 'btnSubmit').click()
            print("[Scraper Principal] Botão 'Submit' do CAPTCHA de imagem clicado.")
            driver.switch_to.default_content()
        except Exception as e:
            print(f"[Scraper Principal] Nenhum botão de submissão encontrado para clicar: {e}")
    # --------------------------------

    print("\n[Scraper Principal] Página pronta! A iniciar a extração de dados...")
    # ... O seu código de scraping vem aqui ...

else:
    print("\n[Scraper Principal] A biblioteca não conseguiu resolver o CAPTCHA. A encerrar.")

time.sleep(10)
driver.quit()
