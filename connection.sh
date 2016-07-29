#!/bin/bash

date=$(date +"%d-%m-%Y-%H:%M")
logfile="connection.log".$date

function show_interfaces(){
ip link show | grep -v link | cut -d':' -f2 | sed 's/ //g'
}

show_interfaces 

read -p "Enter interface:" INT

ifconfig $INT >> $logfile
ip route show >> $logfile
cat /etc/resolv.conf >> $logfile

dhcp=$(ps aux | grep dhclient | grep -c $INT)

if [[ $? -eq 0 ]];then
 cat /var/lib/dhcp/dhclient.leases >> $logfile
fi

check_wifi=$(iwconfig $INT)

if [[ $? -eq 0 ]];
 then
 echo "Wireless settings: " >> $logfile
fi`	
iwconfig $INT >> $logfile




