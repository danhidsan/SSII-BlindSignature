import socket
import sys
from Crypto.PublicKey import RSA
from Utils import delete_noise, complete_message

# Creando un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_address = ('localhost', 10000)

# Incluimos la dirección y el puerto al socket
sock.bind(server_address)

# Iniciamos el listener
sock.listen(1)

print('Server run in', server_address[0], 'port', server_address[1])

key = RSA.importKey(open('public.pem').read())
public_key = key.publickey()

while True:

    print("Esperando conexion de cliente")
    connection, client_address = sock.accept()

    while True:
        try:
            server_response = connection.recv(4096)
            data_without_noise = delete_noise(server_response.decode('utf-8'))
            print('Comprobando la firma...')
            message = data_without_noise.split('|')[0]
            signature = data_without_noise.split('|')[1]
            verification = public_key.verify(int(message), (int(signature), None))
            if verification:
                connection.send(complete_message('OK').encode('utf-8'))
            else:
                connection.send(complete_message('KO').encode('utf-8'))

        except Exception as e:
            print(e)
            connection.close()
