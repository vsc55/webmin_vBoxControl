#!/usr/bin/perl

require 'vboxctrl-lib.pl';
use File::Basename;
&ReadParse();

my $TEXT = $text{'VM_HDDS'};
if ($in{'print'})
	{
	$TEXT .= "<br>(".get_system_hostname().")";
	}
ui_print_header(undef, $TEXT, "", undef, 1, 1);

my %HDs = ListHDDS();


my (@TD) = (
		"width='1%'",
		"width='1%'",
		"width='1%'",
		"width='7%' align='left'",
		"width='1%' align='center'",
		"width='7%' align='right'",
		"width='10%'align='center'",
		"width='1%' align='center'",
		"width='20%' align='center'"
		);
my (@TABHEAD) = (
		$text{''},
		$text{'tabhead_hduser'},
		$text{'tabhead_hdusedby'},
		$text{'tabhead_hd'},
		$text{'tabhead_hdformat'},
		$text{'tabhead_hdcurrsize'},
		$text{'tabhead_hdlogsize'},
		$text{'tabhead_hduuid'},
		$text{'tabhead_hdtype'},
		$text{'tabhead_hdlocation'}
		);

if (! ($in{'print'}) )
	{
	my (@linksrow) = ("<a href='new_hd.cgi'>New Harddisk</a>");
	print &ui_form_start("del_vmhd.cgi", "post");
	print &ui_links_row(\@linksrow);
	}

print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);

foreach my $HD (sort keys %HDs)
	{
	#print "\$HD => '$HD'<br>";
	my ($USER,$VM,$FILE) = split(":" , $HD);
	
	my %HDINFO = GetHDInfo($USER,$FILE);
	
	#print "<b>$USER - $HDHASH</b><br>";
	
	#my $VM = $HDs{$HD}->{'Usage'};
	my $CURRSIZE = $HDINFO{'Current size on disk'};
	my $LOGSIZE = $HDINFO{'Logical size'};
	my $UUID = $HDINFO{'UUID'};
	my $FORMAT = $HDINFO{'Storage format'};
	my $TYPE = $HDINFO{'Type'};
#	my $LOCATION = dirname($FILE);
#	my $FILENAME = basename($FILE);
#	
#	if ($FILENAME =~ /\./)
#		{
#		$FILENAME = $`;
#		}
	
	my($FILENAME,$LOCATION,$SUFFIX) = fileparse($FILE);
	if ($FILENAME =~ /$SUFFIX/)
		{
		$FILENAME = $`;
		}
	if ($LOCATION =~ /\/$/)
		{
		$LOCATION = $`;
		}
	
	$LOGSIZE =~ s/ytes//gi;
	$CURRSIZE =~ s/ytes//gi;
	
	my (@TABDATA);
	
	push(@TABDATA , $USER);
	push (@TABDATA, $VM);
	push (@TABDATA, $FILENAME);
	push (@TABDATA, $FORMAT);
#	if ($VM eq "none")
#		{
#		push (@TABDATA, $VM);
#		}
#	else
#		{
#		push (@TABDATA, "<a href='view_vm.cgi?user=$USER&vm=$VM&mode=hdds'>$VM</a>");
#		}
	
	push (@TABDATA, $CURRSIZE);
	push (@TABDATA, $LOGSIZE);
	push (@TABDATA, $UUID);
	push (@TABDATA, $TYPE);
	push (@TABDATA, $LOCATION);
	
	if ($VM)
		{
		# show default row
		unshift (@TABDATA , " ");
		print ui_columns_row(\@TABDATA,\@TD);
		}
	else
		{
		# show checked row
		print ui_checked_columns_row(\@TABDATA,\@TD,"vmhd",$HD);
		}
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
	print &ui_submit($text{'vmhddel_title'}, "delete"),"<br>\n";
	print &ui_form_end();
	
	print "<br>";
	print "<a href='#' onclick=\"javascript:window.open('list_hdds.cgi?print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a>";
	print "<br>";
	print ui_print_footer("index.cgi?mode=host", $text{'index_return'});
	}



