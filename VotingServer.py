import socket
import sys
from Crypto.PublicKey import RSA
from Utils import complete_message, delete_noise, generate_coprime_random

# Creando un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_address = ('localhost', 3000)

print('connected to', server_address[0], 'port', server_address[1])

sock.connect(server_address)

key = RSA.importKey(open('public.pem').read())
public_key = key.publickey()

key_private = RSA.importKey(open('private.pem').read())

while True:
    try:
        while True:
            message = input()
            random_number = generate_coprime_random(int(message))
            blinded_message = complete_message(str(public_key.blind(int(message), random_number)))
            sock.send(blinded_message.encode('utf-8'))
            server_response = sock.recv(4096)
            delete_noise = delete_noise(server_response.decode('utf-8'))
            unblinded_number = str(public_key.unblind(int(delete_noise), random_number))
            print(str(unblinded_number))
            print('Comprobando la firma...')
            verification = key_private.verify(int(message), (int(unblinded_number), None))

            verification_message = 'Firma correcta'
            if verification is False:
                verification_message = 'Firma incorrecta'
            print(verification_message)
            break

    except Exception as e:
        print(e)
        sys.exit(2)

    finally:
        print('cerrando socket')
        sock.close()
        break
