import socket
from Crypto.PublicKey import RSA
from Utils import delete_noise, complete_message

# Creando un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Direccion y puerto del servidor
server_address = ('localhost', 3000)

# Incluimos la dirección y el puerto al socket
sock.bind(server_address)

# Iniciamos el listener
sock.listen(1)

print('Server run in', server_address[0], 'port', server_address[1])
while True:
    print("Esperando conexion de cliente")
    connection, client_address = sock.accept()

    while True:
        try:
            private_key_string = open('private.pem', "r").read()
            private_key = RSA.importKey(private_key_string)
            print('concexion desde', client_address)

            # Recibe los datos en trozos y reetransmite

            data = connection.recv(4096)
            delete_noise = delete_noise(data.decode('utf-8'))
            client_request = int(delete_noise)
            signed_message = str(private_key.sign(client_request, "")[0])
            complete_message_signed = complete_message(signed_message)
            connection.send(complete_message_signed.encode('utf-8'))

        except Exception as e:
            print(e)
            connection.close()
