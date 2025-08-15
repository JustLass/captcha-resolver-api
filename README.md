

# Resolvedor de CAPTCHA com Capsolver (Modular)

Este projeto é um resolvedor de CAPTCHA modular, focado na utilização da API do [Capsolver](https://www.capsolver.com/) para contornar desafios de CAPTCHA em scripts de web scraping com Selenium. A principal funcionalidade é a detecção e resolução automática de `reCAPTCHA v2`.

A abordagem modular permite que esta classe seja facilmente integrada em qualquer projeto existente, sem a necessidade de modificar a lógica principal do seu scraper.

## Funcionalidades Principais

  - **Integração com a API do Capsolver:** Conecta-se à API do Capsolver para delegar a resolução do CAPTCHA.
  - **Detecção Automática de `reCAPTCHA v2`:** Analisa a página HTML para identificar a presença de `reCAPTCHA v2` com base em `iframes` e `data-sitekey`.
  - **Injeção de Token de Solução:** Após a resolução bem-sucedida pela API, injeta o token de solução (`g-recaptcha-response`) na página, permitindo a submissão do formulário.
  - **Tratamento de Erros:** Lida com falhas na comunicação com a API ou timeouts para garantir que o script não seja interrompido abruptamente.

## Estrutura do Projeto

  - **`capsolver_solver.py`:** A biblioteca principal que contém a classe `CaptchaSolver`. Esta classe encapsula toda a lógica para se comunicar com a API do Capsolver e manipular o DOM da página para injetar o token de solução.

## Pré-requisitos

Para usar esta biblioteca, você precisará ter o seguinte instalado:

  - **Python 3.x**
  - **Bibliotecas Python:**
      - `selenium`: Para automação do navegador.
      - `requests`: Para comunicação com a API do Capsolver.

Você pode instalar as dependências necessárias com `pip`:

```bash
pip install selenium requests
```

## Configuração

1.  **Obtenha sua Chave da API do Capsolver:**

      - Acesse o painel do seu [Capsolver](https://www.capsolver.com/) e obtenha sua chave de API.
      - Esta chave é necessária para autenticar e usar o serviço de resolução de CAPTCHA.

2.  **Webdriver (Selenium):**

      - Certifique-se de que você tem o driver do seu navegador (como o `chromedriver` para Google Chrome) instalado e acessível pelo seu `PATH`.

## Como Usar

A classe `CaptchaSolver` foi projetada para ser simples de usar. Siga os passos abaixo para integrá-la ao seu script de web scraping:

1.  **Instancie a Classe `CaptchaSolver`:**

      - Importe a classe do arquivo `capsolver_solver.py`.
      - Crie uma instância da classe, passando sua chave de API como argumento.

2.  **Chame o Método `check_and_solve_captcha`:**

      - Após carregar a página que pode conter um CAPTCHA, chame este método, passando o objeto `driver` do Selenium.
      - O método cuidará de toda a lógica de detecção, resolução e injeção do token.

### Exemplo de Uso

O seguinte trecho de código demonstra a integração da classe `CaptchaSolver` em um script de scraping com Selenium:

```python
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from capsolver_solver import CaptchaSolver

# --- CONFIGURAÇÕES ---
# IMPORTANTE: Substitua "SUA_CHAVE_API_CAPSOLVER" pela sua chave real
CAPSOLVER_API_KEY = "SUA_CHAVE_API_CAPSOLVER"
URL_DO_SITE = "https://www.senado.leg.br/transparencia/rh/servidores/detalhe.asp?fcodigo=3855180&fvinculo=1"

# --- INÍCIO DO SCRIPT ---
# 1. Instanciar a classe com a sua chave de API
solver = CaptchaSolver(capsolver_api_key=CAPSOLVER_API_KEY)
driver = webdriver.Chrome()
driver.get(URL_DO_SITE)
time.sleep(3)

# 2. Chamar o método para verificar e resolver o CAPTCHA
if solver.check_and_solve_captcha(driver):
    print("\n[Scraper Principal] CAPTCHA resolvido ou ausente. A continuar...")
    
    # A partir daqui, sua lógica de web scraping pode prosseguir
    # Exemplo: clicar em um botão ou preencher um formulário
    # driver.find_element(By.CSS_SELECTOR, 'input[value="Visualizar remuneração"]').click()
    
else:
    print("\n[Scraper Principal] Falha ao resolver o CAPTCHA. O script será encerrado.")
    driver.quit()
```

**Nota:** O método `check_and_solve_captcha` retorna `True` se o CAPTCHA foi resolvido com sucesso (ou se não foi encontrado), e `False` em caso de falha. Isso permite que você trate a resposta de forma programática.

## Licença

Este projeto é de código aberto e está disponível sob a licença MIT.
