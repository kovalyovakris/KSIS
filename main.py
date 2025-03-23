import os
import sys
import ctypes
import socket
import struct
import time
import select
import ipaddress

def is_ip(address):
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False

def get_dns_name(ip_address):
    try:
        host = socket.gethostbyaddr(ip_address)[0]  # Получаем имя хоста
        return host
    except socket.herror:
        return "DNS-имя не найдено"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def checksum(source_string):
    sum = 0
    count_to = (len(source_string) // 2) * 2
    count = 0

    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum = sum + this_val
        sum = sum & 0xffffffff
        count = count + 2

    if count_to < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def create_icmp_packet(id, seq):
    header = struct.pack('bbHHh', 8, 0, 0, id, seq)
    data = b'bsuirbsuirbsuirbsuirbsuirbsuirpi'  # Произвольные данные
    my_checksum = checksum(header + data)
    header = struct.pack('bbHHh', 8, 0, socket.htons(my_checksum), id, seq)
    return header + data

def send_ping(dest_addr, ttl, timeout=2):  # Увеличенный тайм-аут
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        sock.settimeout(timeout)
    except socket.error as e:
        print(f"ошибка при создании сокета: {e}")
        return None, None

    pack_id = os.getpid() & 0xFFFF
    pack_seq = 1
    pack = create_icmp_packet(pack_id, pack_seq)
    try:
        sock.sendto(pack, (dest_addr, 0))
        time_sent = time.time()
    except socket.error as e:
        print(f"ошибка при отправке пакета: {e}")
        sock.close()
        return None, None

    while True:
        try:
            result = select.select([sock], [], [], timeout)
            if result[0] == []:
                print("тайм-аут при ожидании")
                sock.close()
                return None, None

            time_received = time.time()
            recv_packet, addr = sock.recvfrom(1024)
            icmp_header = recv_packet[20:28]
            type, code, checksum, p_id, seq = struct.unpack('bbHHh', icmp_header)
            if type == 0 and p_id == pack_id:
                sock.close()
                return addr[0], (time_received - time_sent) * 1000
            elif type == 11 and code == 0:
                sock.close()
                return addr[0], (time_received - time_sent) * 1000
        except socket.error as e:
            print(f"Ошибка при получении ответа: {e}")
            sock.close()
            return None, None

def tracert(dest_addr, max_hops=30, packets_per_hop=3):
    print(f"traceroute до {dest_addr} (макс {max_hops} шагов)")
    for ttl in range(1, max_hops + 1):
        responses = []
        for _ in range(packets_per_hop):
            addr, duration = send_ping(dest_addr, ttl)
            if addr:
                responses.append((addr, duration))
        if responses:
            avg_duration = sum(duration for _, duration in responses) / len(responses)
            print(f"{ttl}\t{responses[0][0]}\t{avg_duration:.2f} ms")
            if responses[0][0] == dest_addr:
                print("целевой узел достигнут")
                break
        else:
            print(f"{ttl}\t*\t*")

def tracert_dns(dest_addr, max_hops=30, packets_per_hop=3):  # Отправка нескольких пакетов
    print(f"traceroute до {dest_addr} (макс {max_hops} шагов)")
    for ttl in range(1, max_hops + 1):
        responses = []
        for _ in range(packets_per_hop):
            addr, duration = send_ping(dest_addr, ttl)
            if addr:
                responses.append((addr, duration))
        if responses:
            avg_duration = sum(duration for _, duration in responses) / len(responses)
            print(f"{ttl}\t{responses[0][0]}\t{get_dns_name(responses[0][0])}\t{avg_duration:.2f} ms")
            if responses[0][0] == dest_addr:
                print("целевой узел достигнут")
                break
        else:
            print(f"{ttl}\t*\t*")

if __name__ == "__main__":
    trace = input("Введите IP: ")
    if(is_ip(trace)):
        tracert(trace)
    else:
        ip_address = socket.gethostbyname(trace)
        print(f"IP-адрес {trace}: {ip_address}")
        tracert_dns(ip_address)

