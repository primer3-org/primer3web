#!/usr/bin/perl

$file = "rodent_ref.txt";

print("Content-type: text/plain\n\n");
open (FILE, "<$file") or print("Error: Cannot load file: $file");
while (<FILE>) {
   print ($_);
}
close(FILE);
