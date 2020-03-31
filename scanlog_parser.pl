#!/usr/bin/perl
use strict;
use warnings;

# skript parsuje nmap logy ".gnmap" a masscan logy
# cat nmap_results.gnmap masscan.log | perl pars.pl > vystup (format pre repp externy test)

my %hosts;
my %host_dns;
my @doubles;
my $host_counter = 0;

if (@ARGV){
  if ($ARGV[0] =~ /[-]{1,2}h[elp]?/ ){
   print("USAGE: cat *.gnamp | perl nmappars.pl. This script reads nmap \"gnmap\" logs from STDIN and creates .rep hosts.\n");
   exit(1);
  }
  if ( $ARGV[0] =~ /[-]g?nmap/ ){
   print STDERR "Waiting for nmap input\n";
   &nmap_parse;
  }
  if ( $ARGV[0] =~ /[-]mass?/ ){
   &maspars;
   print STDERR "Waiting for masscan input\n";
  }
} else {
  print("Invalid parameters detected!\n");
  &usage;
}

sub usage{
 print("This script reads nmap .gnmap or .masscan logs from STDIN and creates hosts with ports in REP format.\n");
 print("USAGE: cat *.nmap or *.masscan | perl nmappars.pl -gnmap|-mass \n");
}

sub nmap_parse{

while (my $line = <STDIN>){

 chomp($line);
 next if $line =~ '^#.*'; # ignore comments
   
 if ($line =~ /Ports:/){

    if ( $line =~ /^Host:\s+(.+)\s+\((.*)\)\s+Ports:\s*(.+)(\/\/\/?|s*Ignored)/ ){

     my $ip = $1;
     my $dns = $2;
     my $ports = $3;
     my @ports = ();

     # dns stuff
     if (length($dns) == 0 ){
      $host_counter++;
      $dns = 'HOST' . $host_counter;
     }
     else {
      $dns = substr($dns,0,index($dns,'.'));
     } 

     $host_dns{$ip} = $dns;
 
     # fix port string 
     $ports =~ s/\s+$//;     
     $ports =~ s/,\s/,/g;


     if (!$hosts{$ip}){
       $hosts{$ip} = $ports;
     } else {
       my $hports = $hosts{$ip};
       $hosts{$ip} = $hports . "," . $ports;
     }

   }
 }
             
}

# now print it:

my %host_ports;

while (my($host,$ports) = each %hosts){

   print "\\host:";
   if ($host_dns{$host}){
    print uc " $host_dns{$host}\;";
   }
   print " $host\n";
   # get uniq ports
   my @ports = split /,/,$ports;

   # sort ports
   @ports = grep /open/,@ports;
  
   my @sorted = sort {
     my ($aa) = $a =~ /^([0-9]+?)\//x;
     my ($bb) = $b =~ /^([0-9]+?)\//x;
     $aa <=> $bb;
  } @ports;

   foreach my $p (@sorted){
    #if ($p =~ /open/){

      my ($pnum,$psrv,$pdesc) = split /[\/]{2}/,$p;

      # pdesc - can be empty
      if (!$pdesc){
       $pdesc = "-";
      }

      # checking for duplicates
      if ($host_ports{$pnum}){
       
        if ( length($host_ports{$pnum}) < length("$psrv:$pdesc") ) {
         $host_ports{$pnum} = "$psrv:$pdesc";
        } else {
          next;
        }
      } else {
       $host_ports{$pnum} = "$psrv:$pdesc"; # use ':' as separator for port service:description
      }
   
    #} 
     #else {
     #next;
    #}
  }

  # format port:
  print "\n\\portlist_ver+\n";

  # print no duplicate ports and in numeric order
  # hash is protecting against duplicates
  #
  my %test;
  foreach my $k (sort 
     {
     my ($aa) = $a =~ /^([0-9]+)\//;
     my ($bb) = $b =~ /^([0-9]+)\//;
     $aa <=> $bb
     } (keys %host_ports)
     ) # solved numeric order
     {
       my $s = "$k:$host_ports{$k}";
       my ($port,$srv,$desc) = split /:/,$s;

       $port =~ s/\/open//; 
       print "$port open $srv";
       $desc =~ s/\/$//;

       if ($desc =~ /^\/$/){
        print "";
       } else {
         print " $desc";
       }
    print "\n";
  }
 
   print "+\n\n";
  
  }

}

sub maspars{

my %hosts;

# read from stdin get host as hash key, ports as values
while(my $line = <STDIN>){
 chomp($line);
 next if $line =~ /^#/;

 if ($line =~ /Host:\s(.+)\s+\(\)\s+Ports:\s(.+)\/\// ){
   my $host = $1;
   my $ports = $2;
   if ($hosts{$host}){
     my $con = $hosts{$host};
     $con .= ",$ports";
     $hosts{$host} = $con;
   } else {
     $hosts{$host} = $ports;
   }
 }
}

 # print hash in correct format
 print "\n";
 my $counter = 0;
 while (my ($host,$ports) = each(%hosts)){
  $counter++;
  print "\n\\host: HOST",$counter,"; $host\n\n";
  print "\\portlist_ver+\n";
  my @ports = sort (split /,/,$ports);

  @ports = reverse sort @ports; # this is imperfect, but works fine

  foreach my $p (@ports){
   $p =~ s/\/open//;
   my $s1 = substr($p,0,index($p,"\/\/"));
   my $s2 = substr($p,index($p,"\/\/")+2);
   print "$s1\topen\t$s2\n";
  
  }
  print "+\n\n";
 }

}

exit(0);

