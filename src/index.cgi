#!/usr/bin/perl

use WebminCore;
use Switch;
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
my $VBoxVersion = GetVBVersion();
$HEADER = "$module_info{'desc'} (V $module_info{'version'})<br>";
$HEADER .= "<font size='3'>VirtualBox $VBoxVersion</font>";
my $SHOWCONFIG = 1;
my $HIDEMODULEINDEX = 1;
my $HELP = "vboxctrl_help";
ui_print_header(undef, $HEADER, "", $HELP, $SHOWCONFIG, $HIDEMODULEINDEX);

#print "<b>'$remote_user'</b><br>";

switch($in{'action'})
	{
	case "Start"
		{
		$RET = StartVM($USER,$VM);
		}
	case "Pause"
		{
		$RET = StopVM($USER,$VM,0);
		}
	case "Resume"
		{
		$RET = StopVM($USER,$VM,1);
		}
	case "Reset"
		{
		$RET = StopVM($USER,$VM,2);
		}
	case "PowerOff"
		{
		$RET = StopVM($USER,$VM,3);
		}
	case "SaveState"
		{
		$RET = StopVM($USER,$VM,4);
		}
	case "Stop"
		{
		$RET = StopVM($USER,$VM,5);
		}
	}

if ($RET)
	{
	print "<hr><i>$RET</i><hr>";
	
	#$DUMMY = split("\n", $return);
	if ($RET=~ /ERROR\:(.*)\n/i)
		{
		print "<b>ERROR: $1</b><br>";
		}
	}

my (@TABS);

my $formno = 0;

push(@TABS, [ "host", $text{'TAB_HOST'},"index.cgi?mode=host"]);
push(@TABS, [ "vm", $text{'TAB_VM'},"index.cgi?mode=vm"]);
push(@TABS, [ "import", $text{'TAB_IMPORT'},"index.cgi?mode=import"]);
push(@TABS, [ "export", $text{'TAB_EXPORT'},"index.cgi?mode=export"]);
#push(@TABS, [ "hdds", $text{'TAB_HDDS'},"index.cgi?mode=hdds"]);


print &ui_tabs_start(\@TABS, "mode", $in{'mode'} || $TABS[0]->[0], 1);

print &ui_tabs_start_tab("mode", "host");
Host();
print &ui_tabs_end_tab("mode", "host");

print &ui_tabs_start_tab("mode", "vm");
VM();
print &ui_tabs_end_tab("mode", "vm");

print &ui_tabs_start_tab("mode", "import");
ImportVM();
print &ui_tabs_end_tab("mode", "import");

print &ui_tabs_start_tab("mode", "export");
ExportVM();
print &ui_tabs_end_tab("mode", "export");

#print &ui_tabs_start_tab("mode", "hdds");
#HDDS();
#print &ui_tabs_end_tab("mode", "hdds");

print &ui_tabs_end_tab();

ui_print_footer("/", $text{'index'});

#******************************

sub Host
	{
	
	@LINKS = (
		"list_hostinfo.cgi",
		"list_systemproperties.cgi",
		"list_bridgedifs.cgi",
		"list_hostonlyifs.cgi",
		"edit_dhcpservers.cgi",
		"list_ostypes.cgi",
		"list_all_pfs.cgi",
		"list_grp_vboxusers.cgi",
		"list_extensions.cgi",
		"list_hdds.cgi",
		"list_dvds.cgi",
		"list_moduleconfig.cgi",
		"vb_userconfig.cgi",
		);
	
	@TITLES = (
		"Host Info",
		"Host Properties",
		"Bridge Interfaces",
		"Host only Interfaces",
		"DHCP-Servers",
		"OS-Types",
		"Info all Portforwardings",
		"Info Group vboxusers",
		"Info Extension Packs",
		"VM Harddisks",
		"VM ISOs",
		"Module Config",
		"VBox User settings",
		);
	
	@ICONS = (
		"images/hostinfo.png",
		"images/hostproperties.png",
		"images/nic.gif",
		"images/nic.gif",
		"images/dhcpserver.png",
		"images/ostypes.png",
		"images/infoforwarding.gif",
		"images/groupinfo.png",
		"images/extensions.png",
		"images/hdd.png",
		"images/cd-icon.gif",
		"images/config.gif",
		"images/userconfig.png",
		);
	
	
	
	
	&icons_table(\@LINKS, \@TITLES, \@ICONS);
	
	$formno++;
	}



