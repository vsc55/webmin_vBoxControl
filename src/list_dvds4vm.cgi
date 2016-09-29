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
my @ISO = split(';',$in{'iso'});

my $TEXT = text('ISO4VM',$in{'vm'})." ($in{'user'})<br>";
$TEXT .= "(".get_system_hostname().")";
ui_print_header(undef, $TEXT, "", undef);

print "<script type='text/javascript'>";
print "window.print();";
print "</script>";

#*****************************************
# Print out the properties of each DVD
#*****************************************
my (@TD) = ("width='*'","width='*'");
my (@TABHEAD) = ($text{'tabhead_isospec'},$text{'tabhead_isospecdesc'});

my (@TD) = ("align='left'");
my (@TABHEADDESCR) = ($text{'tabhead_isoinfo_descr'});
print &ui_columns_start(\@TABHEADDESCR, 100, 0, \@TD);
print &ui_columns_end();

print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
my $DVD = 1;

my %ALLDVDS = GetAllDVDS();

foreach my $KEY (@ISO)
	{
	#print "\$KEY: '$KEY'<br>";
	
	print ui_columns_row(["<b> ISO #$DVD </b>"],["colspan='2'"]);
	foreach my $DVD (sort keys %{$ALLDVDS{$KEY}})
		{
		#print "\$DVD: '$DVD' => $ALLDVDS{$KEY}->{$DVD}<br>";
		
		my @TABDATA = ($DVD,$ALLDVDS{$KEY}->{$DVD});
		print ui_columns_row(\@TABDATA,\@TD);
		}
	print ui_columns_row([" "],["colspan='2'"]);
	$DVD++;
	}

print &ui_columns_end();

