# -*- coding: UTF-8 -*-
import tkMessageBox
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

    def __init__(self, root):
        self._root = root

    def check_credentials(self, username, password, event=None):
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("##### 1. PETICION #####")
        metodo = 'GET'
        uri = "https://egela.ehu.eus/login/index.php"

        cabeceras = {'Host': 'egela.ehu.eus'}
        respuesta = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)

        print(metodo + " " + uri)
        print(str(respuesta.status_code) + " " + respuesta.reason)

        eGela._cookie = respuesta.headers['Set-Cookie'].split(";")[0]  # obtenemos la cookie de sesión
        print("Cookie de sesión: " + eGela._cookie)

        # obtenemos la contraseña de forma segura y sin codificar. Obtenemos también el usuario
        usuario = input("¿Cuál es tu nombre de usuario?")
        contrasena = getpass.getpass("introduce la contraseña SIN CODIFICAR: ")
        contrasena = urllib.parse.urlencode({'c': contrasena})[2:]  # codificamos la contraseña

        # se busca el logintoken en el html
        html = respuesta.content
        documento = BeautifulSoup(html, "html.parser")
        etiqueta_input = documento.find('input', {'name': 'logintoken'})
        eGela._login = etiqueta_input.get('value')  # guardamos el valor del logintoken

        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 2. PETICION #####")
        
        metodo = 'POST'
        cabeceras = {'Host': 'egela.ehu.eus',
                 'Content-Type': 'application/x-www-form-urlencoded',
                 'Cookie': f'{eGela._cookie}'}
        cuerpo = f'logintoken={eGela._login}&username={usuario}&password={contrasena}'
        respuesta = requests.request(metodo, uri, headers=cabeceras, data=cuerpo, allow_redirects=False)

        print(metodo + " " + uri)
        print(cuerpo)
        print(str(respuesta.status_code) + " " + respuesta.reason)

        html = respuesta.content
        # extraemos la cookie
        try:
            eGela._cookie = respuesta.headers['Set-Cookie'].split(";")[0]
        except:
            print("EL USUARIO O LA CONTRASEÑA SON INCORRECTOS... fin del programa")
            exit(0)
        print("Cookie de sesión: " + eGela._cookie)  # imprimimos la nueva cookie
        # obtenemos la uri a la que nos redirige
        uri = respuesta.headers['Location']

        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 3. PETICION #####")

        metodo = 'GET'
        cabeceras = {'Host': 'egela.ehu.eus',
                    'Cookie': f'{eGela._cookie}'}
        respuesta = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)
        print(metodo + " " + uri)
        print(str(respuesta.status_code) + " " + respuesta.reason)

        uri = respuesta.headers['Location']

        progress = 75
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()
		
        print("\n##### 4. PETICION #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()
		

        if COMPROBACION_DE_LOG_IN:
            #############################################
            # ACTUALIZAR VARIABLES
            #############################################
            self._root.destroy()
        else:
            tkMessageBox.showinfo("Alert Message", "Login incorrect!")

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 4. PETICION (Página principal de la asignatura en eGela) #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        progress_step = float(100.0 / len(NUMERO DE PDF_EN_EGELA))


        print("\n##### Analisis del HTML... #####")
        #############################################
        # ANALISIS DE LA PAGINA DEL AULA EN EGELA
        # PARA BUSCAR PDFs
        #############################################

        # INICIALIZA Y ACTUALIZAR BARRA DE PROGRESO
        # POR CADA PDF ANIADIDO EN self._refs
        progress_step = float(100.0 / NUMERO_DE_PDFs_EN_EGELA)


        progress += progress_step
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)
        
        popup.destroy()
        return self._refs

    def get_pdf(self, selection):

        print("\t##### descargando  PDF... #####")
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        return pdf_name, pdf_content
