# audio_captcha_solver.py
# Versão 3.4 - Adiciona uma pausa estratégica após uma falha para evitar o rate limiting.

import time
import speech_recognition as sr
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import os
import random
import base64
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- Constantes Internas do Módulo ---
_AUDIO_FILE_MP3 = "audio_challenge.mp3"
_AUDIO_FILE_WAV = "audio_challenge.wav"
# AUMENTADO O NÚMERO DE TENTATIVAS PARA TORNAR O SCRIPT MAIS PERSISTENTE
_MAX_RECARREGAMENTOS = 5

def _type_like_human(element: WebElement, text: str):
    """Digita um texto num elemento, caractere por caractere, com pausas aleatórias."""
    print("   [Solver] A digitar a solução de forma cadenciada...")
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.08, 0.25)) # Pausa entre cada letra

def _transcrever_audio_local(caminho_arquivo_wav, language):
    """Função interna para transcrever o áudio no idioma especificado."""
    r = sr.Recognizer()
    try:
        time.sleep(random.uniform(2.0, 3.5))
        with sr.AudioFile(caminho_arquivo_wav) as source:
            print(f"   [Solver] A ouvir o ficheiro de áudio (Idioma: {language})...")
            audio_data = r.record(source)
            print("   [Solver] A transcrever...")
            texto = r.recognize_google(audio_data, language=language)
            texto_limpo = "".join(filter(str.isalnum, texto)).lower()
            print(f"   [Solver] Texto transcrito: '{texto}' -> Limpo: '{texto_limpo}'")
            return texto_limpo
    except (sr.UnknownValueError, sr.RequestError) as e:
        print(f"   [Solver] Erro na transcrição: {e}")
        return None
    except Exception as e:
        print(f"   [Solver] Ocorreu um erro inesperado na transcrição: {e}")
        return None

def solve_recaptcha_v2_audio(driver: WebDriver, language: str = 'en-US') -> bool:
    """
    Tenta resolver um reCAPTCHA v2 na página atual usando o desafio de áudio.
    """
    wait = WebDriverWait(driver, 10)
    short_wait = WebDriverWait(driver, 3)
    
    try:
        print("[Solver] A localizar e a entrar no iframe do reCAPTCHA...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@title="reCAPTCHA"]')))
        
        wait.until(EC.element_to_be_clickable((By.ID, 'recaptcha-anchor'))).click()
        time.sleep(random.uniform(0.6, 1.2))
        print("[Solver] Caixa 'Não sou um robô' clicada.")

        driver.switch_to.default_content()
        iframe_desafio_locator = (By.XPATH, '//iframe[@title="o desafio reCAPTCHA expira em dois minutos"]')
        iframe_desafio = wait.until(EC.presence_of_element_located(iframe_desafio_locator))
        driver.switch_to.frame(iframe_desafio)
        print("[Solver] Entrou no iframe do desafio.")

        wait.until(EC.element_to_be_clickable((By.ID, 'recaptcha-audio-button'))).click()
        time.sleep(random.uniform(1.0, 1.8))
        print("[Solver] Desafio de áudio solicitado.")

        for i in range(_MAX_RECARREGAMENTOS + 1):
            print(f"  [Solver] Sub-tentativa de áudio {i + 1}/{_MAX_RECARREGAMENTOS + 1}...")
            
            audio_src = wait.until(EC.presence_of_element_located((By.ID, 'audio-source'))).get_attribute('src')
            
            print("   [Solver] A baixar o áudio através do navegador...")
            audio_base64 = driver.execute_script(f"""
                return await fetch("{audio_src}")
                    .then(response => response.arrayBuffer())
                    .then(buffer => {{
                        let base64String = '';
                        const bytes = new Uint8Array(buffer);
                        for (let i = 0; i < bytes.byteLength; i++) {{
                            base64String += String.fromCharCode(bytes[i]);
                        }}
                        return btoa(base64String);
                    }});
            """)
            audio_data = base64.b64decode(audio_base64)
            with open(_AUDIO_FILE_MP3, 'wb') as f: f.write(audio_data)
            
            solucao_texto = None
            try:
                # --- BLOCO DE VERIFICAÇÃO DE ÁUDIO ---
                AudioSegment.from_mp3(_AUDIO_FILE_MP3).export(_AUDIO_FILE_WAV, format="wav")
                solucao_texto = _transcrever_audio_local(_AUDIO_FILE_WAV, language)
            except CouldntDecodeError:
                print("   [Solver] ERRO: Ficheiro de áudio inválido recebido. O site pode estar a bloquear o download.")

            if solucao_texto:
                campo_resposta = driver.find_element(By.ID, 'audio-response')
                _type_like_human(campo_resposta, solucao_texto)
                
                time.sleep(random.uniform(0.5, 1.0))
                driver.find_element(By.ID, 'recaptcha-verify-button').click()
                
                driver.switch_to.default_content()
                try:
                    short_wait.until(EC.invisibility_of_element_located(iframe_desafio_locator))
                    print("  [Solver] Sucesso! O desafio foi aceite e fechado.")
                    return True
                except TimeoutException:
                    print("  [Solver] Resposta incorreta.")
                    iframe_desafio = driver.find_element(*iframe_desafio_locator)
                    driver.switch_to.frame(iframe_desafio)
                    if i < _MAX_RECARREGAMENTOS:
                        # --- PAUSA ESTRATÉGICA ADICIONADA ---
                        print("     [Solver] A aguardar antes de pedir um novo áudio...")
                        time.sleep(random.uniform(2.5, 4.0))
                        driver.find_element(By.ID, 'recaptcha-reload-button').click()
                        time.sleep(random.uniform(1.0, 1.5))
                    else:
                        print("  [Solver] Limite de recarregamentos atingido.")
                        break
            else:
                print("  [Solver] Transcrição ou conversão de áudio falhou.")
                if i < _MAX_RECARREGAMENTOS:
                    # --- PAUSA ESTRATÉGICA ADICIONADA ---
                    print("     [Solver] A aguardar antes de pedir um novo áudio...")
                    time.sleep(random.uniform(2.5, 4.0))
                    driver.find_element(By.ID, 'recaptcha-reload-button').click()
                    time.sleep(random.uniform(1.0, 1.5))
                else:
                    print("  [Solver] Limite de recarregamentos atingido.")
                    break
        
        driver.switch_to.default_content()
        return False

    except Exception as e:
        print(f"  [Solver] ERRO INESPERADO durante a resolução: {e}")
        driver.switch_to.default_content()
        return False
    finally:
        if os.path.exists(_AUDIO_FILE_MP3): os.remove(_AUDIO_FILE_MP3)
        if os.path.exists(_AUDIO_FILE_WAV): os.remove(_AUDIO_FILE_WAV)
        print("[Solver] Ficheiros de áudio temporários removidos.")