sub HDDS
	{
	my %SYS = GetSystemInfo();
	my %HDs = ListHDDS();
	
	my $HDPATH = $SYS{'Default hard disk folder'};
	#print "HDPATH: $HDPATH <br>";
	
	$COMMAND = "ls -m $HDPATH";
	$RET = readpipe($COMMAND);
	my @DIR = split("," , $RET);
	
	
	my (@TD) = (
			"width='1%'",
			"width='1%'",
			"width='1%'",
			"width='5%' align='right'",
			"width='7%' align='right'",
			"width='10%' align='center'",
			"width='1%' align='center'",
			"width='1%' align='center'",
			"width='20%'"
			);
	my (@TABHEAD) = (
			$text{''},
			$text{'tabhead_hduser'},
			$text{'tabhead_hdusedby'},
			$text{'tabhead_hdcurrsize'},
			$text{'tabhead_hdlogsize'},
			$text{'tabhead_hduuid'},
			$text{'tabhead_hdformat'},
			$text{'tabhead_hdtype'},
			$text{'tabhead_hdlocation'}
			);
	
	my (@linksrow) = ("<a href='new_hd.cgi'>New Harddisk</a>");
	
	print &ui_form_start("del_vmhd.cgi", "post");
	print &ui_links_row(\@linksrow);
	print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
	
	foreach my $HD (sort keys %HDs)
		{
		#print "\$HD => '$HD'<br>";
		my ($USER,$VM,$FILE) = split(":" , $HD);
		
		
		#print "<b>$USER - $HDHASH</b><br>";
		
		#my $VM = $HDs{$HD}->{'Usage'};
		my $CURRSIZE = $HDs{$HD}->{'Current size on disk'};
		my $LOGSIZE = $HDs{$HD}->{'Logical size'};
		my $UUID = $HDs{$HD}->{'UUID'};
		my $FORMAT = $HDs{$HD}->{'Storage format'};
		my $TYPE = $HDs{$HD}->{'Type'};
		my $LOCATION = $FILE;
		
		$LOGSIZE =~ s/ytes//gi;
		$CURRSIZE =~ s/ytes//gi;
		
		my (@TABDATA);
		
		push(@TABDATA , $USER);
		
		if ($VM eq "none")
			{
			push (@TABDATA, $VM);
			}
		else
			{
			push (@TABDATA, "<a href='view_vm.cgi?user=$USER&vm=$VM&mode=hdds'>$VM</a>");
			}
		
		push (@TABDATA, $CURRSIZE);
		push (@TABDATA, $LOGSIZE);
		push (@TABDATA, $UUID);
		push (@TABDATA, $FORMAT);
		push (@TABDATA, $TYPE);
		push (@TABDATA, $LOCATION);
		
		print ui_checked_columns_row(\@TABDATA,\@TD,"vmhd",$HD);
		
		}
	
	print &ui_columns_end();
	#print &ui_links_row(\@linksrow);
	print &ui_submit($text{'vmhddel_title'}, "delete"),"<br>\n";
	print &ui_form_end();
	
	print "<br>";
	print "<a href='#' onclick=\"javascript:window.open('list_hdds.cgi?print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a>";
	print "<br>";
	
	$formno++;
	}

