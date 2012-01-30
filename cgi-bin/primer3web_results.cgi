#!/usr/bin/perl

# ----- Installer Modifiable Variables -------------------------------------
# You may wish to modify the following variables to suit
# your installation.

# Who the end user will complain to:
$MAINTAINER = 'the webmaster for this site';

# Add mispriming / mishybing libraries;  make coordinate changes
# in input.htm
%SEQ_LIBRARY=
  ('NONE' => '',
   'HUMAN' => 'humrep_and_simple.txt',
   'RODENT_AND_SIMPLE' => 'rodrep_and_simple.txt',
   'RODENT' => 'rodent_ref.txt',
   'DROSOPHILA' => 'drosophila_w_transposons.txt',
   # Put more repeat libraries here.
  );

# The URL for help regarding this screen (which will normally
# be in the same directory as the this script)
$ODOC_URL = "primer3web_help.cgi";

# The location of the primer3_core executable.
# It will be much easier if this is in the
# same directory as this file.
#$PRIMER_BIN =  "primer3_core.exe"; # for windows
$PRIMER_BIN =  "./primer3_core";     # for linux

$FILE_CACHE = "cache/"; # for windows
#$FILE_CACHE = "cache/"; # for linux

# If you make any substantial modifications give this code a new
# version designation.
$CGI_RELEASE = "(primer3_results.cgi release 3.0.0)";

# ----- End Installer Modifiable Variables ---------------------------------

