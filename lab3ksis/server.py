import time, sys, socket
from threading import Thread


class Server(Thread):
    BUFFER_SIZE = 512
    users = []

    def __init__(self):
        Thread.__init__(self)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port_ser = int(input("Введите порт для сервера: "))
        try:
            self.udpSocket.bind((self.IP, self.port_ser))
            print(f"Сервер запущен. IP сервера: {self.IP}:{self.port_ser}")
        except socket.error as e:
            print(f"Порт недоступен!: {e}")
            sys.exit(1)

    def run(self):
        print(f"{self.getCurrentTime()}: Сервер запущен. IP сервера: {self.IP}:{self.port_ser}")
        while True:
            data, address = self.udpSocket.recvfrom(Server.BUFFER_SIZE)
            if address[0] not in self.users:
                if data.decode() == 'init':
                    self.users.append(address[0])
                    self.sendRequest(f"Количество пользователей в сети: {len(self.users)}", (address[0], address[1]))
                    print('Новый пользователь: ' + address[0])
                    self.SendMessages(self.users, 'К сети присоединился новый пользователь', address[0])
                continue

            if data.decode() == 'exit':
                self.users.remove(address[0])
                self.SendMessages(self.users, 'Из сети вышел пользователь ' + address[0], address[0])
                print('Пользователь вышел:' + address[0])
                continue

            data = address[0] + ': ' + data.decode()
            self.SendMessages(self.users, data, address[0])
            print(self.getCurrentTime() + ' ' + data)

    def getCurrentTime(self):
        return time.strftime("%H:%M:%S", time.localtime())

    def SendMessages(self, clients, data, myip):
        for ip in clients:
            if ip != myip:
                self.sendRequest(data, (ip, self.port_ser))

    def sendRequest(self, data, client):
        try:
            self.udpSocket.sendto(data.encode(), client)
        except socket.error:
            print("Ошибка при отправке запроса!")
            exit(1)


if __name__ == "__main__":
    server = Server()
    server.start()