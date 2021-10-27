import requests
from pyngrok import ngrok
import paho.mqtt.client as paho
from sys import argv

import requests
# declaração de constantes

# endereço de ip da câmera
ESP32CAM_IP_ADRESS = '192.168.15.67:80'

# token de acesso ao serviço de tunelamento do ngrok
AUTH_TOKEN = '1vcvjKLwCs5ZNUAYMy4YIMuIFuG_3qqxjdD2EEC5npvwLS56H'

BROKER = 'broker.hivemq.com'
PORT = 1883 
DEVICE_ID = 'SV-SERVER'

CONFIG_SERVER = 'https://arcane-reef-05776.herokuapp.com/config'
STREAMING_SERVER_URL = 'https://arcane-reef-05776.herokuapp.com/stream'

def main():
    # cria um cliente MQTT para se comunicar diretamente com o simov
    client = paho.Client()

    # se conecta ao servidor BROKER
    client.connect(BROKER, PORT)

    # configura o ngrok 

    # seta o token de autenticação
    ngrok.set_auth_token = '1vcvjKLwCs5ZNUAYMy4YIMuIFuG_3qqxjdD2EEC5npvwLS56H'
    ngrok_tunnel = ngrok.connect(ESP32CAM_IP_ADRESS, "tcp")

    # obtem o processo de um tunelamento do ngrok
    ngrok_tunnel_process = ngrok.get_ngrok_process()

    # obtem a url publica do tunnel
    new_url = ngrok_tunnel.public_url

    # formata a url de maneira apropriada 
    url_formatted = new_url.replace("tcp://", 'http://')
    url_formatted += "/mjpeg/1"

    change_url_payload = {
        'url': url_formatted 
    }

    url_change_status = requests.post(CONFIG_SERVER, json=change_url_payload).status_code
    # altera a url de streaming
    while url_change_status != 200: 

        code = requests.post(CONFIG_SERVER, change_url_payload).status_code
        url_change_status = code
        print(code)
        print('tentando atualizar a url do servidor proxy')

    print('-- alteração da url no servidor proxy realizada com sucesso --')

    # notifica o simov da alteração da url
    client.publish("controlador/url", STREAMING_SERVER_URL)
    
    print('-' * 15)

    print('Inicializando processo de tunelamento')

    # inicia o tunnelamento do IP  da ESP32-CAM
    try: 
        print('processo de tunnelamento sendo realizado')

        print('-' * 15)
        print(f'url de streaming local (não acesse): http://{ESP32CAM_IP_ADRESS}/mjpeg/1')
        print(f'url pública de streaming local (não acesse): {url_formatted}')
        print(f'url de streaming do servidor proxy {STREAMING_SERVER_URL}')
        print('-' * 15)

        ngrok_tunnel_process.proc.wait()
    except: 
        print("desligando tunelamento")
        ngrok.kill() 


if __name__ == '__main__': 
    main()