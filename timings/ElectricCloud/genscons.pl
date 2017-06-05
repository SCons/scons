#!/usr/bin/perl
#
# genscons.pl
#
# This script generates a build tree with $ndirs + 1 directories, containing
# $nfils source files each, and both SConstruct files and non-recursive
# Makefiles to build the tree.
#
# Copyright (c) 2010 Electric Cloud, Inc.
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Electric Cloud nor the names of its employees may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# These settings will generate 2,000 total C files, grouped in blocks of 20,
# each of which does a couple of #includes.

$nlvls = 2; $ndirs = 3; $nfils = 500; $nlups = 2; $group = 20;

$rmdel = "rm -f";
$OBJ = ".o";

# Check Variables settings

#if ( ($nfils % $group) != 0) {
#  die "ERROR: The number of files ($nfils) must be a multiple of the group size ($group)";
#}

sub init() {

#    use strict;
#    use warnings FATAL => 'all';
    use Getopt::Std;
    my $opt_string = 'd:f:g:l:u:h';
    getopts ( "$opt_string", \%opt) or usage ();

    &usage() if $opt{h};

    $ndirs      = $opt{d} if $opt{d};
    $nfils      = $opt{f} if $opt{f};
    $group      = $opt{g} if $opt{g};
    $nlvls      = $opt{l} if $opt{l};
    $nlups      = $opt{u} if $opt{u};

    return 0;
}

sub usage () {
    print STDERR << "EOF";

usage: $0 [-l Levels] [-d Dirs] [-f Files] [-g Grouping] [-u Lookups]
          [-h]

-l Levels   : number of levels of directories             (default $nlvls)
-d Dirs     : number of directories at each level         (default $ndirs)
-f Files    : number of source files per directory        (default $nfils)
-g Grouping : compile in groups of Grouping files         (default $group)
-u Lookups  : number of lookups per source file           (default $nlups)

-h         : this help message 

You can edit the default values in genscons.pl

EOF
    exit;
}

# fmt
#
# Adds commas to long numbers to make them more readable.
sub fmt {
    my ($value) = @_;
    my $running = 1;
    while ($running) {
        $value =~ s/([0-9])([0-9]{3})(?![0-9])/\1,\2/g;
        $running = ($1 =~ /[0-9]/);
    }
    return $value;
}

# gen_incfile
#
# Generate a generic include file to keep the compiler busy.
sub gen_incfile {
    my ($basedir, $filename, $idx) = @_;

    open (INC, "> $filename") || die "Cannot open $filename for output.";
    print INC "#ifndef $filname[$idx]\n"
        . "#define $filname[$idx] \"$basedir\"\n\n"
        . "#include \"stdio.h\"\n\n";
    print INC "#endif\n";
    close (INC);
}

# gen_cfile
#
# Generate a distinct C file to keep the compiler busy.
sub gen_cfile {
    my ($basedir, $filename, $idx) = @_;

    open (CFILE, "> $basedir/$filename")
        || die "Cannot open $basedir/$filename for output";

    $buff = "#include <stdlib.h>\n";
    $buff .= "#include <$filname[$idx].h>\n";

    $buff .= "#include <omega.h>\n";
    print CFILE $buff;

    if ($group == 1) {
        print CFILE "int main (int argc, char * argv[]) {\n"
            . "\tint i, mb_out;\n"
            . "\tprintf (\"I am $basedir/%s\\n\", \"$filname[$idx]\""
            . ");\n"
            . "\treturn (0);\n}\n";
    }
    elsif ( ($group - ($fil[$idx] % $group)) == 1) {
        print CFILE "int printr_$filname[$idx] (char * fname) {\n"
            . "    printf (\"I am $basedir/%s\\n\", fname);\n"
            . "    return (0);\n}\n";
    }
    elsif ( ($fil[$idx] % $group) == 0) {
        $idx2 = $fil[$idx] + 1;
        print CFILE "extern int printr_$file[$idx2] (char * fname);\n"
            . "int main (int argc, char * argv[]) {\n"
            . "\tint i, mb_out;\n"; 

        print CFILE "\tprintr_$file[$idx2] (\"$filname[$idx]\");\n"
            . "\n"
            . "\tmb_out = 0;\n"
            . "\tif (argc > 1) {\n"
            . "\t\tmb_out = atoi (argv[1]);\n"
            . "\t}\n"
            . "\tfor (i = 0; i < (mb_out * 16000); i++) {\n"
            . "\t\tprintf (\"%07d 9a123456789b123456789c12345"
            . "6789d123456789e123456789f12345678\\n\", i);\n"
            . "\t}\n"
            . "\texit (0);\n}\n";
    }
    else {
        $idx2 = $fil[$idx] + 1;
        print CFILE "extern int printr_$file[$idx2] (char * fname);\n"
            . "int printr_$filname[$idx] (char * fname) {\n"
            . "    printr_$file[$idx2] (fname);\n"
            . "    return (0);\n}\n";
    }
    close (CFILE);
}