$COPYRIGHT = $COPYRIGHT = q{ 
Copyright (c) 1996,1997,1998,1999,2000,2001,2004,2006,2007,2008,2009,2010,2011,2012
Whitehead Institute for Biomedical Research, Steve Rozen
(http://purl.com/STEVEROZEN/), Andreas Untergasser and Helen Skaletsky.
All rights reserved.

    This file is part of the primer3web suite.

    The primer3 suite and libraries are free software;
    you can redistribute them and/or modify them under the terms
    of the GNU General Public License as published by the Free
    Software Foundation; either version 2 of the License, or (at
    your option) any later version.

    This software is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this software (file gpl-2.0.txt in the source
    distribution); if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

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
};

use CGI;
use Carp;
use FileHandle;
use IPC::Open3;
use File::Basename;

main();

sub main 
{
  $query = new CGI;
  if ($query->param('Pick Primers')) {
    process_input($query);
  } elsif ($query->param('Download Settings')) {
    list_settings($query);
  } elsif ($query->param('Upload')) {
    get_settings($query);
  } else {
    confess "Did not see the 'Pick Primers' or 'Download Settings' query parameter";
  }
}

sub show_error($)
{
    my ($msg) = @_;
    print "$msg";
}

sub get_settings($)
{
  my ($query) = @_;
  print "Content-type: text/html\n\n";
  # Ensure that errors will go to the web browser.
  open(STDERR, ">&STDOUT");
  $| = 1;
  my @names = $query->param;
  my $file = $query->param('Upload');
  if (!$file) {
    show_error("No settings file specified!");
    return;
  }
  my %tags;
  # get file handle
  my $upload_filehandle = $query->upload("Upload");
  # read the tags
  while (<$upload_filehandle>) {
    chomp($_);
    $_ =~ s/^\s*//;
    $_ =~ s/\s*$//;
    if ($_ eq "=") {
      # ignore anything after an = line
      last;
    }
    if ($_ =~ /^Primer3 File/) { next; }
    if ($_ eq "") { next; }
    if ($_ =~ "^#") {next; }
    unless ($_ =~ /([A-Z_0-9]+)=([^\n]*)/) {
      show_error("Incorrect syntax on line \"$_\" of settings file");
      return;
    }
    my $tag = $1;
    my $value = $2;
    if (($tag eq "PRIMER_MISPRIMING_LIBRARY") || ($tag eq 'PRIMER_INTERNAL_MISHYB_LIBRARY')) {
      $value = basename($value);
      if ($value eq "humrep_and_simple.txt") {
	$value = "HUMAN";
      } elsif ($value eq "rodrep_and_simple.txt") {
	$value = "RODENT_AND_SIMPLE";
      } elsif ($value eq "rodent_ref.txt") {
	$value = "RODENT";
      } elsif ($value eq "drosophila_w_transposons.txt") {
	$value = "DROSOPHILA";
      } else {
	$value = "NONE";
      }
    } elsif ($tag eq "PRIMER_TASK") {
      if ($value eq "pick_pcr_primers") {
	$value = "generic";
	$tags{"PRIMER_PICK_LEFT_PRIMER"} = 1;
	$tags{"PRIMER_PICK_INTERNAL_OLIGO"} = 0;
	$tags{"PRIMER_PICK_RIGHT_PRIMER"} = 1;
      } elsif ($value eq "pick_pcr_primers_and_hyb_probe") {
	$value = "generic";
	$tags{"PRIMER_PICK_LEFT_PRIMER"} = 1;
	$tags{"PRIMER_PICK_INTERNAL_OLIGO"} = 1;
	$tags{"PRIMER_PICK_RIGHT_PRIMER"} = 1;
      } elsif ($value eq "pick_left_only") {
	$value = "generic";
	$tags{"PRIMER_PICK_LEFT_PRIMER"} = 1;
	$tags{"PRIMER_PICK_INTERNAL_OLIGO"} = 0;
	$tags{"PRIMER_PICK_RIGHT_PRIMER"} = 0;
      } elsif ($value eq "pick_right_only") {
	$value = "generic";
	$tags{"PRIMER_PICK_LEFT_PRIMER"} = 0;
	$tags{"PRIMER_PICK_INTERNAL_OLIGO"} = 0;
	$tags{"PRIMER_PICK_RIGHT_PRIMER"} = 1;
      } elsif ($value eq "pick_hyb_probe_only") {
	$value = "generic";
	$tags{"PRIMER_PICK_LEFT_PRIMER"} = 0;
	$tags{"PRIMER_PICK_INTERNAL_OLIGO"} = 1;
	$tags{"PRIMER_PICK_RIGHT_PRIMER"} = 0;
      } elsif ($value eq "pick_detection_primers") {
	$value = "generic";
      } elsif (($value ne "pick_detection_primers") &&
	       ($value ne "pick_cloning_primers") &&
	       ($value ne "pick_discriminative_primers") &&
	       ($value ne "pick_sequencing_primers") &&
	       ($value ne "pick_primer_list") &&
	       ($value ne "generic") &&
	       ($value ne "check_primers")) {
	  # use default
	  $value = "generic";
      }
    } elsif ($tag =~ /^SEQUENCE_/) {
      # ignore sequence related tags
      next;
    }
    $tags{$tag} = $value;
  }
  if (!defined($tags{'PRIMER_MISPRIMING_LIBRARY'})) {
    $tags{'PRIMER_MISPRIMING_LIBRARY'} = 'NONE';
  }
  if (!defined($tags{'PRIMER_INTERNAL_MISHYB_LIBRARY'})) {
    $tags{'PRIMER_INTERNAL_MISHYB_LIBRARY'} = 'NONE';
  }
  # read in primer3web_input.htm and update the values
  open IN, "primer3web_input.htm" or die "open primer3web_input.htm: $!\n";
  my $line = <IN>;
  while (1) {
    if (!$line) { last; }
    if ($line =~ /^\s*$/) { $line = <IN>; next; }
    if ($line =~ /primer3web_help.htm/) {
      $line =~ s/primer3web_help.htm/\.\.\/primer3web_help.htm/;
    }
    if ($line =~ /Upload the settings from a file/) {
      print "<p>Settings were loaded from $file</p>\n";
    }
    if ($line =~ /select name="PRIMER_MISPRIMING_LIBRARY"/) {
      # read in all option lines and select the right one
      while ($line !~ /\/select/) {
	# unselect to make it easier
	$line =~ s/\s*selected="selected"\s*//;
	my $value;
	if ($line =~ /\<option\>([A-Za-z0-9]+)\<\/option\>/) {
	  $value = $1;
	  if ($tags{'PRIMER_MISPRIMING_LIBRARY'} eq $value) {
	    # put the select
	    $line =~ s/option/option selected="selected"/;
	  }
	}
	print $line;
	$line = <IN>;
      }
      next;
    } elsif ($line =~ /select name="PRIMER_INTERNAL_MISHYB_LIBRARY"/) {
      # read in all option lines and select the right one
      while ($line !~ /\/select/) {
	# unselect to make it easier
	$line =~ s/\s*selected="selected"\s*//;
	my $value;
	if ($line =~ /\<option\>([A-Za-z0-9]+)\<\/option\>/) {
	  $value = $1;
	  if ($tags{'PRIMER_INTERNAL_MISHYB_LIBRARY'} eq $value) {
	    # put the select
	    $line =~ s/option/option selected="selected"/;
	  }
	}
	print $line;
	$line = <IN>;
      }
      next;
    } elsif ($line =~ /select name="PRIMER_TM_FORMULA"/) {
      if (!defined($tags{'PRIMER_TM_FORMULA'})) { print $line; $line = <IN>; next; }
      my $value = $tags{'PRIMER_TM_FORMULA'};
      # read in all option lines and select the right one
      while ($line !~ /\/select/) {
	# unselect to make it easier
	$line =~ s/selected="selected"//;
	if ($line =~ /value="$value"/) {
	  $line =~ s/value="$value"/value="$value" selected="selected"/;
	}
	print $line;
	$line = <IN>;
      }
      next;
    } elsif ($line =~ /select name="PRIMER_SALT_CORRECTIONS"/) {
      if (!defined($tags{'PRIMER_SALT_CORRECTIONS'})) { print $line; $line = <IN>; next; }
      my $value = $tags{'PRIMER_SALT_CORRECTIONS'};
      # read in all option lines and select the right one
      while ($line !~ /\/select/) {
	# unselect to make it easier
	$line =~ s/selected="selected"//;
	if ($line =~ /value="$value"/) {
	  $line =~ s/value="$value"/value="$value" selected="selected"/;
	}
	print $line;
	$line = <IN>;
      }
      next;
    } elsif ($line =~ /name="([A-Z_]+)"/) {
      my $name = $1;
      if ($name =~ /^MUST_XLATE_/) {
	# this is a checkbox, determine if it should be checked
	$name =~ s/^MUST_XLATE_//;
	if (defined($tags{$name})) {
	  $line =~ s/checked="checked"//;
	  if ($tags{$name} != 0) {
	    $line =~ s/type="checkbox"/checked="checked" type="checkbox"/;
	  }
	}
      } elsif ($line =~ /value="(.+)"/) {
	my $value = $1;
	if (defined($tags{$name})) {
	  $line =~ s/value=".+"/value="$tags{$name}"/;
	}
      }
    } elsif ($line =~ /action="cgi-bin\/primer3web_results\.cgi"/) {
      $line =~ s/action="cgi-bin\/primer3web_results\.cgi"/action="primer3web_results\.cgi"/;
    } elsif (($line =~ /generic/) && (defined($tags{'PRIMER_TASK'})) && 
	     ($tags{'PRIMER_TASK'} ne "generic")) {
      $line =~ s/selected="selected"//;
    } elsif (($line =~ /(pick_[a-z_]*)/) && (defined($tags{'PRIMER_TASK'})) &&
	     ($tags{'PRIMER_TASK'} eq $1)) {
      $line =~ s/option/option selected="selected"/;
    } 
    print $line;
    $line = <IN>;
  }
  close IN;
}

sub list_settings($)
{
  my ($query) = @_;
  my @names = $query->param;

  my $first_base_index = $query->param('PRIMER_FIRST_BASE_INDEX');
  if ($first_base_index !~ \S) {
    $first_base_index = 1;
  }

  # Fix the values of the checkboxes:
  my $therodynamicAlignment  = 0;
  my $pick_left  = 0;
  my $pick_internal = 0;
  my $pick_right = 0;
  my $liberal_base = 0;
  my $print_input = 0;
  my $ambiguity_Consensus = 0;
  my $lowercase_masking = 0;
  my $pick_anyway = 0;
  my $explain_flag = 0;

  if (defined $query->param('MUST_XLATE_PRIMER_THERMODYNAMIC_ALIGNMENT')) {
    $therodynamicAlignment = 1;
  }
  if (defined $query->param('MUST_XLATE_PRIMER_PICK_LEFT_PRIMER')) {
    $pick_left = 1;
  }
  if (defined $query->param('MUST_XLATE_PRIMER_PICK_INTERNAL_OLIGO')) {
    $pick_internal = 1;
  }
  if (defined $query->param('MUST_XLATE_PRIMER_PICK_RIGHT_PRIMER')) {
    $pick_right = 1;
  }
  if (defined $query->param('MUST_XLATE_PRIMER_LIBERAL_BASE')) {
    $liberal_base = 1;
  }
  if (defined $query->param('MUST_XLATE_PRINT_INPUT')) {
    $print_input = 1;
  }
  if (defined $query->param('MUST_XLATE_PRIMER_LIB_AMBIGUITY_CODES_CONSENSUS')) {
    $ambiguity_Consensus = 1;
  }
  if (defined $query->param('MUST_XLATE_PRIMER_LOWERCASE_MASKING')) {
    $lowercase_masking = 1;
  }
  if (defined $query->param('MUST_XLATE_PRIMER_PICK_ANYWAY')) {
    $pick_anyway = 1;
  }
  if (defined $query->param('MUST_XLATE_PRIMER_EXPLAIN_FLAG')) {
    $explain_flag = 1;
  }
  $pick_left     = 1 if $query->param('SEQUENCE_PRIMER');
  $pick_right    = 1 if $query->param('SEQUENCE_PRIMER_REVCOMP');
  $pick_internal = 1 if $query->param('SEQUENCE_INTERNAL_OLIGO');

  my @input;

  push @input, "Primer3 File - http://primer3.sourceforge.net\n";
  push @input, "P3_FILE_TYPE=settings\n";
  push @input, "\n";

  push @input, "PRIMER_FIRST_BASE_INDEX=$first_base_index\n";
  push @input, "PRIMER_THERMODYNAMIC_ALIGNMENT=$therodynamicAlignment\n";
  push @input, "PRIMER_PICK_LEFT_PRIMER=$pick_left\n";
  push @input, "PRIMER_PICK_INTERNAL_OLIGO=$pick_internal\n";
  push @input, "PRIMER_PICK_RIGHT_PRIMER=$pick_right\n";
  push @input, "PRIMER_LIBERAL_BASE=$liberal_base\n";
  push @input, "PRIMER_LIB_AMBIGUITY_CODES_CONSENSUS=$ambiguity_Consensus\n";
  push @input, "PRIMER_LOWERCASE_MASKING=$lowercase_masking\n";
  push @input, "PRIMER_PICK_ANYWAY=$pick_anyway\n";
  push @input, "PRIMER_EXPLAIN_FLAG=$explain_flag\n";

  for (@names) {
    next if /^Pick Primers$/;
    next if /^Download Settings$/;
    next if /^PRIMER_FIRST_BASE_INDEX$/;
    next if /^MUST_XLATE/;

    # we skip completely all sequence related tags
    next if /^SEQUENCE_ID$/;
    next if /^SEQUENCE_TARGET$/;
    next if /^SEQUENCE_EXCLUDED_REGION$/;
    next if /^SEQUENCE_INCLUDED_REGION$/;
    next if /^SEQUENCE_OVERLAP_JUNCTION_LIST$/;
    next if /^SEQUENCE_TEMPLATE$/;
    next if /^SEQUENCE_PRIMER$/;
    next if /^SEQUENCE_INTERNAL_OLIGO$/;
    next if /^SEQUENCE_PRIMER_REVCOMP$/;
    next if /^SEQUENCE_QUALITY$/;
    next if /^SEQUENCE_PRIMER_PAIR_OK_REGION_LIST$/;
    next if /^SEQUENCE_START_CODON_POSITION$/;
    next if /^SEQUENCE_INTERNAL_EXCLUDED_REGION$/;
    next if /^SEQUENCE_FORCE_LEFT_START$/;
    next if /^SEQUENCE_FORCE_LEFT_END$/;
    next if /^SEQUENCE_FORCE_RIGHT_START$/;
    next if /^SEQUENCE_FORCE_RIGHT_END$/;
	
    $v = $query->param($_);
    if (/^PRIMER_(MISPRIMING|INTERNAL_MISHYB)_LIBRARY$/) {
      $v = $SEQ_LIBRARY{$v};
    }
    next if $v =~ /^\s*$/;
    $line = "$_=$v\n";
    push @input, $line;
  }
  push @input, "=\n";

  # return the file
  print "Content-Type:application/x-download; name=primer3_settings.txt\n";
  print "Content-Disposition: attachment; filename=primer3_settings.txt\n\n";
  print @input;
}

sub process_input 
{
    my ($query) = @_;
    my $wrapup = "<pre>$CGI_RELEASE</pre>" . $query->end_html;
    my $tmpurl = $query->url;
    my ($v, $v1);

    local $DO_NOT_PICK = 0;

    print "Content-type: text/html\n\n";
    # Ensure that errors will go to the web browser.
    # open(LOG,">&STDERR"); Intended logging capability does not work correctly.
    # close(STDERR);
    open(STDERR, ">&STDOUT");
    $| = 1;
    print '';
    
    print $query->start_html("Primer3 Output $CGI_RELEASE");
    print qq{<h2>Primer3 Output</h2>\n};
    print "<hr>\n";

    check_server_side_configuration($query);

    my @names = $query->param;
    my $line;
    my $fasta_id;

#    my $settings;
#    # check if a settings file was given, in that case upload it to /tmp and use it when calling primer3
#    my $file = $query->param('Upload');
#    if (defined($file) && ($file ne "")) {
#	# make the filename safe
#	my $safe_filename_characters = "a-zA-Z0-9_.-";
#	my ($name, $path, $extension) = fileparse ($file, '\..*'); 
#	$settings = $name . $extension;
#	$settings =~ tr/ /_/; 
#	$settings =~ s/[^$safe_filename_characters]//g;
#	 # get file handle
#	my $upload_filehandle = $query->upload("Upload");
#	# read the tags and write them to our settings file, also keep track what was given in the settings
#	open UPLOADFILE, ">/tmp/$settings" or die "$!"; 
#	while (my $line = <$upload_filehandle>) {
#	    #skip PRIMER_THERMODYNAMIC_PARAMETERS_PATH as this is different in our case anyway
#	    if ($line =~ /^PRIMER_THERMODYNAMIC_PARAMETERS_PATH/) { next; }
#	    if ($line =~ /^PRIMER_MISPRIMING_LIBRARY=(\S*)/) {
#		my $v = $1;
#		# keep only filename (remove the path)
#		$v = basename($v);
#		print UPLOADFILE "PRIMER_MISPRIMING_LIBRARY=$v\n";
#		next;
#	    } elsif ($line =~ /^PRIMER_INTERNAL_MISHYB_LIBRARY=(\S*)/) {
#		my $v = $1;
#		# keep only filename (remove the path)
#		$v = basename($v);
#		print UPLOADFILE "PRIMER_MISPRIMING_LIBRARY=$v\n";
#		next;
#	    }
#	    print UPLOADFILE $line;
#	}
#	close UPLOADFILE;
#   }

    my $sequence_id = $query->param('SEQUENCE_ID');

    my $first_base_index = $query->param('PRIMER_FIRST_BASE_INDEX');
    if ($first_base_index !~ \S) {
      $first_base_index = 1;
    }

    # Fix the values of the checkboxes:
    my $therodynamicAlignment  = 0;
    my $pick_left  = 0;
    my $pick_internal = 0;
    my $pick_right = 0;
    my $liberal_base = 0;
    my $print_input = 0;
    my $ambiguity_Consensus = 0;
    my $lowercase_masking = 0;
    my $pick_anyway = 0;
    my $explain_flag = 0;

    if (defined $query->param('MUST_XLATE_PRIMER_THERMODYNAMIC_ALIGNMENT')) {
      $therodynamicAlignment = 1;
    }
    if (defined $query->param('MUST_XLATE_PRIMER_PICK_LEFT_PRIMER')) {
      $pick_left = 1;
    }
    if (defined $query->param('MUST_XLATE_PRIMER_PICK_INTERNAL_OLIGO')) {
      $pick_internal = 1;
    }
    if (defined $query->param('MUST_XLATE_PRIMER_PICK_RIGHT_PRIMER')) {
      $pick_right = 1;
    }
    if (defined $query->param('MUST_XLATE_PRIMER_LIBERAL_BASE')) {
      $liberal_base = 1;
    }
    if (defined $query->param('MUST_XLATE_PRINT_INPUT')) {
      $print_input = 1;
    }
    if (defined $query->param('MUST_XLATE_PRIMER_LIB_AMBIGUITY_CODES_CONSENSUS')) {
      $ambiguity_Consensus = 1;
    }
    if (defined $query->param('MUST_XLATE_PRIMER_LOWERCASE_MASKING')) {
      $lowercase_masking = 1;
    }
    if (defined $query->param('MUST_XLATE_PRIMER_PICK_ANYWAY')) {
      $pick_anyway = 1;
    }
    if (defined $query->param('MUST_XLATE_PRIMER_EXPLAIN_FLAG')) {
      $explain_flag = 1;
    }

    $pick_left     = 1 if $query->param('SEQUENCE_PRIMER');
    $pick_right    = 1 if $query->param('SEQUENCE_PRIMER_REVCOMP');
    $pick_internal = 1 if $query->param('SEQUENCE_INTERNAL_OLIGO');

    my $target = $query->param('SEQUENCE_TARGET');
    my $excluded_region = $query->param('SEQUENCE_EXCLUDED_REGION');
    my $included_region = $query->param('SEQUENCE_INCLUDED_REGION');
    my $overlap_pos = $query->param('SEQUENCE_OVERLAP_JUNCTION_LIST');

    my @input;

    for (@names) {
      next if /^Pick Primers$/;
      next if /^SEQUENCE_ID$/;
      next if /^PRIMER_FIRST_BASE_INDEX$/;
      next if /^MUST_XLATE/;
      next if /^SEQUENCE_TARGET$/;
      next if /^SEQUENCE_EXCLUDED_REGION$/;
      next if /^SEQUENCE_INCLUDED_REGION$/;
      next if /^SEQUENCE_OVERLAP_JUNCTION_LIST$/;
      next if /^input/;
	
      $v = $query->param($_);
      next if $v =~ /^\s*$/;   # Is this still the right behavior?

      if (/^SEQUENCE_TEMPLATE$/) {	
	if ($v =~ /^\s*>([^\n]*)/) {
	  # Sequence is in Fasta format.
	  $fasta_id = $1;
	  $fasta_id =~ s/^\s*//;
	  $fasta_id =~ s/\s*$//;
	  if (!$sequence_id) {
	    $sequence_id = $fasta_id;
	  } else {
	    print "<br>WARNING: 2 Sequence Ids provided: ",
	        "$sequence_id and $fasta_id; using ",
		"$sequence_id|$fasta_id\n";
	    $sequence_id .= "|$fasta_id";
	  }
	  $v =~ s/^\s*>([^\n]*)//;
	}
	if ($v =~ /\d/) {
	  print "<br>WARNING: Numbers in input sequence were deleted.\n";
	  $v =~ s/\d//g;
	}
	$v =~ s/\s//g;
	$v =~ s/-+/-/g;
	my ($m_target, $m_excluded_region, $m_included_region, $m_overlap_pos)
	  = read_sequence_markup($v, (['[', ']'], ['<','>'], ['{','}'], ['-','-']));
	$v =~ s/[\[\]\<\>\{\}]//g;
	$v =~ s/-//g;
	if (@$m_target) {
	  if ($target) {
	    print "<br>WARNING Targets specified both as sequence ",
	      "markups and in Other Per-Sequence Inputs\n";
	  }
	  $target = add_start_len_list($target, $m_target, $first_base_index);
	}
	if (@$m_excluded_region) {
	  if ($excluded_region) {
	    print "<br>WARNING Excluded Regions specified both as sequence ",
	      "markups and in Other Per-Sequence Inputs\n";
	  }
	  $excluded_region = add_start_len_list($excluded_region,
						$m_excluded_region,
						$first_base_index);
	}
	if (@$m_overlap_pos) {
	  if ($overlap_pos) {
	    print "<br>WARNING Overlap positions specified both as sequence ",
	      "markups and in Other Per-Sequence Inputs\n";
	  }
	  $overlap_pos = add_start_only_list($overlap_pos,
					     $m_overlap_pos,
					     $first_base_index);
	}
	if (@$m_included_region) {
	  if (scalar @$m_included_region > 1) {
	    print "<br>ERROR: Too many included regions\n";
	    $DO_NOT_PICK = 1;
	  } elsif ($included_region) {
	    print "<br>ERROR: Included region specified both as sequence\n",
	      "       markup and in Other Per-Sequence Inputs\n";
	    $DO_NOT_PICK = 1;
	  }
	  $included_region = add_start_len_list($included_region,
						$m_included_region,
						$first_base_index);
	}
      } elsif (/^PRIMER_(MISPRIMING|INTERNAL_MISHYB)_LIBRARY$/) {
	$v = $SEQ_LIBRARY{$v};
      } elsif (/^SEQUENCE_QUALITY$/) {
	$v =~ s/\s/ /sg;  # If value contains newlines (or other non-space whitespace)
	# change them to space.
      }
      $line = "$_=$v\n";
      push @input, $line;
    }
    if ($DO_NOT_PICK) {
      print "$wrapup\n";
      return;
    }
    push @input, "SEQUENCE_ID=$sequence_id\n";
    push @input, "PRIMER_FIRST_BASE_INDEX=$first_base_index\n";

    push @input, "PRIMER_THERMODYNAMIC_ALIGNMENT=$therodynamicAlignment\n";
    push @input, "PRIMER_PICK_LEFT_PRIMER=$pick_left\n";
    push @input, "PRIMER_PICK_INTERNAL_OLIGO=$pick_internal\n";
    push @input, "PRIMER_PICK_RIGHT_PRIMER=$pick_right\n";
    push @input, "PRIMER_LIBERAL_BASE=$liberal_base\n";
    push @input, "PRIMER_LIB_AMBIGUITY_CODES_CONSENSUS=$ambiguity_Consensus\n";
    push @input, "PRIMER_LOWERCASE_MASKING=$lowercase_masking\n";
    push @input, "PRIMER_PICK_ANYWAY=$pick_anyway\n";
    push @input, "PRIMER_EXPLAIN_FLAG=$explain_flag\n";

    push @input, "SEQUENCE_TARGET=$target\n" if $target;;
    push @input, "SEQUENCE_EXCLUDED_REGION=$excluded_region\n" if $excluded_region;
    push @input, "SEQUENCE_INCLUDED_REGION=$included_region\n" if $included_region;
    push @input, "SEQUENCE_OVERLAP_JUNCTION_LIST=$overlap_pos\n" if $overlap_pos;

    push @input, "=\n";

    my $file_name = $FILE_CACHE . makeUniqueID();
    my @readTheLine;
    open(FILE, ">$file_name") or
      print("Error: Cannot write $file_name");
    print FILE @input;
    close(FILE);

    my $cmd;
#    if (defined($settings)) {
#	$cmd = "/bin/nice -19 $PRIMER_BIN < $file_name -format_output -strict_tags -p3_settings_file=/tmp/$settings"; # for linux
#    } else {
	$cmd = "/bin/nice -19 $PRIMER_BIN < $file_name -format_output -strict_tags"; # for linux
#    }
    #my $cmd = "$PRIMER_BIN < $file_name -format_output -strict_tags"; # for windows

    open PRIMER3OUTPUT, "$cmd 2>&1 |"
      or print("Error: could not start primer3\n");
    while (<PRIMER3OUTPUT>) {
      push @readTheLine, $_;
    }
    close PRIMER3OUTPUT;
    unlink $file_name;

    print "<pre>\n";
    my $cline;
    my $results = '';
    foreach $cline (@readTheLine) {
      $cline =~ s/>/&gt;/g;
      $cline =~ s/</&lt;/g;
      if ($cline =~
	  /(.*)(start) (\s*\S+) (\s*\S+) (\s*\S+) (\s*\S+) (\s*\S+|) (\s*\S+) (\s*\S+)/) {
	my ($margin, $starth, $lenh, $tmh, $gch, $anyh, $threeh, $reph, $seqh) =
	  ($1, $2, $3, $4, $5, $6, $7, $8, $9);
	$cline =  $margin
	  . "<a href=\"$ODOC_URL#p3w_primer_start\">$starth</a> "
	    . "<a href=\"$ODOC_URL#p3w_primer_len\">$lenh</a> "
	      . "<a href=\"$ODOC_URL#p3w_primer_tm\">$tmh</a> "
		. "<a href=\"$ODOC_URL#p3w_primer_gc\">$gch</a> "
		  . "<a href=\"$ODOC_URL#p3w_primer_any\">$anyh</a> "
		    . "<a href=\"$ODOC_URL#p3w_primer_three\">$threeh</a> "
		      . "<a href=\"$ODOC_URL#p3w_primer_repeat\">$reph</a> "
			. "<a href=\"$ODOC_URL#p3w_primer_seq\">$seqh</a> "
			  . "\n";
      }
      if ($cline =~ /NO PRIMERS FOUND/) {
	$cline =~ s/NO PRIMERS FOUND/NO PRIMERS FOUND - <a href=\"$ODOC_URL#findNoPrimers\">Help<\/a>/g;
      }
      if ($cline =~ /^PRIMER PICKING RESULTS FOR\s*$/) {
      } else {
	$results .= $cline;
      }
    }

    print $results;
    print "</pre>\n";
    if ($print_input) {
      my ($user, $system, $cuser, $csystem) = times;
      printf "<pre>\nTIMES: user=%0.2f sys=%0.2f cuser=%0.2f csys=%0.2f</pre>",
	$user, $system, $cuser, $csystem;
      print "<pre>\nCOMMAND WAS: $cmd</pre>\n";
      print "<pre>\nEXACT INPUT WAS:\n";
      print @input, "</pre>";
      #print LOG @input; DOES NOT WORK CORRECTLY -- causes output to hang sometimes
    }
    print "$wrapup\n";
}

sub check_server_side_configuration
{
  my ($query) = @_;

  unless (-e $PRIMER_BIN) {
    print qq{Please clip and e-mail this page to $MAINTAINER: cannot find $PRIMER_BIN executable
	             $wrapup};
    exit;
  }
  unless (-x $PRIMER_BIN) {
    print qq{Please clip and e-mail this page to $MAINTAINER: wrong permissions for $PRIMER_BIN
	             $wrapup};
    exit;
  }
  if (!(-e $FILE_CACHE)) {
    if (!(mkdir($FILE_CACHE,0600))) {
      print qq{Please clip and e-mail this page to $MAINTAINER: error creating folder "$FILE_CACHE"
		             $wrapup};
      exit;
    }
  }

  # Check mispriming / mishyb library setup.
  my @names = $query->param;
  for (@names) {
    if (/^PRIMER_(MISPRIMING|INTERNAL_OLIGO_MISHYB)_LIBRARY$/) {
      $v = $query->param($_);
      $v1 = $SEQ_LIBRARY{'$v'};
      if (!defined($v)) {
        print qq{
            <h3>There is a configuration error at $tmpurl;
            cannot find a library file name for  "$v1".  Please clip and
            mail this page to $MAINTAINER.$wrapup</h3>
            };
        exit;
      }
      if ($v1 && ! -r $v1) {
        print qq{
            <h3>There is a configuration error at $tmpurl;
            library file $v1 cannot be read.  Please clip and
            mail this page to $MAINTAINER.$wrapup</h3>
            };
        exit;
      }
    }
  }
}

############################################################
### The following functions are also used by primer3plus ###
### in module                                            ###
############################################################

sub add_start_len_list($$$)
{
  my ($list_string, $list, $plus) = @_;
  my $sp = $list_string ? ' ' : '' ;
  for (@$list) {
    $list_string .= ($sp . ($_->[0] + $plus) . "," . $_->[1]);
    $sp = ' ';
  }
  return $list_string;
}

sub add_start_only_list($$$)
{
    my ($list_string, $list, $plus) = @_;
    my $sp = $list_string ? ' ' : '' ;
    for (@$list) {
    $list_string .= ($sp . ($_->[0] + $plus));
    $sp = ' ';
    }
    return $list_string;
}

sub read_sequence_markup($@)
{
    my ($s, @delims) = @_;
    # E.g. ['/','/'] would be ok in @delims, but
    # no two pairs in @delims may share a character.
    my @out = (); 
    for (@delims) {
	push @out, read_sequence_markup_1_delim($s, $_, @delims);
    }
    @out;
}

sub read_sequence_markup_1_delim($$@)
{
    my ($s,  $d, @delims) = @_;
    my ($d0, $d1) = @$d;
    my $other_delims = '';
    for (@delims) {
	next if $_->[0] eq $d0 and $_->[1] eq $d1;
	confess 'Programming error' if $_->[0] eq $d0;
	confess 'Programming error' if $_->[1] eq $d1;
	$other_delims .= '\\' . $_->[0] . '\\' . $_->[1];
    }
    if ($other_delims) {
    	$s =~ s/[$other_delims]//g;
    }
    # $s now contains only the delimters of interest.
    my @s = split(//, $s);
    my ($c, $pos) = (0, 0);
    my @out = ();
    my $len;
    while (@s) {
	$c = shift(@s);
	next if ($c eq ' '); # Already used delimeters are set to ' '
	if (($c eq $d0) && ($d0 eq $d1)) {
        push @out, [$pos, 0];
	}elsif ($c eq $d0) {
        $len = len_to_delim($d0, $d1, \@s);
        return undef if (!defined $len);
        push @out, [$pos, $len];
    } elsif ($c eq $d1) {
	    # There is a closing delimiter with no opening
	    # delimeter, an input error.
	    $DO_NOT_PICK = 1;
	    print "<br>ERROR IN SEQUENCE: closing delimiter $d1 not preceded by $d0\n";
	    return undef;
	} else {
	    $pos++;
	}
    }
    return \@out;
}

sub len_to_delim($$$)
{
    my ($d0, $d1, $s) = @_;
    my $i;
    my $len = 0;
    for $i (0..$#{$s}) {
	if ($s->[$i] eq $d0) {
	    # ignore it;
	} elsif ($s->[$i] eq $d1) {
	    $s->[$i] = ' ';
	    return $len;
	} else { $len++ }
    }
    # There was no terminating delim;
    $DO_NOT_PICK = 1;
    print "<br>ERROR IN SEQUENCE: closing delimiter $d1 did not follow $d0\n";
    return undef;
}

sub makeUniqueID
{
    my ( $UID, $randomNumber, $time );
    my ($second,     $minute,    $hour,
        $dayOfMonth, $month,     $yearOffset,
        $dayOfWeek,  $dayOfYear, $daylightSavings);
    (   $second,     $minute,    $hour,
        $dayOfMonth, $month,     $yearOffset,
        $dayOfWeek,  $dayOfYear, $daylightSavings ) = localtime();
    my $year = 1900 + $yearOffset;
    $month++;
    my $length = 7;
    for ( my $i = 0 ; $i < $length ; ) {
        my $j = chr( int( rand(127) ) );
        if ( $j =~ /[a-zA-Z0-9]/ ) {
            $randomNumber .= $j;
            $i++;
        }
    }
    $time = sprintf "%4d%02d%02d%02d%02d%02d", 
            $year, $month, $dayOfMonth, $hour, $minute, $second;
    $UID = $time . $randomNumber;

    return $UID;
}
