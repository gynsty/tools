#!/usr/bin/perl
use strict;
use warnings;
use LWP::Simple;
use Parallel::ForkManager;

my $howmany =  shift; # how many child fork()
my $maxproc = shift;  # max process count for Fork manager
my $command = shift;

if (!($howmany||$maxproc||$command)) {
die "HELP: 1.childs to fork, 2.max process count 3.command\n";
}

my $pm = Parallel::ForkManager->new($maxproc);

for my $i (1..$howmany){ # for each item fork child
  my $child = $pm->start and next; # do the fork
  print "Child forked:, Command: ",$command,"\n";
  system($command);
  $pm->finish;
}

$pm->wait_all_children; # wait till all childs finish their job

exit(0);
