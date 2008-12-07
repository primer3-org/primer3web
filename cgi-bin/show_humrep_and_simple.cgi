#!/usr/bin/perl

$file = "humrep_and_simple.txt";

print("Content-type: text/plain\n\n");
open (FILE, "<$file") or print("Error: Cannot load file: $file");
while (<FILE>) {
   print ($_);
}
close(FILE);