# mkdirs
#
# Recursive function for generating directories full of files to build, and
# the makefiles that go with them.
#
sub mkdirs {
    my ($idx, $basedir, $thisLvl) = @_;

    if ( ! -d $basedir ) {
        mkdir $basedir || die "Cannot create folder $basedir: $!";
    }

    $relpath[$idx] = substr ($basedir, 8); # assumed top dir is "sconsbld"
    if ("$relpath[$idx]" eq "") {
        $relpath[$idx] = ".";
        $basestr = $basedir;
        $foo = "";
        $libdir = ".";
    }
    else {
        $basestr = $relpath[$idx];
        $basestr =~ s|/|_|g;
        $foo = substr($basedir,9) . "/";
        $libdir = substr($basedir,9);
    }
    $bstr[$idx] = $basestr; 

    $dirstr = $basedir;
    $dirstr =~ s|/|_|g;

#   $basedir is $relpath[$idx] with "sconsbld/" prepended so
#   $dirstr is $basestr with "sconsbld_" prepended.

    $cdstr = ".";
    for ($cdidx = 1; $cdidx < $thisLvl; $cdidx++) { $cdstr .= "/.."; }

    $thissc[$idx] = "$basedir/SConstruct";
    $thismk[$idx] = "$basedir/Makefile";
    $fzero[$idx] = "$basedir/file0";

    open (SC, "> $thissc[$idx]")
        || die "Cannot open $thissc[$idx] for output: $!";
    open (MK, "> $thismk[$idx]")
        || die "Cannot open $thismk[$idx] for output: $!";

    print SC "import os\n"
        . "env = Environment(ENV = os.environ)\n\n";

    my $cfgpath = "";
    for (my $junk = 1; $junk < $thisLvl; $junk++) { $cfgpath .= "../"; }

    my $arkive = "archive";

    if ($thisLvl == 1) { $mysubdir = "."; }
    else { $mysubdir = substr ($basedir, 8); }


    if (index ($basedir, "/") > 0) {
        @pieces = split (/\//, $basedir);
        $fileSuffix = "";
        for (my $ii =0; $ii <= $#pieces; $ii++) {
            $fileSuffix .= "_" . $pieces[$ii];
        }
    } else {
        $fileSuffix = "_" . $basedir;
    }

    for (my $lupsIdx = 0; $lupsIdx < $nlups; $lupsIdx++) {
        printf SC ("env.Append (CPPPATH = ['./lup%03d$fileSuffix'])\n",
                   $lupsIdx);
        if ($lupsIdx == 0) {
            $eq = "=";
        } else {
            $eq = "+=";
        }
        printf MK ("${foo}%%.o: CPPFLAGS $eq -I${foo}lup%03d$fileSuffix\n",
                   $lupsIdx);
    }
    print SC "env.Append (LIBPATH = ['.'])\n\n";
    print MK "${foo}%: LDFLAGS = -L$libdir\n\n";

    if ($thisLvl == 1) {
        print SC "\n"
            . "env.Help(\"\"\"\n"
            . "This build has parameters:\n"
            . "     number of levels  = $nlvls\n"
            . "     directories/level = $ndirs\n"
            . "     cfiles/directory  = $nfils\n"
            . "     lookups/source    = $nlups\n"
            . "     compiles grouped  = $group\n"
            . "\"\"\")\n";

        print MK "${foo}%.a:\n";
        print MK "\tar rc \$@ \$^\n";
        print MK "\tranlib \$@\n\n";
        print MK "%.o: %.c\n";
        print MK "\t\$(CC) -MMD -o \$@ -c \$(CPPFLAGS) \$<\n\n";
        print MK "%: %.o\n";
        print MK "\t\$(CC) -o \$@ \$< \$(LDFLAGS) -l\$(notdir \$@)\n\n";
        print MK "CC=gcc\n\n";
        print MK "all:\n\t\@ps -eo vsz,rss,comm | fgrep make\n\n";
    }
    print SC "\n";
    print MK "\n";

    # Create include directories for doing additional lookups.
    for (my $ii = 0; $ii < $nlups; $ii++) {
        $lupDir = sprintf ("lup%03d$fileSuffix", $ii);
        mkdir "$basedir/$lupDir" || die "Couldn't create $basedir/$lupDir: $!";
        $totald++;
    }

    $scfcc = "";
    $scfar = "";
    $mkfcc = "";
    $mkfar = "";

    ###
    ### generate the .c files and the .h files they include.
    ### Also generate the corresponding Makefile commands.
    ###
    for (my $filidx = 0; $filidx < $nfils; $filidx++) {
        $file[$filidx] = sprintf ("f%05d$fileSuffix", $filidx);
    }
    for ($fil[$idx] = 0; $fil[$idx] < $nfils; $fil[$idx]++) {
        $filname[$idx] = "$file[$fil[$idx]]";

        $nextnum = substr ($filname[$idx], 1, 5);

        if ($group == 1) {
#
#           Even when there are no groups, pre-compiled headers
#           still apply.
#
            print SC "env.Program ('$filname[$idx].c')\n\n";
        } #                end of $group == 1
#
#       Compile source files in groups.
#       This removes unique lookups but adds some :: rules.
#
        else {
            if ( ($fil[$idx] % $group) == 0) {
                if ("$scfcc" ne "") {
                    print SC "$scfcc\n$scfar\n\n";
                    $scfcc = "";
                    $scfar = "";
                }
                if ("$mkfcc" ne "") {
                    print MK "$mkfcc\n$mkfar\n\n";
                    $mkfcc = "";
                    $mkfar = "";
                }

                $groupFilename = "$filname[$idx]";
                $nextnum = substr ($filname[$idx], 1, 5);

                $scfcc = "env.Program('$filname[$idx]',\n"
                    . "\tLIBS=['$filname[$idx]'])\n";

                $scfar = "env.Library ('$filname[$idx]',\n"
                    . "\t['$filname[$idx].c'";

                $mkfcc = "TARGETS += ${foo}$filname[$idx]\n${foo}$filname[$idx]: ${foo}$filname[$idx].o ${foo}lib$filname[$idx].a\n";
                $mkfar = "${foo}lib$filname[$idx].a: ${foo}$filname[$idx].o";

                print MK "SRCS += ${foo}$filname[$idx].c\n";
                $tmpfnam = $filname[$idx];
                for ($filei = 1; $filei < $group; $filei++) {
                    $tmpfnum = sprintf ("%05d", $nextnum + $filei);
                    substr ($tmpfnam, 1, 5) = $tmpfnum;

                    $scfar .= ",\n\t '$tmpfnam.c'";
                    $mkfar .= " ${foo}$tmpfnam.o";
                    print MK "SRCS += ${foo}$tmpfnam.c\n";
                }
                $scfar .= "])\n\n";
                $mkfar .= "\n";
            }

        } # end of handling of compiles for $group > 1

        gen_incfile($basedir, "$basedir/$lupDir/$filname[$idx].h", $idx);

        if ($fil[$idx] == 0) {
            open (INC, "> $basedir/$lupDir/omega.h")
            || die "Cannot open $basedir/$lupDir/omega.h for output.";
            print INC "// comment in dummy file.\n";
            close (INC);
        }

        gen_cfile($basedir, "$filname[$idx].c", $idx);
    } # end of generation of source files and header files

    if ($group > 1 && "$scfcc" ne "") {
#
#       create makefile commands for the leftover files
#
        print SC "$scfcc\n$scfar\n\n";
        print MK "$mkfcc\n$mkfar\n\n";
    }

    close (SC);
    close (MK);

    # Recurse and create more subdirectories and their contents.
    if ($thisLvl < $nlvls) {
        $allsubs[$idx] = "";
        for ($dir[$idx] = 0; $dir[$idx] < $ndirs; $dir[$idx]++) {
            $dirname[$idx] = sprintf ("d${thisLvl}_%d", $dir[$idx]);
            $allsubs[$idx] .= "$dirname[$idx].subdir ";
#
#           divide the subdirectories into 2 lists
#           The two lists are/can be treated differently in Makefile.util
#
            if ($dir[$idx] < ($ndirs / 2)) {
                if ("$dirs1[$idx]" eq "") { $dirs1[$idx] = "$dirname[$idx]"; }
                elsif (index ($dirs1[$idx], $dirname[$idx]) < 0) {
                    $dirs1[$idx] .= " $dirname[$idx]";
                }
            }
            else {
                if ("$dirs2[$idx]" eq "") { $dirs2[$idx] = "$dirname[$idx]"; }
                elsif (index ($dirs2[$idx], $dirname[$idx]) < 0) {
                    $dirs2[$idx] .= " $dirname[$idx]";
#
#                   The preceding elsif should really just be
#                   "else" but when nlvls > 2, you start getting repetition
#                   of directory names in $dirs1[$idx] and $dirs2[$idx].
#                   Rather than figure out where the duplication is coming
#                   from, just prevent it.
#
                }
            }

            if ( ! -d "$basedir/$dirname[$idx]") {
                mkdir "$basedir/$dirname[$idx]" ||
                    die "Couldn't create $basedir/$dirname[$idx]: $!";
                $totald++;
            }

            &mkdirs ($idx + 1, "$basedir/$dirname[$idx]", $thisLvl + 1);
            if ($thisLvl == 1) {
                print "Finished folder $dirname[$idx] in $basedir at "
                    . `date`;
            }
        }

    }

    if ($thisLvl < $nlvls) {
        open (SC, ">> $thissc[$idx]")
            || die "Cannot open $thissc[$idx] for append: $!";
        open (MK, ">> $thismk[$idx]")
            || die "Cannot open $thismk[$idx] for append: $!";

        print SC "SConscript([";

        if (index ($dirs1[$idx], " ") > 0) {
            @subdirs = split (/ /, $dirs1[$idx]);
            for ($i = 0; $i <= $#subdirs; $i++) {
                print SC "'$subdirs[$i]/SConstruct',\n\t";
                print MK "include $subdirs[$i]/Makefile\n";
            }
        }
        else {
            print SC "'$dirs1[$idx]/SConstruct',\n\t";
            print MK "include $dirs1[$idx]/Makefile\n";
        }
        if (index ($dirs2[$idx], " ") > 0) {
            @subdirs = split (/ /, $dirs2[$idx]);
            for ($i = 0; $i < $#subdirs; $i++) {
                print SC "'$subdirs[$i]/SConstruct',\n\t";
                print MK "include $subdirs[$i]/Makefile\n";
            }
            print SC "'$subdirs[$#subdirs]/SConstruct'";
            print MK "include $subdirs[$#subdirs]/Makefile\n";
        }
        else {
            print SC "'$dirs2[$idx]/SConstruct'";
            print MK "include $dirs2[$idx]/Makefile\n";
        }
        print SC "])\n\n";
        print SC "\n";
        print MK "NUL=\n";
        print MK "SPACE=\$(NUL) \$(NUL)\n";
        print MK "define nl\n\$(SPACE)\n\$(SPACE)\nendef\n\n";
        print MK "all: \$(TARGETS)\n\n";
        print MK "clean:\n";
        print MK "\t\$(foreach tgt,\$(TARGETS),rm -f \$(tgt)\$(nl))\n";
        print MK "\tfor n in d1*; do rm -f \$\$n/*.o ; rm -f \$\$n/*.a;done\n";
        print MK "\trm -f *.o ; rm -f *.a\n\n";
        print MK "-include \$(SRCS:.c=.d)";

        close (SC);
        close (MK);
    }
    return 0;
}

$basedir = "sconsbld";
if ( ! -d $basedir) { mkdir $basedir || die "Couldn't create $basedir: $!"; }

&init ();

$numdirs = 0; # dirs other than include dirs
for ($i = 0; $i < $nlvls; $i++) { $numdirs += ($ndirs ** $i); }

$totldirs = $numdirs * ($nlups + 1); # dirs including include dirs

# total   = ( .c              ) + ( .h              ) + mkfiles + Makefile.util
#                                                               + Makefile.cfg
#                                                               + readme
#                                                               + omega.h
#                                                               + Makefile.clean

$totlfils = ($nfils * $numdirs) + ($nfils * $numdirs)
    + $numdirs + 3 + $numdirs;

$totlobjs = $nfils * $numdirs;
$totlexes = $numdirs * ($nfils / $group);

$totllups = $nfils * $numdirs * $nlups / $group;
$allfiles = $totlfils + $totlobjs + $totlexes;

# one rule for each group plus overhead of 10/makefile
$nrules = ($numdirs * $nfils / $group) + ($numdirs * 10);

$txt1 = "Number of levels = $nlvls\n"
      . "Number of dirs / level = $ndirs\n"
      . "Number of source files / dir = $nfils\n"
      . "Number of lookups / source file = $nlups\n"
      . "Number of compiles grouped      = $group\n";
print $txt1;

print $vartxt;
    $numMakefiles = 1;

$txt2 = "Expecting:\n"
      . "\tdirectories:   " . fmt($totldirs) . "\n"
      . "\tsource files:  " . fmt($numdirs * $nfils) . "\n"
      . "\tinclude files: " . fmt($numdirs * ($nfils + 1)) . "\n"
      . "\tmakefiles:     " . fmt($numdirs * $numMakefiles) 
                            . " ($numMakefiles per directory)\n"
      . "\ttotal files:   " . fmt($totlfils) . "\n"
      . "\tlook-ups: >=   " . fmt($totllups) . "\n"
      . "\trules: >=      " . fmt($nrules) . "\n";
print $txt2;

$txt3 = "When the build runs, " . fmt($totlobjs) . " object files & "
    . fmt($totlexes) . " executable(s)"
    . "\nwill be created, for a total of " . fmt($allfiles) . " files.\n";
print $txt3;

# Using local archives the number of conflicts is about the number of compiles
# which equals the number of archive writes.
#

if (-d $basedir) {
    print "Cleaning up from a previous run of this perl script.\n\n";
   system ("rm -rf $basedir/*");
}

###
### Generate README.txt
###
$readme = "$basedir/README.txt";
open (README, "> $readme") || die "Cannot open $readme for output.";

$txt = "\nStarted at " . `date` . "\n";
print $txt;
print README $txt
           . $vartxt
           . $txt1
           . $txt2
           . $txt3 || die "Cannot write txt, vartxt, txt1 etc to README";

###
### Do the heavy lifting
###

print "Start writing new files at " . `date` . "......\n";

$basedir0 = $basedir;
&mkdirs (0, $basedir, 1);

###
### Summarize the results to the README and the console
###

$txt = "\nFile creation ended at " . `date` . "\n";
print $txt; print README $txt || die "Cannot print txt to README";

close (README);
