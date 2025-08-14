import time
from selenium import webdriver
from capsolver_solver import CaptchaSolver

# --- CONFIGURAÇÕES ---

CAPSOLVER_API_KEY = "CHAVE-API"
URL_DO_SITE = "https://www.senado.leg.br/transparencia/rh/servidores/detalhe.asp?fcodigo=3855180&fvinculo=1"

# --- INÍCIO DO SCRIPT ---

# Inicialize o resolvedor
try:
    solver = CaptchaSolver(capsolver_api_key=CAPSOLVER_API_KEY)
except ValueError as e:
    print(f"Erro de configuração: {e}")
    exit()

# Inicie o seu driver do Selenium como de costume
driver = webdriver.Chrome()
driver.get(URL_DO_SITE)
time.sleep(3)


if solver.check_and_solve_captcha(driver):
    # Se chegou aqui, a página está livre de CAPTCHA e pronta para o scraping
    print("\n[Scraper Principal] Página pronta! A iniciar a extração de dados...")
    
    #
    # COLOQUE O SEU CÓDIGO DE SCRAPING AQUI
    # Exemplo: extrair o nome do servidor
    #
    try:
        time.sleep(5) # Espera extra para os dados carregarem
        nome_servidor = driver.find_element(By.XPATH, "//td[text()='Nome']/following-sibling::td").text
        print(f"Nome do servidor encontrado: {nome_servidor}")
    except Exception as e:
        print(f"Não foi possível extrair os dados. Erro: {e}")

else:
    # Se a função retornou False, algo correu mal
    print("\n[Scraper Principal] A biblioteca não conseguiu resolver o CAPTCHA. A encerrar.")