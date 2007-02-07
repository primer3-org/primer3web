#!/usr/bin/perl -T

# ----- Installer Modifiable Variables -------------------------------------
# You may wish to modify the following variables to suit
# your installation.

# Who the end user will complain to:
$MAINTAINER
    ='primer3&#64;wi.mit.edu';

# Add mispriming / mishybing libraries;  make coordinate changes
# in primer3_www.cgi
%SEQ_LIBRARY=
    ('NONE' => '',
     'HUMAN' => 'humrep_and_simple.txt',
     'RODENT_AND_SIMPLE' => 'rodrep_and_simple.txt',
     'RODENT' => 'rodent_ref.txt',
     'DROSOPHILA' => 'drosophila.w.transposons.txt',
     # Put more repeat libraries here.
     );

# The URL for help regarding this screen (which will normally
# be in the same directory as the this script)
$ODOC_URL = "primer3_www_results_help.cgi";

# The location of the primer3_core executable.
$PRIMER_BIN =  "./primer3_core";

# If you make any substantial modifications give this code a new
# version designation.
$CGI_VERSION = "(primer3_www_results.cgi v 0.4)";
# 1a corrects a minor bug that deleted the 'PRIMER PICKING RESULTS FOR...'
# line even when the user supplied a sequence id.

# 0.4 corrects a bug that prevented picking hyb oligos

# ----- End Installer Modifiable Variables ---------------------------------

$COPYRIGHT = $COPYRIGHT = q{ 
 Copyright (c) 1996,1997,1998,1999,2000,2001,2004
        Whitehead Institute for Biomedical Research. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1.      Redistributions must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the  documentation
and/or other materials provided with the distribution.  Redistributions of
source code must also reproduce this information in the source code itself.

2.      If the program is modified, redistributions must include a notice
(in the same places as above) indicating that the redistributed program is
not identical to the version distributed by Whitehead Institute.

3.      All advertising materials mentioning features or use of this
software  must display the following acknowledgment:
        This product includes software developed by the
        Whitehead Institute for Biomedical Research.

4.      The name of the Whitehead Institute may not be used to endorse or
promote products derived from this software without specific prior written
permission.

We also request that use of this software be cited in publications as 

Steve Rozen, Helen J. Skaletsky (2000)
Primer3 on the WWW for general users and for biologist programmers.
In: Krawetz S, Misener S (eds)
Bioinformatics Methods and Protocols: Methods in Molecular Biology.
Humana Press, Totowa, NJ, pp 365-386
<a href="/primer3/primer3_code.html">
Source code available at http://fokker.wi.mit.edu/primer3/
</a>
<br>
THIS SOFTWARE IS PROVIDED BY THE WHITEHEAD INSTITUTE ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE WHITEHEAD INSTITUTE BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
};

BEGIN{
    print "Content-type: text/html\n\n";

    # Ensure that errors will go to the web browser.
    open(STDERR, ">&STDOUT");
    $| = 1;
    print '';
}

use FileHandle;
use IPC::Open3;

use Carp;

use CGI;
# The CGI module is available from CPAN

main();

sub main {

  $PR_DEFAULT_PRODUCT_MIN_SIZE = 100;
  $PR_DEFAULT_PRODUCT_MAX_SIZE = 1000;

  $query = new CGI;

  if ($query->param('Pick Primers')) {
      process_input($query);
  } else {
      confess "Did not see the 'Pick Primers' query parameter"
  }
}

