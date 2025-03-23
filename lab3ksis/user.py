
import socket, sys
from threading import Thread

ip_server = ""
port_ser = ""
port_us = ""
def is_valid_ip (ip: str)-> bool:
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0<= int(part) <= 255 for part in parts)
    except ValueError:
        print("Некорректный ввод")
        return  False

def is_valid_port (port: str)-> bool:
    try:
        int_port = int(port)
        if 1024 <= int_port <= 65535:
            return True
        else:
            return False
    except:
        print("Некорректный ввод")
        return False

class User(Thread):
    BUFFER_SIZE = 512

    def __init__(self):
        super().__init__()
        try:
            self.IP_udp = ip_server
            self.port_server = port_ser
            self.port_user = port_us
            self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udpSocket.bind(('', self.port_user))
        except socket.error as e:
            print("Ошибка создания сокета: {}".format(e))
            exit(1)
        self.daemon = True

    def run(self):
        client.sendRequest('init', (self.IP_udp, self.port_server))
        while True:
            data, address = self.udpSocket.recvfrom(self.BUFFER_SIZE)
            print(data.decode())

    def sendRequest(self, data, client):
        try:
            self.udpSocket.sendto(data.encode(), client)
        except socket.error as e:
            print("Ошибка при отправке запроса: ".format(e))
            exit(1)


if __name__ == "__main__":
    while True:
        print("Введите IP сервера:")
        ip_server = input()
        if (is_valid_ip(ip_server)):
            break
    while True:
        print("Введите порт сервера:")
        port_ser = input()
        if is_valid_port(port_ser):
            port_ser = int(port_ser)
            break
    while True:
        print("Введите ваш порт:")
        port_us = input()
        if (is_valid_port(port_us)):
            port_us = int(port_us)
            break

    client = User()
    client.start()

    userInput = ''
    while userInput != 'exit':
        userInput = input()
        client.sendRequest(str(userInput), (ip_server, port_ser))
