#!/usr/bin/perl

use Switch;
require 'vboxctrl-lib.pl';
&ReadParse();
init_config();

$DEBUGMODE = $config{'DEBUGMODE'};
if($DEBUGMODE)
	{
	DebugOut();
	}


my $TEXT = $text{'PORTFORWARD_ALL_VMS'};
if ($in{'print'})
	{
	$TEXT .= " (".get_system_hostname().")";
	}
ui_print_header(undef, $TEXT, "", undef, 1, 1);

if ($config{'multiuser'})
	{
	@VBOXUSER = GetVBoxUser();
	}
else
	{
	@VBOXUSER = "root";
	}



$VMRUNNING = 1;

# Set NICTYPE Hash
my %NICTYPE;
$NICTYPE{'Am79C970A'} = "PCnet-PCI II";
$NICTYPE{'Am79C973'} = "PCnet-PCI III";
$NICTYPE{'82540EM'} = "Intel PRO/1000 MT Desktop";
$NICTYPE{'82543GC'} = "Intel PRO/1000 T Server";
$NICTYPE{'82545EM'} = "Intel PRO/1000 MT Server";
$NICTYPE{'virtio'} = "Virtio-net (virtio)";

my (@TABHEAD) = (
		$text{'tabhead_source'},
		$text{'tabhead_nic'},
		$text{'tabhead_service'},
		$text{'tabhead_protocol'},
		$text{'tabhead_hostip'},
		$text{'tabhead_hostport'},
		$text{'tabhead_direction'},
		$text{'tabhead_guestip'},
		$text{'tabhead_guestport'}
		);
my (@TD) = (
	"width=10%",
	"width=20%",
	"width=10%",
	"width=5%",
	"width=5%",
	"width=5%",
	"width=1% align='center'",
	"width=5%",
	"width=5%"
	);

my (@ALLVMS) = ListAllVM();

foreach my $DUMMY (@ALLVMS)
	{
	
	($USER,$VM) = split(":" , $DUMMY);
	
	# get VM info for VM xml path
	%INFO = GetVMInfo($USER,$VM);
	# figure out XML-File from VM
	my $XMLFILE = $INFO{'Config file'};
	# read NAT from each VM-XML
	my $VMNAT = Read_NatXML($XMLFILE, 'fh00');
	#$VMNAT->{$SLOT}->{'natrule'}->{$RULE}->{$KEY} = $VAL;
	
	# Collect NICs for type info
	my %NIC = GetNIC($USER,$VM);
	
	print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
	
	my $TITLE ="Edit portforwarding rules for VM $VM.";
	print ui_columns_row(["<a href='forward_vm.cgi?vm=$VM&user=$USER&state=1' title='$TITLE'><b>VM <i>'$VM' ($USER)</i></b></a>"],["colspan='9' align='center'"]);
	
	#my (%DATANAT) = GetNATPF($USER,$VM);
	
	# Portforwarding via NATRules
	for(my $SLOT = 0; $SLOT <= 7; $SLOT++)
		{
		foreach my $RULE (sort keys %{$VMNAT->{$SLOT}->{'natrule'}})
			{
			#print "$USER -> $VM -> $RULE<br>";
			
			
			my ($SERVICE) = $RULE;
			my ($PROTOCOL) = $VMNAT->{$SLOT}->{'natrule'}->{$RULE}->{'proto'};
			my ($GUESTIP) = $VMNAT->{$SLOT}->{'natrule'}->{$RULE}->{'guestip'};
			my ($GUESTPORT) = $VMNAT->{$SLOT}->{'natrule'}->{$RULE}->{'guestport'};
			my ($HOSTIP) = $VMNAT->{$SLOT}->{'natrule'}->{$RULE}->{'hostip'};
			my ($HOSTPORT) = $VMNAT->{$SLOT}->{'natrule'}->{$RULE}->{'hostport'};
			
			#my ($NIC_N,$B) = split("_" , $DUMMY);
			my ($NIC_TXT) = "#".($SLOT+1)." ".${$NIC{$SLOT+1}}{'Type'};
			$NIC_TXT .= " (".$NICTYPE{${$NIC{$SLOT+1}}{'Type'}}.")";
			
			my @TABDATA = (
					"natpf",
					$NIC_TXT,
					$SERVICE,
					$PROTOCOL,
					$HOSTIP,
					$HOSTPORT,
					"-->",
					$GUESTIP,
					$GUESTPORT
					);
			print ui_columns_row(\@TABDATA,\@TD);
			
			}
		}
	
	my(%DATAEXTRA) =GetVMExtraNICData($USER,$VM);
	
	# Portforwarding via ExtraData
	foreach $DUMMY(sort keys %DATAEXTRA)
		{
		
		foreach $DUMMY2(sort keys %{$DATAEXTRA{$DUMMY}})
			{
			#print"Key1: '$DUMMY' Key2: '$DUMMY2' -> '${$DATAEXTRA{$DUMMY}}{$DUMMY2}{'Protocol'}'<br>";
			
			my $SERVICE = $DUMMY2;
			my ($NICTYPE,$PROTOCOL) = split(":" , ${$DATAEXTRA{$DUMMY}}{$DUMMY2}{'Protocol'});
			my ($NICTYPE,$GUESTPORT) = split(":" , ${$DATAEXTRA{$DUMMY}}{$DUMMY2}{'GuestPort'});
			my ($NICTYPE,$HOSTPORT) = split(":" , ${$DATAEXTRA{$DUMMY}}{$DUMMY2}{'HostPort'});
			my $NIC = "$NICTYPE:$DUMMY";
			
			my $NIC_N = $DUMMY;
			$NIC_N++;
			my ($NIC_TXT) = "#$NIC_N ${$NIC{$NIC_N}}{'Type'}";
			
			$NIC_TXT .= " (".$NICTYPE{${$NIC{$NIC_N}}{'Type'}}.")";
			
			
			my @TABDATA = (
					"extradata",
					$NIC_TXT,
					$SERVICE,
					$PROTOCOL,
					"-",
					$HOSTPORT,
					"-->",
					"-",
					$GUESTPORT
					);
			print ui_columns_row(\@TABDATA,\@TD);
			}
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
	print "<a href='#' onclick=\"javascript:window.open('list_all_pfs.cgi?print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a> <br>";
	print ui_print_footer("index.cgi?mode=host", $text{'index_return'});
	}