sub check_server_side_configuration {
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

sub process_input {
    my ($query) = @_;
    my $wrapup = "<pre>$CGI_VERSION</pre>" . $query->end_html;
    my $tmpurl = $query->url;
    my ($v, $v1);

    local $DO_NOT_PICK = 0;

    print $query->start_html("Primer3 Output $CGI_VERSION");
    print qq{<h2>Primer3 Output</h2>\n};
    print "<hr>\n";

    check_server_side_configuration($query);

    my @names = $query->param;
    my $cmd = "/bin/nice -19 $PRIMER_BIN -format_output -strict_tags";
    my $line;
    my $fasta_id;

    my $sequence_id = $query->param('PRIMER_SEQUENCE_ID');
    my $min_prod_size = $query->param('MUST_XLATE_PRODUCT_MIN_SIZE');
    my $max_prod_size = $query->param('MUST_XLATE_PRODUCT_MAX_SIZE');
    $min_prod_size = $PR_DEFAULT_PRODUCT_MIN_SIZE unless $min_prod_size =~ /\S/;
    $max_prod_size = $PR_DEFAULT_PRODUCT_MAX_SIZE unless $max_prod_size =~ /\S/;
    my $size_range = "$min_prod_size-$max_prod_size";

    my $first_base_index = $query->param('PRIMER_FIRST_BASE_INDEX');
    if ($first_base_index !~ \S) {
	$first_base_index = 1;
    }

    my $pick_left  = $query->param('MUST_XLATE_PICK_LEFT');
    my $pick_hyb   = $query->param('MUST_XLATE_PICK_HYB_PROBE');
    my $pick_right = $query->param('MUST_XLATE_PICK_RIGHT');

    $pick_left  = 1 if $query->param('PRIMER_LEFT_INPUT');
    $pick_right = 1 if $query->param('PRIMER_RIGHT_INPUT');
    $pick_hyb   = 1 if $query->param('PRIMER_INTERNAL_OLIGO_INPUT');

    my $task;
    if ($pick_hyb) {
	if ($pick_right || $pick_left) {
	    $task='pick_pcr_primers_and_hyb_probe';
	    print "<br>WARNING: Assuming you want to pick a right primer because\n",
	          "         you are picking a left primer and internal oligo\n"
		if !$pick_right;
	    print "<br>WARNING: Assuming you want to pick a left primer because\n",
	          "         you are picking a right primer and internal oligo\n"
		if !$pick_left;
	} else {
	    $task='pick_hyb_probe_only';
	    if ($query->param('PRIMER_MISPRIMING_LIBRARY') 
		&& $query->param('PRIMER_MISPRIMING_LIBRARY') ne 'NONE') {  # fix for v 0.4
		print "<br>ERROR: you specifed a mispriming library but you ",
		"only requested a hybridization oligo. ",
		"Set the library at Hyb Oligo Mishyb Library.";
		$DO_NOT_PICK=1;
	    }
	}
    } else {
	if ($pick_right && $pick_left) {
	    $task='pick_pcr_primers';
	} elsif ($pick_right) {
	    $task='pick_right_only';
	} elsif ($pick_left) {
	    $task='pick_left_only';
	} else {
	    print "<br>WARNING: assuming you want to pick PCR primers\n";
	    $task='pick_pcr_primers';
	}
    }

    my $print_input = $query->param('MUST_XLATE_PRINT_INPUT');

    my $target = $query->param('TARGET');
    my $excluded_region = $query->param('EXCLUDED_REGION');
    my $included_region = $query->param('INCLUDED_REGION');
    my $inferred_sequence = '';
    if (!$query->param('SEQUENCE')) {
	if ($query->param('PRIMER_LEFT_INPUT')) {
	    $inferred_sequence = $query->param('PRIMER_LEFT_INPUT');
	}
	if ($query->param('PRIMER_INTERNAL_OLIGO_INPUT')) {
	    $inferred_sequence .= $query->param('PRIMER_INTERNAL_OLIGO_INPUT');
	}
	if ($query->param('PRIMER_RIGHT_INPUT')) {
	    my $tmp_seq = $query->param('PRIMER_RIGHT_INPUT');
	    $tmp_seq = scalar(reverse($tmp_seq));
	    $tmp_seq =~ tr/acgtACGT/tgcaTGCA/;
	    $inferred_sequence .= $tmp_seq;
	}
	if (!$inferred_sequence) {
	    print "<br>ERROR: you must supply a source sequence or primers/oligos to evaluate\n";
	    $DO_NOT_PICK=1;
	}
    }

    my @input;
    push @input, "PRIMER_EXPLAIN_FLAG=1\n";
    for (@names) {

	next if /^Pick Primers$/;
	next if /^old_obj_fn$/;
	next if /^PRIMER_SEQUENCE_ID$/;
	next if /^PRIMER_FIRST_BASE_INDEX$/;
	next if /^TARGET$/;
	next if /^INCLUDED_REGION$/;
	next if /^EXCLUDED_REGION$/;

	$v = $query->param($_);
	next if $v =~ /^\s*$/;   # Is this still the right behavior?

        if (/^SEQUENCE$/) {	
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
	    my ($m_target, $m_excluded_region, $m_included_region)
		    = read_sequence_markup($v, (['[', ']'], ['<','>'], ['{','}']));
	    $v =~ s/[\[\]\<\>\{\}]//g;
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


	} elsif (/^MUST_XLATE/) {
	    next if /^MUST_XLATE_PRODUCT_M(IN|AX)_SIZE$/;
	    next if /^MUST_XLATE_PICK_(LEFT|RIGHT|HYB_PROBE)$/;
	    next if /^MUST_XLATE_PRINT_INPUT$/;
	} elsif (/^PRIMER_(MISPRIMING|INTERNAL_OLIGO_MISHYB)_LIBRARY$/) {
	    $v = $SEQ_LIBRARY{$v};
	} elsif (/^PRIMER_MIN_SIZE$/ && $v < 1) {
	    print "<br>WARNING: Changed illegal Primer Size Min of $v to 1\n";
	    $v = 1;
	} elsif (/^PRIMER_PRODUCT_SIZE_RANGE$/) {
	    $v =~ s/,/ /g;
	} elsif (/^PRIMER_SEQUENCE_QUALITY$/) {
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
    push @input, "PRIMER_TASK=$task\n";
    push @input, "PRIMER_SEQUENCE_ID=$sequence_id\n";
    push @input, "PRIMER_PRODUCT_SIZE_RANGE=$size_range\n"
	unless $query->param('PRIMER_PRODUCT_SIZE_RANGE');
    push @input, "PRIMER_FIRST_BASE_INDEX=$first_base_index\n";
    push @input, "TARGET=$target\n" if $target;;
    push @input, "EXCLUDED_REGION=$excluded_region\n" if $excluded_region;
    push @input, "INCLUDED_REGION=$included_region\n" if $included_region;
    push @input, "SEQUENCE=$inferred_sequence\n" if $inferred_sequence;
    push @input, "PRIMER_PICK_ANYWAY=1\n";
    push @input, "=\n";

    # to keep taint happy
    my $savepath = $ENV{PATH};
    $ENV{PATH} = undef;

    my $primer3_pid;
    my ($childin, $childout) = (FileHandle->new, FileHandle->new);
    {
	local $^W = 0;
	$primer3_pid = open3($childin, $childout, $childout, $cmd);

    }
    if (!$primer3_pid) {
	print "Cannot excecure $cmd:<br>$!";
        print "$wrapup\n";
        exit;    
    }

    print "<pre>\n";
    print $childin @input;
    $childin->close;
    my $cline;
    my $results = '';
    my $found = 1;
    while ($cline = $childout->getline) {
	$cline =~ s/>/&gt;/g;
	$cline =~ s/</&lt;/g;
	if ($cline =~
	 /(.*)(start) (\s*\S+) (\s*\S+) (\s*\S+) (\s*\S+) (\s*\S+|) (\s*\S+) (\s*\S+)/) {
	    my ($margin, $starth, $lenh, $tmh, $gch, $anyh, $threeh, $reph, $seqh) =
		($1, $2, $3, $4, $5, $6, $7, $8, $9);
	    $cline =  $margin
		. "<a href=\"$ODOC_URL#PRIMER_START\">$starth</a> "
	    	. "<a href=\"$ODOC_URL#PRIMER_LEN\">$lenh</a> "
		. "<a href=\"$ODOC_URL#PRIMER_TM\">$tmh</a> "
		. "<a href=\"$ODOC_URL#PRIMER_GC\">$gch</a> "
		. "<a href=\"$ODOC_URL#PRIMER_ANY\">$anyh</a> "
		. "<a href=\"$ODOC_URL#PRIMER_THREE\">$threeh</a> "
		. "<a href=\"$ODOC_URL#PRIMER_REPEAT\">$reph</a> "
		. "<a href=\"$ODOC_URL#PRIMER_OLIGO_SEQ\">$seqh</a> "
		    . "\n";
	}
	$cline =~ s/INTERNAL OLIGO/HYB OLIGO     /;
	$cline =~ s/internal oligo/hyb oligo/;
	$cline =~ s/Intl/Hyb /;
	if ($cline =~ /NO PRIMERS FOUND/) {
	    $found = 0;
	} elsif ($cline =~ /^Statistics/ && !$found) {
	    $results .= no_primers_found() . $cline;
	} elsif ($cline =~ /^PRIMER PICKING RESULTS FOR\s*$/) {
	} else {
	    $results .= $cline;
	}
    }

    $ENV{PATH} = $savepath;

    print $results;
    print "</pre>\n";
    waitpid $primer3_pid, 0;
    if ($? != 0 && $? != 64512) { # 64512 == -4
        my $tmpnames = join("\n", @names);
        my $tmpurl = $query->url;
        print qq{
        <h3>Please clip and mail this page (including any
        information above this line) to $MAINTAINER (deleting your
        input sequence if you wish).</h3>
        <p>
	<h3>There is a configuration error or
        an unexpected internal error in the primer3 program at
        $tmpurl</h3>
        <p>
        <h3>The child process for $PRIMER_BIN was reaped with a non-0 termination
        status of $?.</h3>
        <p>
        <pre>
        \n};
	for (@names) {
	    $v = $query->param($_);
	    print "$_=$v\n";
	}
	print "<pre>\nCOMMAND WAS: $cmd</pre>\n";
	print "<pre>\nEXACT INPUT WAS:\n";
	print @input;
        print "</pre>\n";
    } elsif ($print_input) {
	my ($user, $system, $cuser, $csystem) = times;
	printf "<pre>\nTIMES: user=%0.2f sys=%0.2f cuser=%0.2f csys=%0.2f</pre>",
	$user, $system, $cuser, $csystem;
	print "<pre>\nCOMMAND WAS: $cmd</pre>\n";
	print "<pre>\nEXACT INPUT WAS:\n";
	print @input, "</pre>";
    }
    
    print "$wrapup\n";
}

sub no_primers_found {
    return qq{
</pre>
<h2>No Acceptable Primers Were Found</h2>

The statistics below should indicate why no acceptable
primers were found.
Try relaxing various parameters, including the
self-complementarity parameters and max and min oligo melting
temperatures.  For example, for very A-T-rich regions you might
have to increase maximum primer size or decrease minimum melting
temperature.

      <hr>

<pre>
}
}

sub add_start_len_list($$$) {
    my ($list_string, $list, $plus) = @_;
    my $sp = $list_string ? ' ' : '' ;
    for (@$list) {
	$list_string .= ($sp . ($_->[0] + $plus) . "," . $_->[1]);
	$sp = ' ';
    }
    return $list_string;
}

sub read_sequence_markup($@) {
    my ($s, @delims) = @_;
    # E.g. ['/','/'] would be ok in @delims, but
    # no two pairs in @delims may share a character.
    my @out = (); 
    for (@delims) {
	push @out, read_sequence_markup_1_delim($s, $_, @delims);
    }
    @out;
}

sub read_sequence_markup_1_delim($$@) {
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
	if ($c eq $d0) {
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

sub len_to_delim($$$) {
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
