import requests
import urllib
import webbrowser
from socket import AF_INET, socket, SOCK_STREAM
import json
import helper
import pyperclip


app_key = '48unrvyjbl7yjbw'
app_secret = 'ceek2nqin860zuw'
server_addr = "localhost"
server_port = 8090
redirect_uri = "http://" + server_addr + ":" + str(server_port)

class Dropbox:
    _access_token = ""
    _path = ""
    _files = []
    _root = None
    _msg_listbox = None

    def __init__(self, root):
        self._root = root

    def local_server(self):
        # por el puerto 8090 esta escuchando el servidor que generamos
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((server_addr, server_port))
        server_socket.listen(1)
        print("\tLocal server listening on port " + str(server_port))

        # recibe la redireccion 302 del navegador
        client_connection, client_address = server_socket.accept()
        peticion = client_connection.recv(1024)
        print("\tRequest from the browser received at local server:")
        print (peticion)

        # buscar en solicitud el "auth_code"
        primera_linea = peticion.decode('UTF8').split('\n')[0]
        aux_auth_code = primera_linea.split(' ')[1]
        auth_code = aux_auth_code[7:].split('&')[0]
        print ("\tauth_code: " + auth_code)

        # devolver una respuesta al usuario
        http_response = "HTTP/1.1 200 OK\r\n\r\n" \
                        "<html>" \
                        "<head><title>Proba</title></head>" \
                        "<body>The authentication flow has completed. Close this window.</body>" \
                        "</html>"
        client_connection.sendall(http_response.encode(encoding="utf-8"))
        client_connection.close()
        server_socket.close()

        return auth_code

    def do_oauth(self):
        #############################################
        # RELLENAR CON CODIGO DE LAS PETICIONES HTTP
        # Y PROCESAMIENTO DE LAS RESPUESTAS HTTP
        # PARA LA OBTENCION DEL ACCESS TOKEN
        #############################################

        # Paso 1: Obtener el código de autorización

        # Construir la URL de autorización
        authorize_url = "https://www.dropbox.com/oauth2/authorize"
        authorize_params = {
            "response_type": "code",
            "client_id": app_key,
            "redirect_uri": redirect_uri
        }
        authorize_url += "?" + urllib.parse.urlencode(authorize_params)

        # Abrir la URL en el navegador para que el usuario pueda autorizar la aplicación
        webbrowser.open(authorize_url)

        # Paso 2: Esperar a que el servidor local reciba el código de autorización

        # Iniciar el servidor local para recibir el código de autorización
        auth_code = self.local_server()

        # Paso 3: Intercambiar el código de autorización por un token de acceso

        token_url = "https://api.dropboxapi.com/oauth2/token"
        token_params = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": app_key,
            "client_secret": app_secret,
            "redirect_uri": redirect_uri
        }

        # Realizar la solicitud POST para obtener el token de acceso
        headers = {
            'User-Agent': 'Python Client',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(token_url, headers=headers, data=token_params)

        # Procesar la respuesta JSON
        response_data = json.loads(response.content)
        self._access_token = response_data["access_token"]

        # Cerrar la ventana principal de la aplicación
        self._root.destroy()

    def list_folder(self, msg_listbox):
        print("/list_folder")
        uri = 'https://api.dropboxapi.com/2/files/list_folder'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-list_folder
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        uri = 'https://api.dropboxapi.com/2/files/list_folder'

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Content-Type': 'application/json'
        }

        data = {
            'path': self._path,
            'recursive': False,
            'include_media_info': False,
            'include_deleted': False,
            'include_has_explicit_shared_members': False,
            'include_mounted_folders': True,
            'include_non_downloadable_files': True
        }

        response = requests.post(uri, headers=headers, json=data)

        if response.status_code == 200:
            content_json = response.json()
            self._files = helper.update_listbox2(msg_listbox, self._path, content_json)
        else:
            print("Error occurred while listing folder:", response.text)


    def transfer_file(self, file_path, file_data):
        print("/upload")
        print("filepath = " + str(file_path))
        print("filedata = " + str(file_data))
        uri = 'https://content.dropboxapi.com/2/files/upload'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-upload
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        uri = 'https://content.dropboxapi.com/2/files/upload'

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': json.dumps({'path': file_path, 'mode': 'add', 'autorename': True, 'mute': False})
        }

        response = requests.post(uri, headers=headers, data=file_data)

        if response.status_code == 200:
            print("File uploaded successfully.")
        else:
            print("Error occurred while uploading file:", response.text)

    def delete_file(self, file_path):
        print("/delete_file")
        uri = 'https://api.dropboxapi.com/2/files/delete_v2'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-delete
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        uri = 'https://api.dropboxapi.com/2/files/delete_v2'

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Content-Type': 'application/json'
        }

        data = {
            'path': file_path
        }

        response = requests.post(uri, headers=headers, json=data)

        if response.status_code == 200:
            print("File deleted successfully.")
        else:
            print("Error occurred while deleting file:", response.text)


    def create_folder(self, path):
        print("/create_folder")

        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        uri = 'https://api.dropboxapi.com/2/files/create_folder_v2'

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Content-Type': 'application/json'
        }

        data = {
            'path': path,
            'autorename': False
        }

        response = requests.post(uri, headers=headers, json=data)

        if response.status_code == 200:
            print("Folder created successfully.")
        else:
            print("Error occurred while creating folder:", response.text)

    def download_file(self, file_path):
        print("/download_file")
        uri = 'https://content.dropboxapi.com/2/files/download'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-download
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        uri = 'https://content.dropboxapi.com/2/files/download'

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Dropbox-API-Arg': json.dumps({'path': file_path})
        }

        response = requests.post(uri, headers=headers)

        if response.status_code == 200:
            # Guardar el archivo descargado
            file_data = response.content
            file_name = file_path.split('/')[-1]
            with open(file_name, 'wb') as file:
                file.write(file_data)
            print("File downloaded successfully.")
        else:
            print("Error occurred while downloading file:", response.text)

    def create_shared_link(self, file_path):
        print("/create_shared_link")
        uri = 'https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings'
        #############################################
        # RELLENAR CON CODIGO DE LA PETICION HTTP
        # Y PROCESAMIENTO DE LA RESPUESTA HTTP
        #############################################

        uri = 'https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings'

        headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Content-Type': 'application/json'
        }

        data = {
            'path': file_path,
            'settings': {
                'requested_visibility': 'public'
            }
        }

        response = requests.post(uri, headers=headers, json=data)

        if response.status_code == 200:
            content_json = response.json()
            shared_link = content_json['url']
            print("Shared link created:", shared_link)
            # Guardar el enlace compartido en el portapapeles
            pyperclip.copy(shared_link)
            print("El enlace se ha copiado al portapapeles.")
        else:
            print("Error occurred while creating shared link:", response.text)
