#!/usr/bin/perl

require 'vboxctrl-lib.pl';

&ReadParse();
init_config();
$DEBUGMODE = $config{'DEBUGMODE'};
if ($DEBUGMODE)
	{
	DebugOut();
	}

my $VBOXBIN = $config{'PATH_VB_BIN'};
if (! ($VBBOXBIN =~ /\/$/))
	{
	$VBOXBIN .= "/";
	}


$COMMAND = $VBOXBIN."VBoxManage list extpacks 2>&1";
my @RETURN = readpipe($COMMAND);
if ($DEBUGMODE)
	{
	$RETURN = join ("" , @RETURN);
	$RETURN =~ s/\n/<br>/g;
	print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
	}

my $TEXT = $text{'VM_EXTENSIONS'};
if ($in{'print'})
	{
	$TEXT .= " (".get_system_hostname().")";
	}
ui_print_header(undef, $TEXT, "", undef, 1, 1);

my (@TD) = ("width=1%","width=1%");
my (@TABHEAD) = ($text{'tabhead_ostypes'},$text{'tabhead_ostypesdesc'});

print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);

foreach my $DUMMY (sort @RETURN)
	{
	my ($KEY, $VALUE) = split(":" , $DUMMY);
	my @TABDATA = ($KEY,$VALUE);
	print ui_columns_row(\@TABDATA,\@TD);
	}
print &ui_columns_end();

if ($in{'print'})
	{
	print "<script type='text/javascript'>";
	print "window.print();";
	print "</script>";
	}
else
	{
	print "<br>";
	print "<a href='#' onclick=\"javascript:window.open('list_extensions.cgi?print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a> <br>";
	print ui_print_footer("index.cgi?mode=host", $text{'index_return'});
	}

