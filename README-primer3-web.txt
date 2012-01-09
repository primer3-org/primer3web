primer3-web release 0.4.0

[This is a *new* BSD license -- no advertising reach-through.]

Copyright (c) 1996,1997,1998,1999,2000,2001,2004,2006,2007
Whitehead Institute for Biomedical Research, Steve Rozen
(http://jura.wi.mit.edu/rozen), and Helen Skaletsky
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

   * Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following disclaimer
in the documentation and/or other materials provided with the
distribution.
   * Neither the names of the copyright holders nor contributors may
be used to endorse or promote products derived from this software
without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


This file contains instructions for installing the
primer3 web interface (release 0.4.0).  This interface
is provided strictly 'as-is'.  You may be able to
get some help by posting to 

primer3-mail .AT. lists.sourceforge net.


To install the web interface you will need:

a. primer3_core, which is written in C and which, at this
point, you must compile yourself. You can find links
to the C code for primer3_core from 
http://sourceforge.net/projects/primer3.

b. primer3-web-htdocs-0.4.0.tar.gz (available 
from http://sourceforge.net/projects/primer3)

c. primer3-web-cgi-bin-0.4.0.tar.gz (available
from http://sourceforge.net/projects/primer3)

d. The perl module CGI.pm (available from CPAN,
http://cpan.org, if it is not already available
in your perl installation).

1. gunzip and untar primer3-web-htdocs-0.4.0.tar.gz
in your .../htdocs directory or equivalent.

2. gunzip and untar primer3-web-cgi-bin-0.4.0.tar.gz
in your .../cgi-bin directory or equivalent

3. Build primer3_core (anywhere) and copy or
move it to .../cgi-bin/primer3-web-cgi-bin-0.4.0/
(created by untar'ing primer3-web-cgi-bin-0.4.0.tar.gz)

Depending on the structure of your web site you may
have to adjust some of the URLs in the .htm
.html, or .cgi files.  You might have to fix the #!
headers in the .cgi files to point to your perl.

** We are looking for help with moving primer3 and
primer3-web to open source development.  If you
would like to contribute your expertise in
open software development, C, perl, web-design,
end user documentation, release engineering, testing,
usability, please post to

primer3-mail .AT. lists.sourceforge.com.

or contact Steve Rozen directly:

steverozen .AT. gmail.com
