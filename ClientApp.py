import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.config import Config
import socket
from Crypto.PublicKey import RSA
from Utils import complete_message, generate_coprime_random, delete_noise

kivy.require('1.9.0')

Config.set('graphics', 'width', 400)
Config.set('graphics', 'height', 400)


# Creando un socket TCP/IP del la entidad firmante

try:
    signer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    signer_server_address = ('localhost', 3000)

    print('connected to', signer_server_address[0], 'port', signer_server_address[1])

    signer_socket.connect(signer_server_address)
except Exception as e:
    print(e)


# Creando un socket TCP/IP del centro de voto

try:

    voting_center_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    voting_server_address = ('localhost', 10000)

    print('connected to', voting_server_address[0], 'port', voting_server_address[1])

    voting_center_socket.connect(voting_server_address)
except Exception as e:
    print(e)

# Importando clave pública

key = RSA.importKey(open('public.pem').read())
public_key = key.publickey()


class MainApp(App):
    title = "Puntuality Voting App"

    def __init__(self, **kwargs):

        self.message = ""
        self.signature = ""

        # Checkbox
        self.btn1 = CheckBox(size=(25, 25), group="gr1")
        self.btn2 = CheckBox(size=(25, 25), group="gr1")
        self.btn3 = CheckBox(size=(25, 25), group="gr1")
        self.btn4 = CheckBox(size=(25, 25), group="gr1")

        # Sign Button
        self.sign_button = Button(text="Firmar Voto")

        # Sign Label
        self.sign_label = Label(text="Firma")

        # Vote Button
        self.vote_button = Button(text="Votar")

        # Vote Label
        self.vote_label = Label(text="Voto")

        super().__init__(**kwargs)

    def build(self):
        layout = BoxLayout(padding=10, orientation='vertical')

        # Checkbox
        label_btn1 = Label(text="AMC")
        layout.add_widget(self.btn1)
        layout.add_widget(label_btn1)

        label_btn2 = Label(text="JML")
        layout.add_widget(self.btn2)
        layout.add_widget(label_btn2)

        label_btn3 = Label(text="RMF")
        layout.add_widget(self.btn3)
        layout.add_widget(label_btn3)

        label_btn4 = Label(text="LCD")
        layout.add_widget(self.btn4)
        layout.add_widget(label_btn4)

        # Sign Button
        self.sign_button.bind(on_press=self.sign_button_clicked)
        layout.add_widget(self.sign_button)

        # Sign Label
        layout.add_widget(self.sign_label)

        # Vote Button
        self.vote_button.bind(on_press=self.vote_button_clicked)
        layout.add_widget(self.vote_button)

        # Vote Label
        layout.add_widget(self.vote_label)

        return layout

    def sign_button_clicked(self, btn):

        try:
            if self.btn1.active:
                self.message = '20'
            elif self.btn2.active:
                self.message = '30'
            elif self.btn3.active:
                self.message = '40'
            elif self.btn4.active:
                self.message = '50'
            else:
                self.sign_label.text = "Seleciona un Empleado"
                print("Selecciona un empleado")
                return

            random_number = generate_coprime_random(int(self.message))
            blinded_message = complete_message(str(public_key.blind(int(self.message), random_number)))
            signer_socket.send(blinded_message.encode('utf-8'))
            server_response = signer_socket.recv(4096)
            response_noise = self.delete_noise(server_response.decode('utf-8'))
            number = str(public_key.unblind(int(response_noise), random_number))
            print(str(number))
            self.sign_label.text = str(number)
            self.signature = str(number)

        except Exception as exception:
            print(exception)
            self.sign_label.text = str(exception)

    def vote_button_clicked(self, btn):
        try:
            message_with_vote = self.message + '|' + self.signature
            data_to_send = complete_message(message_with_vote)
            voting_center_socket.send(data_to_send.encode('utf-8'))
            voting_server_response = voting_center_socket.recv(4096)
            message_noise = self.delete_noise(voting_server_response.decode('utf-8'))
            print(message_noise)
            if message_noise == 'OK':
                self.vote_label.text = "Voto correcto"
            else:
                self.vote_label.text = "Voto incorrecto"
        except Exception as ex:
            print(ex)
            self.vote_label.text = str(ex)

    @staticmethod
    def delete_noise(string):
        sub_str = string.replace('=', '')
        return sub_str


if __name__ == '__main__':
    MainApp().run()