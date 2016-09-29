#!/usr/bin/perl

require 'vboxctrl-lib.pl';
&ReadParse();

init_config();
$DEBUGMODE = $config{'DEBUGMODE'};
if ($DEBUGMODE)
	{
	DebugOut();
	}

my $VM = $in{'vm'};
my $USER = $in{'user'};

my $TEXT = $text{'view_vm'}." '$VM'";
if ($in{'print'})
	{
	$TEXT .= " (".get_system_hostname().")";
	}
ui_print_header(undef, $TEXT, "", undef, 1, 1);

my %PROP=GetVMProperty($USER, $VM);
my %VMINFO = GetVMInfo($USER,$VM);
my %EXTRA = GetVMExtradata($USER,$VM);


my (@TD) = ("width=1%","width=1%");

my (@TABHEAD) = ($text{'tabhead_info'},$text{'tabhead_infodesc'});
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
foreach $KEY (sort keys %VMINFO)
	{
	#print "View: $KEY --> $VMINFO{$KEY}<br>";
	my @TABDATA = ($KEY,$VMINFO{$KEY});
	print ui_columns_row(\@TABDATA,\@TD);
	}
print &ui_columns_end();
print "<hr>";

my (@TABHEAD) = ($text{'tabhead_property'},$text{'tabhead_propertydesc'});
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
foreach $KEY (sort keys %PROP)
	{
	#print "$KEY --> $PROP{$KEY}<br>";
	my @TABDATA = ($KEY,$PROP{$KEY});
	print ui_columns_row(\@TABDATA,\@TD);
	}
print &ui_columns_end();

print "<hr>";
my (@TABHEAD) = ($text{'tabhead_extradata'},$text{'tabhead_extradatadesc'});
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
foreach $KEY (sort keys %EXTRA)
	{
	#print "$KEY --> $PROP{$KEY}<br>";
	my @TABDATA = ($KEY,$EXTRA{$KEY});
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
	print "<a href='#' onclick=\"javascript:window.open('view_vm.cgi?vm=$VM&print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a> <br>";
	
	# Ruecksprung zur anfordernden Seite
	if ($in{'mode'})
		{
		#print "return -> index.cgi?mode=$in{'mode'}<br>";
		print ui_print_footer("index.cgi?mode=hdds", $text{'index_return'});
		}
	else
		{
		print ui_print_footer("index.cgi?mode=vm", $text{'index_return'});
		}
	}


