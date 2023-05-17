# -*- coding: UTF-8 -*-
from tkinter import messagebox
import requests
import urllib
from bs4 import BeautifulSoup
import time
import helper
import getpass

class eGela:
    _login = 0
    _cookie = ""
    _curso = ""
    _refs = []
    _root = None
    _uriegela = ""

    def __init__(self, root):
        self._root = root

    def check_credentials(self, username, password, event=None):
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        username = username.get()
        password = password.get()

        print("##### 1. PETICION #####")
        metodo = 'GET'
        uri = "https://egela.ehu.eus/login/index.php"

        cabeceras = {'Host': 'egela.ehu.eus'}
        respuesta = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)

        print(metodo + " " + uri)
        print(str(respuesta.status_code) + " " + respuesta.reason)

        eGela._cookie = respuesta.headers['Set-Cookie'].split(";")[0]  # obtenemos la cookie de sesión
        print("Cookie de sesión: " + eGela._cookie)

        # obtenemos el nombre y codificamos la contraseña
        nombre = input("Introduzca su nombre y apellidos en mayúsculas: ")
        password = urllib.parse.urlencode({'c': password})[2:]  # codificamos la contraseña

        # se busca el logintoken en el html
        html = respuesta.content
        documento = BeautifulSoup(html, "html.parser")
        etiqueta_input = documento.find('input', {'name': 'logintoken'})
        logintoken = etiqueta_input.get('value')  # guardamos el valor del logintoken

        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 2. PETICION #####")
        
        metodo = 'POST'
        cabeceras = {'Host': 'egela.ehu.eus',
                 'Content-Type': 'application/x-www-form-urlencoded',
                 'Cookie': f'{self._cookie}'}
        cuerpo = f'logintoken={logintoken}&username={username}&password={password}'
        respuesta = requests.request(metodo, uri, headers=cabeceras, data=cuerpo, allow_redirects=False)

        print(metodo + " " + uri)
        print(cuerpo)
        print(str(respuesta.status_code) + " " + respuesta.reason)

        html = respuesta.content
        # extraemos la cookie
        try:
            self._cookie = respuesta.headers['Set-Cookie'].split(";")[0]
            print("se ha iniciado sesión correctamente")
        except:
            self._login = 0
            print("el inicio de sesión no es correcto")
        print("Cookie de sesión: " + self._cookie)  # imprimimos la nueva cookie
        # obtenemos la uri a la que nos redirige
        uri = respuesta.headers['Location']

        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 3. PETICION #####")

        metodo = 'GET'
        cabeceras = {'Host': 'egela.ehu.eus',
                    'Cookie': f'{self._cookie}'}
        respuesta = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)
        print(metodo + " " + uri)
        print(str(respuesta.status_code) + " " + respuesta.reason)
        print(respuesta.headers)
        uri = respuesta.headers['Location']

        progress = 75
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()
		
        print("\n##### 4. PETICION #####")
        #############################################
        metodo = 'GET'
        cabeceras = {'Host': 'egela.ehu.eus',
                    'Cookie': f'{self._cookie}'}
        respuesta = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)
        print(metodo + " " + uri)
        print(str(respuesta.status_code) + " " + respuesta.reason)
        #############################################

        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()
		

        if str(nombre) in str(respuesta.content):
            # ahora debemos parsear la respuesta para hallar la uri de la asignatura que queremos
            documento = BeautifulSoup(respuesta.content, "html.parser")

            # buscamos la etiqueta <a> que nos interesa, la cual contiene el texto "Sistemas Web"
            asignatura = documento.find('a', string="Sistemas Web")
            self._curso = asignatura.get('href')

            print("login = " + str(self._login))
            
            self._root.destroy()
        else:
            tkMessageBox.showinfo("Alert Message", "Login incorrect!")

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 4. PETICION (Página principal de la asignatura en eGela) #####")
        
        metodo = 'GET'
        cabeceras = {'Host': 'egela.ehu.eus',
                     'Cookie': f'{self._cookie}'}
        respuesta = requests.request(metodo, self._curso, headers=cabeceras, allow_redirects=False)
        print(metodo + " " + self._curso)
        print(str(respuesta.status_code) + " " + respuesta.reason)

        documento = BeautifulSoup(respuesta.content, "html.parser")

        a_tags = documento.find_all('a') # buscamos todas las etiquetas <a>

        progress_step = float(100.0 / float(len(a_tags)))  # debería ser el número de pdfs de eGela


        print("\n##### Analisis del HTML... #####")
        #############################################
        for a_tag in a_tags:  # por cada a_tag encontrada en la página de eGela
            # filtramos para obtener únicamente las que son pdf
            img_tag = a_tag.find('img', src='https://egela.ehu.eus/theme/image.php/ehu/core/1678718742/f/pdf')
            if img_tag:
                pdf_link = a_tag.get('href')  # obtenemos la dirección del pdf

                identificarNombre = pdf_link.rfind("/")
                pdf_name = pdf_link[identificarNombre+1:]
                self._refs.append({"pdf_name": pdf_name, "pdf_link": pdf_link})  # anidamos el nombre y el link de cada pdf a refs

        #############################################

        # INICIALIZA Y ACTUALIZAR BARRA DE PROGRESO
        # POR CADA PDF ANIADIDO EN self._refs
        progress_step = float(100.0 / float(len(a_tags)))

        progress += progress_step
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)
        
        popup.destroy()
        return self._refs

    def get_pdf(self, selection):

        print("\t##### descargando  PDF... #####")
        #############################################
        metodo = 'GET'
        uri = self._refs[selection]
        cabeceras = {'Host': 'egela.ehu.eus',
                        'Cookie': f'{self._cookie}'}
        respuesta = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)

        print(metodo + " " + uri)
        print(str(respuesta.status_code) + " " + respuesta.reason)

         # recuperamos la "Location" de las cabeceras de cada respuesta.
        redireccion = respuesta.headers['Location']
        descarga = requests.request(metodo, redireccion, headers=cabeceras, allow_redirects=False)
        print(metodo + " " + redireccion)
        print(str(descarga.status_code) + " " + descarga.reason)

        pdf_name = self._refs[selection]["pdf_name"]
        pdf_content = descarga.content
        #############################################

        return pdf_name, pdf_content
