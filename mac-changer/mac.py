#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
import sys

class MacChanger:
    MAC_PATTERN = re.compile(r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}")

    def __init__(self, interface=None, mac_address=None):
        self.interface = interface
        self.requested_mac = mac_address.lower() if mac_address else None

    def is_root(self):
        """Return True, if user is root, else False."""

        return os.getuid() == 0

    # Works for linux
    def does_interface_exist(self, interface):
        """Returns True, if interface exists, else False."""

        return os.path.isdir(f"/sys/class/net/{interface}")

    def is_valid_mac(self, mac):
        """Returns True, if mac address pattern is valid, else False."""

        if not mac:
            return False

        return bool(self.MAC_PATTERN.fullmatch(mac.lower()))

    def change_mac(self, interface, mac):
        """Simply changes mac address using 'ip' command."""

        try:
            print("[+] Changing MAC Address...")
            subprocess.run(["ip", "link", "set", "dev", interface, "down"])  # No check=True as the interface maybe already down
            subprocess.run(["ip", "link", "set", "dev", interface, "address", mac,], check=True,)
            subprocess.run(["ip", "link", "set", interface, "up"], check=True)
        except Exception as e:
            raise RuntimeError(f"[!] Error Occurred\n{e}")

    def is_mac_changed(self, interface, requested_mac):
        """Returns True if MAC address was successfully changed, else False."""

        try:
            result = subprocess.run(
                ["ip", "link", "show", interface],
                check=True,
                text=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get interface info: {e}")

        current_macs = self.MAC_PATTERN.findall(result.stdout)

        if not current_macs:
            raise RuntimeError("Could not detect MAC address from interface output")

        current_mac = current_macs[0].lower()

        return current_mac == requested_mac

    def run(self):
        if not self.is_root():
            print("[!] Root Access not Detected.")
            print("[!] Please use sudo to run the program.")
            sys.exit(1)

        if not self.does_interface_exist(interface=self.interface):
            print("[!] Invalid interface.")
            sys.exit(1)

        if not self.is_valid_mac(mac=self.requested_mac):
            raise ValueError("Invalid MAC address format")
        
        # Chnage the mac
        self.change_mac()

        if not self.is_mac_changed(interface=self.interface, requested_mac=self.requested_mac):
            print("[!] Failed to change the MAC Adress")
        else:
            print(f"[+] Successfully changed the mac address for {self.interface} to {self.mac}")

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", required=True, help="Specify the interface")
    parser.add_argument("-m", "--mac", required=True, help="Specify the mac address")
    args = parser.parse_args()

    iface = args.interface
    target_mac = args.mac

    mac_changer = MacChanger(interface=iface, mac_address=target_mac)
    mac_changer.run()
