#!/usr/bin/perl

require 'vboxctrl-lib.pl';
&ReadParse();

init_config();

$DEBUGMODE = $config{'DEBUGMODE'};
if($DEBUGMODE)
	{
	DebugOut();
	}

my @HOSTONLYIF = GetHostOnlyIfs();

my $TEXT = $text{'VM_HOSTONLYIF'};
if ($in{'print'})
	{
	$TEXT .= "<br>(".get_system_hostname().")";
	}

ui_print_header(undef, $TEXT, "", undef, 1, 1);

my (@TD) = ("width=1%","width=1%");
my (@TABHEAD) = ($text{'tabhead_hostonly'},$text{'tabhead_hostonlydesc'});

print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
foreach my $DUMMY (@HOSTONLYIF)
	{
	print ui_columns_row(["<b> Host Only Adapter ${$DUMMY}{'Name'}</b>"],["colspan=2 align=center"]);
	foreach my $KEY (sort keys %{$DUMMY})
		{
		#print "$KEY --> ${$DUMMY}{$KEY}<br>";
		my @TABDATA = ($KEY,${$DUMMY}{$KEY});
		print ui_columns_row(\@TABDATA,\@TD);
		}
	print ui_columns_row([" "],["colspan=2"]);
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
	print "<a href='#' onclick=\"javascript:window.open('list_hostonlyifs.cgi?print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a> <br>";
	print ui_print_footer("index.cgi?mode=host", $text{'index_return'});
	}





