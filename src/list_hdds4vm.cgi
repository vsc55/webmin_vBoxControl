#!/usr/bin/perl

require 'vboxctrl-lib.pl';
&ReadParse();
init_config();

$DEBUGMODE = $config{'DEBUGMODE'};
if($DEBUGMODE)
	{
	DebugOut();
	}

my $VBOXBIN = $config{'PATH_VB_BIN'};
if (! ($VBBOXBIN =~ /\/$/))
	{
	$VBOXBIN .= "/";
	}

my $ERR = 0;
my $VM = $in{'vm'};
my $USER = $in{'user'};

my $TEXT = text('HDD4VM',$VM);
if ($in{'print'})
	{
	$TEXT .= " (".get_system_hostname().")<br>($USER)";
	}
ui_print_header(undef, $TEXT, "", undef);

print "<script type='text/javascript'>";
print "window.print();";
print "</script>";

#my %DEVICENAME;
#
## Print out the properties of each HD
#
#my @USEDHDDS = GetHDDsFromVM($USER,$VM);
#my (@TD) = ("width='15%'","width='*'");
#my (@TABHEAD) = ($text{'tabhead_hdspec'},$text{'tabhead_hdspecdesc'});
#
#print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
#my $HD = 1;
#foreach my $HDUUID (@USEDHDDS)
#	{
#	print ui_columns_row(["<b> HDD #$HD </b>"],["colspan='2'"]);
#	foreach my $KEY (sort keys %{$HDUUID})
#		{
#		#print "$KEY -> ${$HDUUID}{$KEY}<br>";
#		my @TABDATA = ($KEY,${$HDUUID}{$KEY});
#		print ui_columns_row(\@TABDATA,\@TD);
#		}
#	print ui_columns_row([" "],["colspan='2'"]);
#	$HD++;
#	}
#print &ui_columns_end();

#*****************************************
# Print out the properties of each HD
#*****************************************
my @USEDHDDS = GetHDDsFromVM($USER,$VM);
my (@TD) = ("width='*'","width='*'");
my (@TABHEAD) = ($text{'tabhead_hdspec'},$text{'tabhead_hdspecdesc'});

my (@TD) = ("align='left'");
my (@TABHEADDESCR) = ($text{'tabhead_hdinfo_descr'});
print &ui_columns_start(\@TABHEADDESCR, 100, 0, \@TD);
print &ui_columns_end();

print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
my $HD = 1;
foreach my $HDUUID (@USEDHDDS)
	{
	print ui_columns_row(["<b> HDD #$HD </b>"],["colspan='2'"]);
	foreach my $KEY (sort keys %{$HDUUID})
		{
		#print "$KEY -> ${$HDUUID}{$KEY}<br>";
		my @TABDATA = ($KEY,${$HDUUID}{$KEY});
		print ui_columns_row(\@TABDATA,\@TD);
		}
	print ui_columns_row([" "],["colspan='2'"]);
	$HD++;
	}
print &ui_columns_end();