#Snipped and modify from 'install_mod.cgi' WebMin Main Modules
sub ImportVM
	{
	
	my @VBOXUSER = GetVBoxUser();
	
	print &ui_form_start("import_vm.cgi","form-data");
	print &ui_table_start($text{'TABHEADER_IMPORT'}, undef, 2);
	
	#programming own hardcoded HTML
	print "\n<table border='0'>";
	if ($config{'multiuser'})
		{
		print "<tr><td><b>$text{'IMPORT_VMAS'}</b></td><td>".ui_select("imp_user","",\@VBOXUSER)."</td><td>&nbsp;</td></tr>";
		}
	my @RADIO = [2,$text{'IMPORT_VMOVFLOCALFILE'}];
	print "\n<tr><td rowspan='4'><b>$text{'IMPORT_VMSOURCE'}</b></td><td>".&ui_radio("to", 0,\@RADIO)."</td><td>".&ui_filebox("file_ova", "/", 40,0,50,"file_ovf")."</td></tr>";
	print "\n<tr><td colspan='2'><hr></td></tr>";
	
	my @RADIO = [0,$text{'IMPORT_VMUPLOADFILE'}];
	print "\n<tr><td>".&ui_radio("to", 0,\@RADIO)."</td><td>".&ui_upload("upload", 40)."</td></tr>";
	my @RADIO = [1,$text{'IMPORT_VMGZLOCALFILE'}];
	print "\n<tr><td>".&ui_radio("to", 0,\@RADIO)."</td><td>".&ui_filebox("file_tgz", "/", 40,0,50,"file_tgz")."</td></tr>";
	
	print &ui_table_end();
	print &ui_form_end([ [ "ok", $text{'IMPORT_VMOK'} ] ]);
	$formno++;
	
	}



#Snipped and modify from 'edit_mods.cgi' WebMin Main Modules
sub ExportVM
	{
	#print "Form: $formno - export_vm.cgi<br>";
	my @DUMMY = ListAllVM();
	
	foreach my $DUMMY (sort @DUMMY)
		{
		my ($user,$vm) = split(":" , $DUMMY);
		push(@VMS ,[$DUMMY,"$vm ($user)"]);
		}
	
	print &ui_form_start("export_vm.cgi");
	print &ui_table_start($text{'TABHEADER_EXPORT'}, undef, 2);
	
	#programming own hardcoded HTML
	
	print "<table border='0'>";
	print "<tr><td><b>$text{'EXPORT_VMMODE'}</b></td><td>".&ui_select("vms", undef,\@VMS, 10, 1)."</td><td>&nbsp;</td></tr>";
	my @RADIO = [0,$text{'EXPORT_VMBROWSER'}];
	print "<tr><td rowspan='3'><b>$text{'EXPORT_VMTO'}</b></td><td>".&ui_radio("to", 0,\@RADIO)."</td><td>&nbsp;</td></tr>";
	my @RADIO = [1,$text{'EXPORT_TGZFILE'}];
	print "<tr><td>".&ui_radio("to", 0,\@RADIO)."</td><td>".&ui_filebox("file_tgz", "/", 40,0,50,"file_tgz",1)."</td></tr>";
	my @RADIO = [2,$text{'EXPORT_OVFFILE'}];
	print "<tr><td>".&ui_radio("to", 0,\@RADIO)."</td><td>".&ui_filebox("file_ova", "/", 40,0,50,"file_tgz",1)."</td></tr>";
	
	print &ui_table_end();
	print &ui_form_end([ [ "ok", $text{'EXPORT_VMOK'} ] ]);
	$formno++;
	}

