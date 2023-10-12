from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
from PySimpleGUI import theme

import PySimpleGUI as sg
import os
import threading
import json

from config import *


def save_settings(login, password, selected_profiles):
    with open('data.json', 'r+') as file:
        json_file = json.load(file)
        json_file['login'] = login
        json_file['password'] = password
        json_file['selected_profiles'] = selected_profiles
        file.seek(0)
        json.dump(json_file, file, indent=4)
        file.truncate()
        
def get_settings():
    with open('data.json', 'r') as file:
        json_file = json.load(file)
        login = json_file.get('login', '')
        password = json_file.get('password', '')
        selected_profiles = json_file.get('selected_profiles', '')
        
    return login, password, selected_profiles

def initiate_webdriver():
    dir_path = os.getcwd()
    profile = os.path.join(dir_path, 'profile', 'user')
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-data-dir={profile}')
    browser = webdriver.Chrome(options=options)

    return browser

def execute(login, password, selected_profiles):
    browser = initiate_webdriver()
    browser.get(url)
    sleep(5)

    try:
        browser.find_element(By.XPATH, '//input[@aria-label="Telefone, nome de usuário ou email"]').send_keys(login)
        browser.find_element(By.XPATH, '//input[@aria-label="Senha"]').send_keys(password)
        browser.find_element(By.XPATH, '//button[@type="submit"]').click()
        sleep(5)
    except Exception as e:
        print(f'Erro ao fazer login: {str(e)}')

    selected_profiles = selected_profiles.split(',')

    for i in range(len(selected_profiles)):
        browser.get(f'{url}{selected_profiles[i].strip()}/')
        sleep(3)
        posts = browser.find_elements(By.XPATH, '//div[@class="_aagu"]')
        for post in posts:
            post.click()
        
            sleep(3)

            comments = browser.find_elements(By.XPATH, '//div[@class="_ae5q _akdn _ae5r _ae5s"]')
            comments_text = comments[0].text
            comment_list = comments_text.split('\n')

            user_dict = {}
            for i in range(len(comment_list)):
                if comment_list[i] == fst_element and i < len(comment_list) - 1:
                    if snd_element not in comment_list[i + 1]:
                        user_dict[comment_list[i + 1]] = comment_list[i + 2]
                    else:
                        try:
                            user_dict[comment_list[i + 2]] = comment_list[i + 3]
                        except:
                            print('Nenhum termo encontrado.')

            profile_users = [key for key, value in user_dict.items() if 'valor' in value.lower() or 'disponível' in value.lower() or 'qual' in value.lower()]
            if profile_users:
                profiles.append(profile_users)

            close_button = browser.find_element(By.XPATH, '//div[@class="x160vmok x10l6tqk x1eu8d0j x1vjfegm"]')
            close_button.click()

        try:
            for user in profiles:
                browser.get(url + user[0])
                sleep(3)
                follow_button = browser.find_element(By.XPATH, '//div[@class="_aacl _aaco _aacw _aad6 _aade"]')
                if follow_button.text == 'Seguir':
                    print(f'Seguindo {user[0]}')
                    follow_button.click()
        except:
            print('Nenhuma palavra chave encontrada nos comentários.')

        profiles.clear()

        sleep(5)

def execute_main_thread(login, password, selected_profiles):
    print('Iniciando...')
    execute(login, password, selected_profiles)


def interface():
    theme('Reddit')

    login, password, profiles = get_settings()

    layout = [
        [sg.Text('Login:'), sg.Push(), sg.InputText(login, key='login')],
        [sg.Text('Senha:'), sg.Push(), sg.InputText(password, key='senha', password_char='*')],
        [sg.Text('')],
        [sg.Text('Perfis para análise:')],
        [sg.InputText(profiles, key='perfis', size=(55))],
        [sg.Text('Atenção: Digite os perfis separados por vírgula.')],
        [sg.Text('')],
        [sg.Push(), sg.Button('Iniciar'), sg.Button('Fechar'), sg.Push()],
    ]

    window = sg.Window(f'Coletor de Perfis v{version}', layout, icon='robot.ico')

    while True:
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED or event == 'Fechar':
            break

        if event == 'Iniciar':
            login = values['login']
            password = values['senha']
            selected_profiles = values['perfis']

            save_settings(login, password, selected_profiles)

            threading.Thread(target=execute_main_thread, args=(login, password, selected_profiles)).start()

    window.close()


if __name__=='__main__':
    profiles = []
    interface()