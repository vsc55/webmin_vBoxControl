#!/usr/bin/perl

use Switch;
use File::Basename;
require 'vboxctrl-lib.pl';
&ReadParse();
init_config();

$DEBUGMODE = $config{'DEBUGMODE'};
if($DEBUGMODE)
	{
	DebugOut();
	}

my $VM = $in{'vm'};
my $USER = $in{'user'};

my $VBOXBIN = $config{'PATH_VB_BIN'};
if (! ($VBBOXBIN =~ /\/$/))
	{
	$VBOXBIN .= "/";
	}

if ($config{'multiuser'})
	{
	$CMD_MULTIUSER = "sudo -H -u $USER ";
	}
else
	{
	$CMD_MULTIUSER = "";
	}

# activate this headercode only for debuging
ui_print_header(undef, text('VM_NIC',$VM), "", undef, 1, 1);

my @NIC = split(/\0/, $in{'nic'});
foreach my $DUMMY (@NIC)
	{
	
	if ( (exists $in{'update'}) | (exists $in{'add'}) )
		{
		# NAT ALIAS-Mode;
		my %ALIAS;
		$ALIAS{0} = "default";
		$ALIAS{1} = "log";
		$ALIAS{2} = "proxyonly";
		$ALIAS{4} = "sameports";
		
		my $COMMAND = $CMD_MULTIUSER;
		$COMMAND .= $VBOXBIN."VBoxManage -q modifyvm \"$VM\" ";
		$COMMAND .= "--nataliasmode$DUMMY ".$ALIAS{$in{"NATALIAS$DUMMY"}}." ";
		
		# Update NICTYPE
		$COMMAND .= "--nictype$DUMMY ".$in{"NIC$DUMMY"}." ";
		if ($in{"MAC$DUMMY"} ne "")
			{
			$COMMAND .= "--macaddress$DUMMY ".$in{"MAC$DUMMY"}." ";
			}
		
		my ($NICMODE,$BRIDGEIF) = split (":" , $in{"MODE$DUMMY"});
		
		$COMMAND .= "--nic$DUMMY $NICMODE ";
		
		if ($NICMODE eq "bridged")
			{
			$COMMAND .= "--bridgeadapter$DUMMY $BRIDGEIF ";
			}
		elsif ($NICMODE eq "hostonly")
			{
			$COMMAND .= "--hostonlyadapter$DUMMY $BRIDGEIF ";
			}
		
		
		$COMMAND .= "--cableconnected$DUMMY ".$in{"CONN$DUMMY"}." ";
		$COMMAND .= "--nictrace$DUMMY ".$in{"TRACE$DUMMY"}." ";
		
		$TRACEFILE = $in{"TRACEFILE$DUMMY"};
		
		$ERR = 0;
		if ($TRACEFILE ne "")
			{
			if ($TRACEFILE ne "none")
				{
				$DIR = dirname($TRACEFILE);
				if (! ($DIR =~ /\/$/))
					{
					$DIR .= "/";
					}
				
				# tracedirectory exists ?
				if (! (-e $DIR))
					{
					print "<font color='red'><b>ERROR: ";
					print text('nic_errtracedir'," <tt>'$TRACEFILE'</tt>");
					print "</b></font><p>\n";
					$ERR = 1;
					}
				}
			}
		else
			{
			$TRACEFILE = "none";
			}
		# No error with tracefile directory
		if (! $ERROR)
			{
			$COMMAND .= "--nictracefile$DUMMY \"$TRACEFILE\" ";
			}
		
		# Update NATNET
		$COMMAND .= "--natnet$DUMMY \"".lc($in{"NATNET$DUMMY"})."\" ";
		
		
		my ($RETURN);
		if (! $ERR)
			{
			$COMMAND .= " 2>&1";
			$RETURN = readpipe($COMMAND);
			if ($DEBUGMODE)
				{
				print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
				}
			}
		
		if ($RETURN)
			{
			print "<font color='red'><b>$RETURN</b></font> <p>\n";
			}
		my $HASH = \%in;
		$HASH->{'COMMAND'} = $COMMAND;
		$HASH->{'RETURN'} = $RETURN;
		my $ACTION;
		if (exists $in{'update'})
			{
			$ACTION = "Update NIC";
			}
		else
			{
			$ACTION = "Add NIC";
			}
		webmin_log("$ACTION","'".$in{"NIC$DUMMY"}."'","'$VM' ($USER)",\%in);
		}
	elsif (exists $in{'delete'})
		{
		#print "Daten Delete<br>";
		
		# first, set NIC-Mode
		my $COMMAND = $CMD_MULTIUSER;
		$COMMAND .= $VBOXBIN."VBoxManage -q modifyvm \"$VM\" ";
		$COMMAND .= "--nic$DUMMY null 2>&1";
		#print "<hr>$COMMAND<hr>";
		$RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
			}
		if ($RETURN)
			{
			print "<font color='red'><b>$RETURN</b></font> <p>\n";
			}
		
		# second, switch nic off
		my $COMMAND = $CMD_MULTIUSER;
		$COMMAND .= $VBOXBIN."VBoxManage -q modifyvm \"$VM\" ";
		$COMMAND .= "--nic$DUMMY none 2>&1";
		#print "<hr>$COMMAND<hr>";
		$RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
			}
		if ($RETURN)
			{
			print "<font color='red'><b>$RETURN</b></font> <p>\n";
			}
		my $HASH = \%in;
		$HASH->{'COMMAND'} = $COMMAND;
		$HASH->{'RETURN'} = $RETURN;
		webmin_log("Delete NIC","'".$in{"NIC$DUMMY"}."'","'$VM' ($USER)",\%in);
		}
	}

