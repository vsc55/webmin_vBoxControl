#!/usr/bin/perl

use Data::Dumper;
require 'vboxctrl-lib.pl';
&ReadParse();

my $TEXT = $text{'VM_ISO'};
if ($in{'print'})
	{
	$TEXT .= "<br>(".get_system_hostname().")";
	}
ui_print_header(undef, $TEXT, "", undef, 1, 1);

my %DVDs = GetAllDVDS();
#print Dumper(\%DVDs)."<br>";

my (@TD) = (
		"width='5%' align='center'",
		"width='5%' align='center'",
		"width='10%' align='left'",
		"width='1%' align='center'",
		"width='1%'align='center'",
		"width='1%' align='center'",
		"width='15%' align='left'",
		);

my (@TABHEAD) = (
		$text{'tabhead_isouser'},
		$text{'tabhead_isousedby'},
		$text{'tabhead_isouuid'},
		$text{'tabhead_isoformat'},
		$text{'tabhead_isostate'},
		$text{'tabhead_isotype'},
		$text{'tabhead_isolocation'},
		);

if (! ($in{'print'}) )
	{
	print &ui_form_start("del_vmhd.cgi", "post");
	}

print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);

foreach my $KEY (sort keys %DVDs)
	{
	#print "'$KEY' => '$USER,$VM,$LOCATION'<br>";
	
	my ($USER,$VM,$LOCATION) = split(":" , $KEY);
	
	my $UUID = $DVDs{$KEY}->{'UUID'};
	my $FORMAT = $DVDs{$KEY}->{'Format'};
	my $LOCATION = $DVDs{$KEY}->{'Location'};
	my $STATE = $DVDs{$KEY}->{'State'};
	my $TYPE = $DVDs{$KEY}->{'Type'};
	my @USAGE = split("<br>", $DVDs{$KEY}->{'Usage'});
	my $NAME = $DVDs{$KEY}->{'Name'};
	
	$LOCATION = ($LOCATION)?$LOCATION:$NAME;
	my $USAGE;
	foreach my $DUMMY (@USAGE)
		{
		if ($DUMMY =~ /\(uuid\:+?/i)
			{
			$USAGE .= "$`<br>";
			}
		}
	my (@TABDATA);
	
	push (@TABDATA, $USER);
	push (@TABDATA, $USAGE);
	push (@TABDATA , $UUID);
	push (@TABDATA, $FORMAT);
	push (@TABDATA , $STATE);
	push (@TABDATA, $TYPE);
	push (@TABDATA , $LOCATION);
	
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
	#print &ui_submit($text{'vmhddel_title'}, "delete"),"<br>\n";
	print &ui_form_end();
	
	print "<br>";
	print "<a href='#' onclick=\"javascript:window.open('list_dvds.cgi?print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a>";
	print "<br>";
	print ui_print_footer("index.cgi?mode=host", $text{'index_return'});
	}



