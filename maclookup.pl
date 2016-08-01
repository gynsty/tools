#!/usr/bin/perl
use strict;
use warnings;
use Term::ANSIColor;

my $arg = shift;

my $sample = "oui.sample";
my $FILE = "oui.txt";

if (!$arg){
  &help;
}

elsif ($arg =~ /-update/){
  &update;
} 
elsif ($arg =~ /-lookup/){
  &lookup(shift);
}
elsif ($arg =~ /-help/){
  &help;
}

else {
  print "Invalid arguments detected. Exiting!\n";
  help();
}



sub help{
 print color 'green';
 print "Valid parameters are: \
 --update - to update oui.txt \
 --lookup - to lookup for MAC Address OUI\n";
 print "example: perl changeoui.pl --lookup 04:1B:BA:00:12:5D\n";
 print color 'reset';
 exit(255);
}

sub update{

  #if (-f "oui.txt"){
  #  print "oui.txt file exists - moving!\n";
  #  system("mv oui.txt oui.txt.old");
  #}

  print "Trying to update oui.txt online...\n";
  print "Enter ctrl+c to exit!\n";
  sleep(5);
  `wget http://standards.ieee.org/regauth/oui/oui.txt`;

  # applying good format for oui.txt

  print "Applying format patch for oui.txt\n";
  sleep 3;

    if (! -f $FILE){
    die "No such file or directory: oui.txt!!\nExiting\n";
  }  

  open FILE,"<",$FILE or die "$!\n";
  open SAMPLE,">",$sample;

  while(my $line = <FILE>){

   if ($line =~ /\(hex\)/ ){
     $line =~ s/\s+\(hex\)\s+/\t/g;
     print SAMPLE $line;

    # get substring:
    my $index = index($line,' ');
    my $sub = substr($line,0,$index);
    $sub =~ s/-/:/g;
    my $rest = substr($line,$index+1);
    print SAMPLE $sub,$rest;
   }
   elsif ($line =~ /base 16/){
     $line =~ s/\s+\(base 16\)\s+/\t\t/g;
     print SAMPLE $line;
   }
}

close(FILE);
close(SAMPLE);

exit(256);
}

sub lookup{
  my $mac = shift; 

  if ($mac =~ "" or !$mac){
    print "INVALID MAC..Quiting\n";    
    exit(257);
  }

  my @tmp = split /:/,$mac;
  my $myoui = join ':',@tmp[0..2]; 

  open SAMPLE,"<",$sample or die "Unable to open sample file!\n";

  my $hitcount = 0;
  while (my $s = <SAMPLE>){
   chomp($s);
   if ($s =~ /$myoui/i){
     my @lines = split /\t/,$s;

     print color 'green';
     print "$myoui :$lines[1]\n";
     print color 'reset';
     $hitcount = 1; 
   }
  }

  if (!$hitcount){
    print color 'green';
    print "Nothing found .. sorry... :-(\n";
    print color 'reset';
  }
}

exit(0);

# apply path - change to right format on lines 96-97
