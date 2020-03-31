#!/bin/bash

# this script enumerate certain DNS domain info

DOMAIN=$1
BRUTE_FILE=$2
ERROR1="11" #BADARG
ERROR3="33" #LOGFILE EXISTS
LOGFILE="$DOMAIN.dnslog"

	if [[ ! $DOMAIN ]]
        then 
        echo "DOMAIN MISSING AS FIRST PARAMETER!!";
        echo "This script enumerate certain DNS domain info";
        exit
	fi

	function logfile { 
	if [ -e "$LOGFILE" ]; then
	echo "==================================="
	echo "LOGFILE FOR $DOMAIN EXISTS!!";
	echo "CHECK LOGFILE: $LOGFILE";
	echo "==================================="
	exit "$ERROR3"
	else 
	touch "$LOGFILE"
	fi
	}

	logfile; # function to check logfile existence

	echo '=======================';
	echo "Host: $DOMAIN" | tee -a $LOGFILE 
	echo '=======================';
	
	REV=`host $DOMAIN | grep "$DOMAIN has address" | perl -ne 'print "$1" if /has address\s(.+)$/'`
	echo "DOMAIN IS: $REV" | tee -a $LOGFILE

	echo "=======================";
	echo "DOMAIN: $DOMAIN REVERSE RECORD:" | tee -a $LOGFILE
	echo "=======================";
	dig -x "$REV" +noall +ans | tee -a $LOGFILE


	echo '=======================';
        echo "$DOMAIN SOA records:"  | tee -a $LOGFILE
        echo '=======================';
	dig -t soa "$DOMAIN" +short | tee -a $LOGFILE

	echo '=======================';
        echo "$DOMAIN NS records:"  | tee -a $LOGFILE
        echo '=======================';
	dig -t ns "$DOMAIN" +noall +answer +add | tee -a $LOGFILE

	echo '=======================';
        echo "$DOMAIN MX records:" | tee -a $LOGFILE
        echo '=======================';
	dig -t mx "$DOMAIN" +noall +answer +add	| tee -a $LOGFILE

	echo '=======================';
        echo "$DOMAIN TXT records:" | tee -a $LOGFILE
        echo '=======================';
	TXT=`dig -t txt "$DOMAIN" +noall +ans +add` | tee -a $LOGFILE

	if [ -z "$TXT" ]; then
	echo "No TXT RECORD FOUND!" 
	else
	echo "$TXT" 
	fi
	
	echo '=======================';
        echo "$DOMAIN HINFO records:"  | tee -a $LOGFILE
        echo '=======================';
	HINFO=`dig -t hinfo "$DOMAIN" +noall +ans +add` | tee -a $LOGFILE
        if [ -z "$HINFO" ]; then
	echo "No HINFO RECORD FOUND!" 
	else
	echo "$TXT" 
	fi

        # DNSSEC
        echo "$DOMAIN DNSSEC records:"  | tee -a $LOGFILE
	echo '=======================';
	echo "Checking DNSSEC:" | tee -a $LOGFILE
	echo '=======================';
        dig "$DOMAIN" +dnssec +short | tee -a $LOGFILE	
  

	NS=`dig -t ns "$DOMAIN" +noall +ans +add | grep NS | cut -f6`
	NSA=( $NS ); # array defined with NS SERVERS PTR RECORDS
	
	echo "Trying AXFR from domain."

			#read -p "Try AXFR?" que
                        #if [[ $que =~ "y" ]];then
		          for i in ${NSA[*]}
			  do
                          echo -en "\nChecking Server: $i for AXFR\n" | tee -a $LOGFILE
		          echo 	   "========================================="
			  dig "@$i" "$DOMAIN" axfr +short | tee -a $LOGFILE
 		          done
			# fi

			# this miss IXFR, CHAOS DOMAIN

		#	dig "@$i" "$DOMAIN" ixfr | tee -a $LOGFILE
		#	dig "@$i" version.bind chaos txt | tee -a $LOGFILE

		read -p "Do you want to try brute-force?" ans
		if [[ "$ans" == "y" ]];then
		 read -p "Enter dictionary file:" ifile
		else
		 exit 1
		fi
		
		if [ -f "$ifile" ]
		then
                  echo
                  echo  "###"
                  echo "Brute-force results for domain:$DOMAIN" | tee -a $LOGFILE
                  echo  "###"
		  while IFS= read -r line
		   do
		   host="$line.$DOMAIN"
		   echo "Checking host:$host"
		   check=$(dig $host +short)
		   if [[ "$check" != "" ]];then
		    echo "Exists:$host:$check" | tee -a $LOGFILE
		   fi
		  done < "$ifile"
		else
		 echo "No such file:$ifile !!"
		 echo "EXITING!"
		fi

exit 0
