#!/usr/bin/perl

require 'vboxctrl-lib.pl';
&ReadParse();

init_config();

$DEBUGMODE = $config{'DEBUGMODE'};
if($DEBUGMODE)
	{
	DebugOut();
	}

my $TEXT = $text{'VM_SYSTEMPROPERTIES'};
if ($in{'print'})
	{
	$TEXT .= " (".get_system_hostname().")";
	}
ui_print_header(undef, $TEXT, "", undef, 1, 1);

my $SYSTEMPROPERTIES = GetSystemProperties();

my (@TD) = ("width=1%","width=1%");
my (@TABHEAD) = ($text{'tabhead_systemproperties'},$text{'tabhead_systempropertiesdesc'});

foreach my $USER (sort keys %{$SYSTEMPROPERTIES})
	{
	print "<br>";
	my (@TABHEAD2) = ("User $USER","");
	print &ui_columns_header(\@TABHEAD2);
	print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
	
	foreach my $KEY (sort keys %{$SYSTEMPROPERTIES->{$USER}})
		{
		my @TABDATA = ($KEY,$SYSTEMPROPERTIES->{$USER}->{$KEY});
		print ui_columns_row(\@TABDATA,\@TD);
		}
	print &ui_columns_end();
	}






if ($in{'print'})
	{
	print "<script type='text/javascript'>";
	print "window.print();";
	print "</script>";
	}
else
	{
	print "<br>";
	print "<a href='#' onclick=\"javascript:window.open('list_systemproperties.cgi?print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a> <br>";
	print ui_print_footer("index.cgi?mode=host", $text{'index_return'});
	}


