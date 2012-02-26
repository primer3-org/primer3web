primer3-web release 3.0.0

GPL 2.0 license (please see gpl-2.0.txt)

Copyright (c) 1996,1997,1998,1999,2000,2001,2004,2006,2007,
              2008,2009,2010,2011,2012
Whitehead Institute for Biomedical Research, Steve Rozen
(http://steverozen.net), and Helen Skaletsky
All rights reserved.

This file contains instructions for installing the
primer3 web interface (release 3.0.0).  This interface
is provided strictly 'as-is'.

To install the web interface you will need:

a. primer3_core, which is written in C and which, at this  
point, you must compile yourself. You can find links
to the C code for primer3_core from 
http://sourceforge.net/projects/primer3.

b. primer3-web-htdocs-3.0.0.tar.gz (available 
from http://sourceforge.net/projects/primer3)

c. primer3-web-cgi-bin-3.0.0.tar.gz (available
from http://sourceforge.net/projects/primer3)

d. The perl module CGI.pm (available from CPAN,
http://cpan.org, if it is not already available
in your perl installation).

1. gunzip and untar primer3-web-htdocs-3.0.0.tar.gz
in your .../htdocs directory or equivalent.
** This will put the constituent files in
the current working directory.

2. gunzip and untar primer3-web-cgi-bin-3.0.0.tar.gz
in your .../cgi-bin directory or equivalent
** This will put the constituent files in
the current working directory.

3. Build primer3_core (anywhere) and copy or move it to
the directory containing the files from 
primer3-web-cgi-bin-3.0.0.tar.gz.  Also copy the
directory ./src/primer3_config to this directory.
(Background: running primer3_core requires the
directory primer3_config and its contents. This 
directory is provided in 
primer3-web-cgi-bin-3.0.0.tar.gz as 
./src/primer3_config/.  By default this primer3_config
needs to be in the current working directory when 
primer3_core is executed.)

4. Depending on the structure of your web site you may
have to adjust some of the URLs in the .htm
.html, or .cgi files.  You might have to fix the #!
headers in the .cgi files to point to your perl.