# Collect NICs
my %NIC = GetNIC($USER,$VM);

my (@NICMODE,@NICDATA,@NATALIAS,@TABHEAD,@TD, @linksrow);

my $COUNT = 0;
my $NIC_N;

ui_print_header(undef, text('VM_NIC',$VM), "", undef, 1, 1);

my $VMRUNNING = IsVMRunning($VM);
if ($VMRUNNING){print "<font color='red'><b>".text('HINT_VMRUNING',$VM)."</b></font><br>";}

# Set NICArray
push (@NICDATA , ["Am79C970A","PCnet-PCI II (Am79C970A)"]);
push (@NICDATA , ["Am79C973","PCnet-PCI III (Am79C973)"]);
push (@NICDATA , ["82540EM","Intel PRO/1000 MT Desktop (82540EM)"]);
push (@NICDATA , ["82543GC","Intel PRO/1000 T Server (82543GC)"]);
push (@NICDATA , ["82545EM","Intel PRO/1000 MT Server (82545EM)"]);
push (@NICDATA , ["virtio","Virtio-net (virtio)"]);

# Set NATAliasArray
push (@NATALIAS , [0,"default"]);
push (@NATALIAS , [1,"log"]);
push (@NATALIAS , [2,"proxyonly"]);
push (@NATALIAS , [4,"sameports"]);


my (@BRIDGE) = GetBridgedIfs();
my (@HOSTONLY) = GetHostOnlyIfs();

# NIC Connection mode
push (@NICMODE , ["null","Not attached"]);
push (@NICMODE , ["nat","NAT"]);
foreach my $DUMMY (@BRIDGE)
	{
	push (@NICMODE , ["bridged:${$DUMMY}{'Name'}","Bridged Adapter (${$DUMMY}{'Name'})"]);
	}
push (@NICMODE , ["intnet","Internal Network"]);
foreach my $DUMMY (@HOSTONLY)
	{
	push (@NICMODE , ["hostonly:${$DUMMY}{'Name'}","Host-only Adapter (${$DUMMY}{'Name'})"]);
	}
#push (@NICMODE , ["hostonly","Host-only Adapter"]);
push (@NICMODE , ["vde","Virtual Distributed Ethernet"]);

#foreach my $XXX (@NICMODE)
#	{
#	print "$XXX <br>";
#	foreach my $DATA (@{$XXX})
#		{
#		print "$DATA<br>";
#		}
#	print "===================<br>";
#	}



(@TABHEAD) = ($text{'tabhead_nic_select'},
		$text{'tabhead_nic_number'},
		$text{'tabhead_nic_type'},
		$text{'tabhead_nic_mac'},
		$text{'tabhead_nic_mode'},
		'NAT Net',
		$text{'tabhead_nic_natalias'},
		$text{'tabhead_nic_connect'},
		$text{'tabhead_nic_trace'},
		$text{'tabhead_nic_tracefile'}
		);

@TD = ("width=1%",
	"'width=1%' align='center'",
	"'width=10%' align='center'",
	"'width=10%' align='center'",
	"'width=10%' align='center'",
	"'width=10%' align='center'",
	"'width=10%' align='center'",
	"'width=1%' align='center'",
	"'width=1%' align='center'",
	"width=30%"
	);

my (@linksrow) = ( &select_all_link("nic", 0),&select_invert_link("nic", 0) );

