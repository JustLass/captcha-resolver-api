# capsolver_solver.py
# Biblioteca reutilizável para detetar e resolver CAPTCHAs com Capsolver.

import time
import requests
import base64
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class CaptchaSolver:
    def __init__(self, capsolver_api_key: str):
        """
        Inicializa o resolvedor com a sua chave da API do Capsolver.
        """
        if not capsolver_api_key or capsolver_api_key == "SUA_CHAVE_API_CAPSOLVER":
            raise ValueError("A chave da API do Capsolver é necessária. Por favor, forneça uma chave válida.")
        self.api_key = capsolver_api_key
        print("[Solver] Resolvedor de CAPTCHA inicializado.")

    def _resolver_com_api(self, task_payload):
        """Função interna para comunicar com a API do Capsolver."""
        try:
            task_payload["clientKey"] = self.api_key
            print("   [Solver] A criar tarefa no Capsolver...")
            response_criacao = requests.post("https://api.capsolver.com/createTask", json=task_payload, timeout=30)
            response_criacao.raise_for_status()
            result_criacao = response_criacao.json()

            if result_criacao.get("errorId") != 0:
                print(f"   [Solver] Erro ao criar tarefa: {result_criacao.get('errorDescription')}")
                return None
            
            task_id = result_criacao.get("taskId")
            print(f"   [Solver] Tarefa criada com sucesso. ID: {task_id}")
            
            result_payload = {"clientKey": self.api_key, "taskId": task_id}
            print("   [Solver] A aguardar a solução...")
            start_time = time.time()
            while time.time() - start_time < 180:
                time.sleep(5)
                response_resultado = requests.post("https://api.capsolver.com/getTaskResult", json=result_payload, timeout=30)
                response_resultado.raise_for_status()
                result = response_resultado.json()

                if result.get("status") == "ready":
                    print("   [Solver] Solução recebida!")
                    return result.get("solution")
                elif result.get("status") == "processing":
                    print("   [Solver] Solução ainda a ser processada...")
                else:
                    print(f"   [Solver] Erro ou estado inesperado: {result.get('errorDescription')}")
                    return None
            
            print("   [Solver] Tempo de espera excedido.")
            return None

        except requests.exceptions.RequestException as e:
            print(f"   [Solver] Erro de conexão com a API do Capsolver: {e}")
            return None

    def check_and_solve_captcha(self, driver: WebDriver) -> bool:
        """
        Verifica se um CAPTCHA conhecido está presente na página e tenta resolvê-lo.
        Retorna True se nenhum CAPTCHA for encontrado ou se for resolvido com sucesso.
        Retorna False se um CAPTCHA for encontrado, mas a resolução falhar.
        """
        wait = WebDriverWait(driver, 5) # Espera curta para detetar o CAPTCHA

        try:
            # Tenta encontrar o CAPTCHA de Imagem
            print("[Solver] A verificar se existe um CAPTCHA de imagem...")
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'captcha')))
            print("[Solver] Encontrado: CAPTCHA de imagem. A iniciar resolução...")
            
            captcha_image_element = wait.until(EC.presence_of_element_located((By.ID, 'imgCaptcha')))
            imagem_base64 = captcha_image_element.screenshot_as_base64
            
            task_payload = {"task": {"type": "ImageToTextTask", "body": imagem_base64}}
            solution = self._resolver_com_api(task_payload)
            
            if solution:
                captcha_texto = solution.get("text")
                print(f"[Solver] Solução: {captcha_texto}. A ser digitado no campo.")
                driver.find_element(By.ID, 'txtTexto_captcha').send_keys(captcha_texto)
                driver.find_element(By.ID, 'btnSubmit').click()
                return True
            return False

        except TimeoutException:
            # Se não encontrou o CAPTCHA de imagem, procura pelo reCAPTCHA
            print("[Solver] CAPTCHA de imagem não encontrado. A verificar se existe Google reCAPTCHA...")
            driver.switch_to.default_content()
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[starts-with(@name, "a-") and starts-with(@src, "https://www.google.com/recaptcha")]')))
                print("[Solver] Encontrado: Google reCAPTCHA. A iniciar resolução...")
                
                driver.switch_to.default_content()
                site_key_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'g-recaptcha')))
                site_key = site_key_element.get_attribute('data-sitekey')
                
                task_payload = {
                    "task": {
                        "type": "ReCaptchaV2TaskProxyLess",
                        "websiteURL": driver.current_url,
                        "websiteKey": site_key
                    }
                }
                solution = self._resolver_com_api(task_payload)

                if solution:
                    recaptcha_token = solution.get("gRecaptchaResponse")
                    submit_button = driver.find_element(By.CSS_SELECTOR, 'input[value="Visualizar remuneração"]')
                    driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{recaptcha_token}';")
                    time.sleep(1)
                    submit_button.click()
                    return True
                return False
            
            except TimeoutException:
                # Se não encontrou nenhum dos dois, assume que não há CAPTCHA
                print("[Solver] Nenhum CAPTCHA conhecido foi encontrado na página. A continuar...")
                driver.switch_to.default_content()
                return True