sub VM
	{
	my ($STARTUPVM,$ERROR) = ReadEnabledVM();
	my $STARTUPUSER = GetStartupUser();
	
	my @VMS = ListAllVM();
	my @VRDE;
	
	my (@TD) = (
			"width=1%",
			"width=1% align='center'",
			"width=1% align='center'",
			"width=1% align='center'",
			"width=1% align='center'",
			"width=1% align='center'",
			"width=1% align='center'",
			"width=1% align='center'",
			"width=5% align='center'",
			"width=1% align='center'",
			"width=5% align='center'",
			"width=1%",
			"width=1%",
			"width=1%",
			"width=1%",
			"width=1%",
			"width=1%",
			"width=1%",
			"width=5% align='center'",
			
			);
	my (@TABHEAD) = (
			$text{'tabhead_account'},
			$text{'tabhead_vm'},
			$text{'tabhead_vmaddon'},
			$text{'tabhead_comment'},
			$text{'tabhead_forwarding'},
			$text{'tabhead_hd'},
			$text{'tabhead_iso'},
			$text{'tabhead_nic'},
			$text{'tabhead_vmvrdp'},
			$text{'tabhead_vmos'},
			$text{'tabhead_vmstate'},
			$text{'tabhead_vmaction'},
			"",
			"",
			"",
			"",
			"",
			"",
			"",
			);
	
	my (@linksrow) = ("<a href='new_vm.cgi'>$text{'VM_NEW'}</a>");
	
	print &ui_links_row(\@linksrow);
	print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
	
	my $ISVMADMIN = IsAdmin($remote_user);
	
	foreach my $DUMMY (sort @VMS)
		{
		
		($USER,$DUMMY) = split(":" , $DUMMY);
		
		if ( (! $ISVMADMIN ) && ($remote_user ne $USER) ){next;}
			#{
			
			#print "Form: $formno - index.cgi<br>";
			print &ui_form_start("index.cgi?mode=vm", "post");
			my %VMINFO = GetVMInfo($USER,$DUMMY);
			my %VMPROP=GetVMProperty($USER,$DUMMY);
			
			# Create NICTTITLE item
			# For increase the speed, i dont want to use the function GetNIC()
			#therefore i use the same code here
			my $NICTITLE;
			for (my $i=1;$i<=8;$i++)
				{
				#print "$DUMMY: '".$VMINFO{'NIC '.$i}."' <br>";
				
				if (! ($VMINFO{'NIC '.$i} =~ /disabled/i) )
					{
					
					my @VALS = split("," , $VMINFO{'NIC '.$i});
					foreach my $DUMMY2 (@VALS)
						{
						my ($KEY2,$VAL2) = split(":" , $DUMMY2);
						
						$KEY2 =~ s/^\s+//g;
						$KEY2 =~ s/\s+$//g;
						$VAL2 =~ s/^\s+//g;
						$VAL2 =~ s/\s+$//g;
						$VAL2 =~ s/\'//g;
						
						if (($KEY2 =~ /attachment/i))
							{
							$NICTITLE .= "NIC#$i->$VAL2 | ";
							}
						}
					}
				}
			
			my %DATAEXTRA =GetVMExtraNICData($USER, $DUMMY);
			my $XMLFILE = $VMINFO{'Config file'};
			my $VMNAT = Read_NatXML($XMLFILE, 'fh00');
			
			my $NATTITLE;
			
			if (%DATAEXTRA)
				{
				$NAT = 1;
				}
			elsif ($VMNAT->{'NAT'})
				{
				$NAT = 1;
				
				foreach my $SLOT (sort keys %{$VMNAT})
					{
					
					#workaround for bug in Read_NatXML()
					if ($SLOT =~ /nat/i){next;}
					
					if (exists($VMNAT->{$SLOT}->{'natrule'}))
						{
						$NATTITLE .= " | NIC#$SLOT ";
						}
					
					foreach my $RULE (keys %{$VMNAT->{$SLOT}->{'natrule'}})
						{
						my $HOSTPORT = $VMNAT->{$SLOT}->{'natrule'}->{$RULE}->{'hostport'};
						my $GUESTPORT = $VMNAT->{$SLOT}->{'natrule'}->{$RULE}->{'guestport'};
						
						$NATTITLE .= "$RULE:$HOSTPORT->$GUESTPORT ";
						}
					}
				}
			else
				{
				$NAT = 0;
				}
			
			my ($PRODUCT, $USERS);
			
			my $STATE = $VMINFO{'State'};
			
			if (exists $VMPROP{'/VirtualBox/GuestInfo/OS/Product'})
				{
				$PRODUCT = $VMPROP{'/VirtualBox/GuestInfo/OS/Product'};
				if ($PRODUCT =~ /\,/)
					{
					$PRODUCT = $`;
					}
				}
			else
				{
				$PRODUCT = "-";
				}
			
			if (exists $VMPROP{'/VirtualBox/GuestInfo/OS/LoggedInUsersList'})
				{
				$USERS = $VMPROP{'/VirtualBox/GuestInfo/OS/LoggedInUsersList'};
				if ($USERS =~ /timestamp/i)
					{
					$USERS = $`;
					$USERS =~ s/, //;
					}
				}
			
			my ($VRDEPORT, $VRDEIP, $VRDPAUTH);
			my $LINE = $VMINFO{'VRDE'};
			my ($VRDE,$B) = split(" " , $LINE);
			$VRDE =~ s/\(//;
			$VRDE =~ s/\s//;
			$VRDE =($VRDE eq "enabled")?1:0;
			
			if ($VRDE)
				{
				$LINE =~ /.*(\(.*\))/g;
				$LINE = $1;
				$LINE =~ s/\(//;
				$LINE =~ s/\)//;
				
				@VRDE = split(", " , $LINE);
				
				foreach my $DUMMY3 (@VRDE)
					{
					if ($DUMMY3 =~ /ports/gi)
						{
						$VRDEPORT = $';
						$VRDEPORT =~ s/\s//;
						#$VRDEPORT ="($VRDEPORT)";
						}
					elsif ($DUMMY3 =~ /address/gi)
						{
						$VRDEIP = $';
						$VRDEIP =~ s/\s//;
						#$VRDEIP ="($VRDEPORT)";
						}
					}
				}
			
			my $TITLE1 = "Edit portforwarding rules of VM $DUMMY $NATTITLE";
			my $TITLE2 = "Show propertys of VM $DUMMY";
			
			$X = "";
			if ( (! $ERROR) && ($STARTUPUSER eq $USER) )
				{
				if (exists $STARTUPVM->{$DUMMY})
					{
					my $TITLE = text('VM_DISABLE',$DUMMY,$config{'FILE_VM_ENABLED'});
					$VM_EN_TXT = "<a href='toggle_vmenabled.cgi?clear=$DUMMY' title='$TITLE'><img src='images/not.gif3.png' border='0'></a>";
					}
				else
					{
					my $TITLE = text('VM_ENABLE',$DUMMY,$config{'FILE_VM_ENABLED'});
					$VM_EN_TXT = "<a href='toggle_vmenabled.cgi?set=$DUMMY' title='$TITLE'><img src='images/down.gif.png' border='0'></a>";
					}
				}
			
			$DESCRIPTION = GetVMDesc($XMLFILE);
			if ($DESCRIPTION)
				{
				$COMMENT = "<a href='#' title='$DESCRIPTION'><img src='images/comment.gif' border='1'></a>";
				}
			else
				{
				$COMMENT = "<img src='images/nocomment.gif' border='1'>";
				}
			
			my (@TABDATA, @DUMMY2);
			if ($STATE =~ /running/i)
				{
				push (@TABDATA, "<font color='green'><b>$USER</b></font>");
				}
			else
				{
				push (@TABDATA, "<b>$USER</b>");
				}
			
			my $V_GAO = GetGuestAddonVersion($USER,$DUMMY);
			my ($V_VB,$ADDONIMG);
			if ($VBoxVersion =~ /r/i)
				{
				$V_VB = $`;
				$V_VB =~ s/^\s+//g;
				$V_VB =~ s/\s+$//g;
				}
			
			if ($V_GAO =~ /^No/i)
				{
				$ADDONIMG = "<img src='images/GuestAddOn_no.gif' ";
				$ADDONIMG .= "title='No Guestaddon installed'>";
				}
			elsif($V_GAO eq $V_VB)
				{
				$ADDONIMG = "<img src='images/GuestAddOn_ok.gif' ";
				$ADDONIMG .= "title='Guestaddon V $V_VB installed'>";
				}
			else
				{
				$ADDONIMG = "<img src='images/GuestAddOn_err.gif' ";
				$ADDONIMG .= "title='Wrong Guestaddon Version installed. Current $V_GAO should be $V_VB'>";
				}
			
			push (@TABDATA, ui_hidden("vm",$DUMMY).ui_hidden("user",$USER)." <a href='view_vm.cgi?vm=$DUMMY&user=$USER' title='$TITLE2'>$DUMMY</a><br>$VM_EN_TXT");
			push (@TABDATA, $ADDONIMG);
			push (@TABDATA, "$COMMENT");
			push (@TABDATA, "<a href='forward_vm.cgi?vm=$DUMMY&user=$USER&mode=vm' title='$TITLE1'><img src='images/forward".($NAT?"_on":"_off").".gif' border='1'></a>");
			push (@TABDATA, "<a href='edit_hdds4vm.cgi?vm=$DUMMY&user=$USER'><img src='images/hdd.png' border='0'></a>");
			push (@TABDATA, "<a href='edit_dvds4vm.cgi?vm=$DUMMY&user=$USER'><img src='images/cd-icon.gif' border='0'></a>");
			push (@TABDATA, "<a href='nic.cgi?vm=$DUMMY&user=$USER&mode=vm' title='$NICTITLE'><img src='images/nic.gif' border='0'></a>");
			if ($VRDE)
				{
				$VRDEIPPORT = "($VRDEIP:$VRDEPORT)";
				}
			else
				{
				$VRDEIPPORT = "";
				}
			push (@TABDATA, "<a href='vrde.cgi?vm=$DUMMY&user=$USER&mode=vm'><img src='images/vrde".($VRDE?"_on":"_off").".gif' border='0'></a><br>$VRDEIPPORT");
			
			push (@TABDATA, $VMINFO{'Guest OS'});
			
			switch($STATE)
				{
				$STATE =~ /\(/;
				
				case /running/
					{
					push(@TABDATA,"<image src='images/up.gif.png' alt='$text{'img_on'}'><br>$`");
					@DUMMY2 = SetButtons("1,0,1,0,0,0,0");
					}
				case /powered off/
					{
					push(@TABDATA,"<image src='images/down.gif.png' alt='$text{'img_off'}'><br>$`");
					@DUMMY2 = SetButtons("0,1,1,1,1,1,1");
					}
				case /saved/
					{
					push(@TABDATA,"<image src='images/down.gif.png' alt='$text{'img_off'}'><br>$`");
					@DUMMY2 = SetButtons("0,1,0,0,0,1,0");
					}
				case /paused/
					{
					push(@TABDATA,"<image src='images/paused.gif' alt='$text{'img_off'}'><br>$`");
					@DUMMY2 = SetButtons("0,1,0,1,0,1,1");
					}
				case /restoring/
					{
					push(@TABDATA,"<image src='images/up.gif.png' alt='$text{'img_on'}'><br>$`");
					@DUMMY2 = SetButtons("1,0,1,0,0,0,0");
					}
				case /starting/
					{
					push(@TABDATA,"<image src='images/up.gif.png' alt='$text{'img_on'}'><br>$`");
					@DUMMY2 = SetButtons("1,0,1,0,0,0,0");
					}
				default:
					{
					push(@TABDATA,"<image src='images/blank.gif'><br>$`");
					@DUMMY2 = SetButtons("0,0,0,0,0,0,0");
					}
				}
			
			#my @DUMMY2 = SetButtons("0,1,1,0,1,1,0");
			foreach my $DUMMY2 (@DUMMY2)
				{
				push(@TABDATA ,$DUMMY2);
				}
			
			#window.confirm('Link folgen?');
			
			#push (@TABDATA, &ui_submit($text{'vmdel_title'}, "delete"));
			push (@TABDATA ,"&nbsp;<a href='delete_vm.cgi?vm=$DUMMY&user=$USER&mode=1')'><img src='images/trash.png' border='0'></a>&nbsp;");
			#push (@TABDATA, $USERS);
			
			print ui_columns_row(\@TABDATA,\@TD);
			
			print &ui_form_end();
			#}
		}
	
	print &ui_columns_end();
	print &ui_links_row(\@linksrow);
	
	print "<br>";
	print "<a href='#' onclick=\"javascript:window.open('list_vms.cgi?print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a>";
	print "<br>";
	
	
	$formno++;
	
	}