# exist a nic for the VM ?
if (IsVMNIC($VM))
	{
	# Collect VM Info
	my %INFO = GetVMInfo($USER,$VM);
	
	my $VM_XML = $INFO{'Config file'};
	my $NATALIAS = Read_NatXML($VM_XML, 'fh00');
	
	print &ui_form_start("nic.cgi", "post");
	print &ui_links_row(\@linksrow);
	print ui_hidden("vm",$VM);
	print ui_hidden("user",$USER);
	print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
	
	foreach my $DUMMY (sort keys %NIC)
		{
		
		$NIC_N = $DUMMY;
		my ($NIC) = ${$NIC{$NIC_N}}{'Type'};
		my ($NIC_MAC) = ${$NIC{$NIC_N}}{'MAC'};
		my ($NIC_MODE) = ${$NIC{$NIC_N}}{'Attachment'};
		my ($NIC_CONNECT) = ${$NIC{$NIC_N}}{'Cable connected'};
		my ($NIC_TRACE) = ${$NIC{$NIC_N}}{'Trace'};
		my ($NIC_TRACEFILE);
		my ($BRIDGEIF);
		my $NATNET = $NATALIAS->{($NIC_N) - 1}->{'natnet'};
		if (!$NATNET){$NATNET = "Default";}
		
		
		#print "NIC_MODE: '$NIC_MODE'<br>";
		
		$NIC_TRACE =~ /\((.+)\)/;
		$NIC_TRACEFILE = $1;
		$NIC_TRACE =~ s/ \($NIC_TRACEFILE\)//i;
		
		$NIC_NATALIAS = $NATALIAS->{lc($NIC_MAC)};
		$NIC_NATALIAS = $NATALIAS->{$DUMMY-1}->{'alias'};
		#Translate the NIC-Mode
		if ($NIC_MODE =~ /none/i){$NIC_MODE = "none";}
		if ($NIC_MODE =~ /nat/i){$NIC_MODE = "nat";}
		
		if ($NIC_MODE =~ /bridged/i)
			{
			if ($' =~ /'(.+)'/)
				{
				$BRIDGEIF = $1;
				}
			$NIC_MODE = "bridged:$BRIDGEIF";
			}
		elsif ($NIC_MODE =~ /host-only/i)
			{
			if ($' =~ /'(.+)'/)
				{
				$HOSTONLYIF = $1;
				}
			$NIC_MODE = "hostonly:$HOSTONLYIF";
			}
		
		if ($NIC_MODE =~ /internal/i){$NIC_MODE = "intnet";}
		#if ($NIC_MODE =~ /host-only/i){$NIC_MODE = "hostonly";}
		if ($NIC_MODE =~ /vde/i){$NIC_MODE = "vde";}
		
		#($VRDP?"_on":"_off")
		#print "NIC_MODE: '$NIC_MODE'<br>";
		#$XXX = ($NIC_MODE eq "bridged")?"$NIC_MODE:$BRIDGEIF":"$NIC_MODE";
		#print "XXX: $XXX <br>";
		
		my @TABDATA = (
				"#$NIC_N",
				&ui_select("NIC$NIC_N", $NIC,\@NICDATA,1,0,0,$VMRUNNING),
				ui_textbox("MAC$NIC_N",$NIC_MAC,17,$VMRUNNING,12),
				&ui_select("MODE$NIC_N",$NIC_MODE,\@NICMODE,1,0,0,$VMRUNNING),
				ui_textbox("NATNET$NIC_N",$NATNET,12,$VMRUNNING,12),
				&ui_select("NATALIAS$NIC_N",$NIC_NATALIAS,\@NATALIAS,1,0,0,$VMRUNNING),
				&ui_select("CONN$NIC_N",$NIC_CONNECT,[["off","Off"],["on","On"]],1,0,0,$VMRUNNING),
				&ui_select("TRACE$NIC_N",$NIC_TRACE,[["off","Off"],["on","On"]],1,0,0,$VMRUNNING),
				ui_textbox("TRACEFILE$NIC_N",$NIC_TRACEFILE,20,$VMRUNNING)
				);
		
		print ui_checked_columns_row(\@TABDATA,\@TD,'nic',$NIC_N);
		
		
		}
	
	print &ui_columns_end();
	print &ui_links_row(\@linksrow);
	
	if (! $VMRUNNING)
		{
		print &ui_submit($text{'nic_update'}, "update"),&ui_submit($text{'nic_delete'}, "delete"),"<br>\n";
		}
	print &ui_form_end();
	
	}


# Add New NIC for VM

# delete "Set" from @TABHEAD
shift @TABHEAD;
unshift @TABHEAD, "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";

$NIC_N++;

my @TABDATA = (
		ui_hidden("nic",$NIC_N),
		"#$NIC_N",
		&ui_select("NIC$NIC_N",'',\@NICDATA),
		ui_textbox("MAC$NIC_N",'',17,0,12),
		&ui_select("MODE$NIC_N", '',\@NICMODE),
		ui_textbox("NATNET$NIC_N",'Default',12,0,12),
		&ui_select("NATALIAS$NIC_N",'',\@NATALIAS),
		&ui_select("CONN$NIC_N","on",[["off","Off"],["on","On"]]),
		&ui_select("TRACE$NIC_N",'',[["off","Off"],["on","On"]]),
		ui_textbox("TRACEFILE$NIC_N",'',20)
		);

# 8 NICs are supported
if ( ($NIC_N < 9) && (! $VMRUNNING) )
	{
	print &ui_form_start("nic.cgi", "post");
	print ui_hidden("vm",$VM);
	print ui_hidden("user",$USER);
	print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
	print ui_columns_row(\@TABDATA,\@TD);
	print &ui_columns_end();
	print &ui_submit(text('nic_add',"#$NIC_N"), "add"),"<br>\n";
	print &ui_form_end();
	}


print ui_print_footer("index.cgi?mode=vm", $text{'index_return'});


