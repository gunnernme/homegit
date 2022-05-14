package tools;
my $version='$Header: /home/eao/perlbin/RCS/tools.pm,v 1.9 2005/05/09 16:37:05 eao Exp eao $';
sub get_version()
    {
    return $version;
    }
1;
package main;

sub basename($)
    {
	my $arg=shift;
	my $base;
    return $arg if ((!$arg) || !(($arg =~ /\//) or ($arg =~ /\\/)));
    ($base) = ($arg =~ /.*\/(.*)/) if ($arg=~ /\//);
    ($base) = ($arg =~ /.*\\(.*)/) if ($arg=~ /\\/);
    return $base;
    }

sub verstring($)
    {
	my $header=shift;
	my (@arr, $base, $date, $ver);

    @arr=split /\s+/, $header;
    return $header if (!$arr[1]);
    ($base)=basename($arr[1]);
    ($base)=($base =~ /([^,]+)/) if ($base !~ /,/);
    return $header if (!$base);
    $ver=$arr[2];
    $date=$arr[3];
    return "$base v$ver ($date)";
    }

sub version($)
    {
	my $version=shift;
    print verstring($version) ."\n";
    #print verstring($header) ."\n";
    }

sub dirname($)
    {
	my $arg=shift;
	my $dir;

    return "" if (!($arg =~ /\//));
    ($dir)= ($arg =~ /(.*\/)/);
    chop($dir);
    return $dir;
    }

sub stderr($)
    {
	my $arg=shift;

    chomp($arg);
    print STDERR "$arg\n";
    }

sub info($)
    {
    	my $arg=shift;

    chomp($arg);
    print STDERR "$arg\n";
    }

sub warning($)
    {
    	my $arg=shift;

    info("warning: $arg");
    }

sub chomp2($)
    {
	my $arg=shift;

    #
    # This function is essentially chomp for when you're not
    # sure if the line is going to be terminated with newline
    # or with carriage-return newline
    #
    chomp($arg);
    chop($arg) if (rindex($arg, "\r") == length($arg)-1);
    return($arg);
    }

sub runcmd($$$)
    {
	my $cmd=shift;
	my $filename=shift;
	my $quiet=shift;
	my @output;
	my ($orc, $rc);

    $orc=open FH, "$cmd 2>&1|";
    if (!$orc)
	{
	warn "Cannot execute command \"$cmd\": $!\n";
	return (101, undef);
	}
    @output=<FH>;
    $rc=close(FH);
    if ($?)
	{
	    my $tmp;

	$rc=($? >> 8);
	if (!$quiet)
	    {
	    print STDERR "   ". "WARNING: error code $rc returned from \"$cmd\"\n";
	    print STDERR "   ". "Output from command was:\n";
	    print STDERR "   ". "-" x 40, "\n";
	    for $tmp (@output)
		{
		print STDERR "   " . $tmp;
		}
	    print STDERR "   ". "-" x 40, "\n";
	    }
	}
    else
	{
	$rc=0;
	}
    if ($filename)
	{
	    my $line;

	$orc=open OH, ">>$filename";
	if (!$orc)
	    {
	    warn "Cannot open output filename \"$filename\" for runcmd \"$cmd\": $!\n";
	    return (101, undef);
	    }
	foreach $line(@output)
	    {
	    print OH $line;
	    }
	$orc=close(OH);
	if (!$orc)
	    {
	    warn "Cannot close output filename \"$filename\" for runcmd \"$cmd\": $!\n";
	    return (101, undef);
	    }
	}
    return($rc,  @output);
    }
1;
