#!/usr/bin/perl

$file = "rodrep_and_simple.txt";

print("Content-type: text/plain\n\n");
open (FILE, "<$file") or print("Error: Cannot load file: $file");
while (<FILE>) {
   print ($_);
}
close(FILE);
rodrep_and_simple.txt
