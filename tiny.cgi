#! /usr/bin/env perl

use strict;
use warnings;

# settings

use constant DBDIR => '/srv/zpaste';

use CGI;
use File::Spec::Functions;
use Fcntl;

use SDBM_File;
#use GDBM_File;

# CGI setup

my $q = CGI->new;

# attach to the rewrite mapping db

my $rewritedb = catfile(DBDIR, 'rewrite.db');
my %rewrites;

tie %rewrites, 'SDBM_File', $rewritedb, O_RDWR|O_CREAT, 0644;
#tie %rewrites, 'GDBM_File', $rewritedb, &GDBM_READER, 0644;

unless (tied %rewrites)
{
    print "unable to attach: $rewritedb: $!";
    exit;
}

# extract tiny url name

my $name = $ENV{'PATH_INFO'};
$name =~ s,/,,;

#print "name: $name\n";

# look for the redirect link

my $link = $rewrites{$name};

unless ($link) {
	print "no link found for $name\n";
	exit;
}

print $q->redirect($link);
