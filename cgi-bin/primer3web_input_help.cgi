#!/usr/bin/perl

$file = "primer3web_input_help.htm";

print("Content-type: text/html\n\n");
open (FILE, "<$file") or print("Error: Cannot load file: $file");
while (<FILE>) {
   print ($_);
}
close(FILE);
