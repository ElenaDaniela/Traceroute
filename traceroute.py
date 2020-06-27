import socket
import traceback
import requests
import random
import struct
import json
import sys

# socket de UDP
udp_send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

# socket RAW de citire a răspunsurilor ICMP
icmp_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
# setam timout in cazul in care socketul ICMP la apelul recvfrom nu primeste nimic in buffer



def ip_info(ip):
	fake_HTTP_header = {
					'referer': 'https://ipinfo.io/',
					'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
					'X-Forwarded-For': socket.inet_ntoa(struct.pack('!I', random.randint(1, 0xffffffff)))
				   }
	res = requests.get(str(ip), headers=fake_HTTP_header)
	return (json.loads(res.text))


def traceroute(ip, port):
	# setam TTL in headerul de IP pentru socketul de UDP
	max_hops = 30
	for TTL in range(1, max_hops+1):
		icmp_recv_socket.settimeout(0.2)
		udp_send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, TTL)

		# trimite un mesaj UDP catre un tuplu (IP, port)
		udp_send_sock.sendto(b'salut', (ip, port))
		try:
			data, curr_adr = icmp_recv_socket.recvfrom(63535)
			curr_adr = curr_adr[0]
		except socket.error:
			curr_addr = None

		yield curr_adr
		if curr_adr == ip:
			break

nume_dest = sys.argv[1]
adr_dest = socket.gethostbyname(nume_dest)
print (adr_dest)
ip_list = []


for i, traced_ip in enumerate(traceroute(adr_dest, 33434)):
		if(traced_ip != None and traced_ip not in ip_list):
			ip_list.append(traced_ip)
			url = "https://ipinfo.io/widget/"+traced_ip
			raspuns = ip_info(url)
			if 'bogon' not in raspuns:
					print(str(i+1) + ')' + '\t' + traced_ip + '\t- ' + raspuns['city'] + ', ' + raspuns['region'] + ', ' + raspuns['country'])
			else:
					print(str(i+1) + ')' + '\t' + traced_ip + '\t- ' + 'Private IP')
		else:
			print(str(i+1) + ')'  +'\t' + "*" + ' ' + "*" + ' ' + "*")