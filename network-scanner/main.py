

import scapy.all as scapy

class ArpScan:
    def scan(self, ip):
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        ans_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

        client_list = []
        for element in ans_list:
            client_dict = {
                "ip": element[1].psrc,
                "mac": element[1].hwsrc
            }
            client_list.append(client_dict)
        
        return client_list
    
    def parser_arp_result(self, result):

        client_list = result

        print("-"*50)
        print("\tIP\t\t\t\t MAC Address")
        print("-"*50)

        for client in client_list:
            print(f"{client.get("ip")}\t\t{client.get("mac")}")

    def run(self, ip):
        arp_result = self.scan(ip=ip)
        self.parser_arp_result(result=arp_result)
        


arp_scanner = ArpScan()
arp_scanner.run(ip="192.168.31.1/24")
