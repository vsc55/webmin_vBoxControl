#!/usr/bin/perl

use File::Basename;
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

my $MULTIUSER;
if ($config{'multiuser'})
	{
	$MULTIUSER = 1;
	}
else
	{
	$MULTIUSER = 0;
	}

my %OSTYPES = GetOStypes();
my @OSTYPES;

my $ERR = 0;

if ($in{'new'})
	{
	
	my $USER = $in{'vmuser'};
	
	my ($PARAMETER, $REMARK);
	
	if ($in{'to'})
		{
		$PARAMETER = "--basefolder \"$in{'vmbasedir'}\" ";
		}
	
	my $COMMAND;
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $USER ";
		}
	$COMMAND .= $VBOXBIN."VBoxManage --nologo createvm -name \"$in{'vmname'}\" -register ";
	$COMMAND .= "$PARAMETER 2>&1";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "<b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br><br>";
		}
	my $DUMMY = IsError($RETURN,"PART: Creating machine...");
	$ERR = ($ERR || $DUMMY);
	
	my $PARAMETER = "--ostype $in{'ostype'} --memory $in{'vmram'} --acpi on --vram 128 ";
	
	my @BOOT = ("none","floppy","dvd","disk","net");
	if ($in{'boot1'})
		{
		$PARAMETER .= "--boot1 @BOOT[$in{'boot1'}] ";
		}
	if ($in{'boot2'})
		{
		$PARAMETER .= "--boot2 @BOOT[$in{'boot2'}] ";
		}
	if ($in{'boot3'})
		{
		$PARAMETER .= "--boot3 @BOOT[$in{'boot3'}] ";
		}
	if ($in{'boot4'})
		{
		$PARAMETER .= "--boot4 @BOOT[$in{'boot4'}] ";
		}
	
	if ($in{'vrde'})
		{
		my @AUTH = ("null","external","guest");
		$PARAMETER .= "--vrde on --vrdeport $in{'vrdeport'} --vrdeauthtype @AUTH[$in{'vrdeauth'}] ";
		$PARAMETER .= "--vrdemulticon on ";
		}
	
	my @NIC = ("none","null","nat","bridged","intnet","hostonly");
	if ($in{'nic1'})
		{
		my ($NIC,$IF) = split(":" , $in{'nic1'});
		if ($NIC eq "3")
			{
			$PARAMETER .= "--nic1 bridged --bridgeadapter1 $IF ";
			}
		else
			{
			$PARAMETER .= "--nic1 @NIC[$in{'nic1'}] ";
			}
		}
	if ($in{'nic2'})
		{
		my ($NIC,$IF) = split(":" , $in{'nic2'});
		if ($NIC eq "3")
			{
			$PARAMETER .= "--nic2 bridged --bridgeadapter2 $IF ";
			}
		else
			{
			$PARAMETER .= "--nic2 @NIC[$in{'nic2'}] ";
			}
		}
	if ($in{'nic3'})
		{
		my ($NIC,$IF) = split(":" , $in{'nic3'});
		if ($NIC eq "3")
			{
			$PARAMETER .= "--nic3 bridged --bridgeadapter3 $IF ";
			}
		else
			{
			$PARAMETER .= "--nic3 @NIC[$in{'nic3'}] ";
			}
		}
	if ($in{'nic4'})
		{
		my ($NIC,$IF) = split(":" , $in{'nic4'});
		if ($NIC eq "3")
			{
			$PARAMETER .= "--nic4 bridged --bridgeadapter4 $IF ";
			}
		else
			{
			$PARAMETER .= "--nic4 @NIC[$in{'nic4'}] ";
			}
		}
	
	my @NICTYPE = ("none","Am79C970A","Am79C973","82540EM","82543GC","82545EM","virtio");
	if ($in{'nichw1'})
		{
		$PARAMETER .= "--nictype1 @NICTYPE[$in{'nichw1'}] ";
		}
	if ($in{'nichw2'})
		{
		$PARAMETER .= "--nictype2 @NICTYPE[$in{'nichw2'}] ";
		}
	if ($in{'nichw3'})
		{
		$PARAMETER .= "--nictype3 @NICTYPE[$in{'nichw3'}] ";
		}
	if ($in{'nichw4'})
		{
		$PARAMETER .= "--nictype4 @NICTYPE[$in{'nichw4'}] ";
		}
	
	if ($in{'mac1'})
		{
		$in{'mac1'} =~ s/\://g;
		$in{'mac1'} =~ s/\-//g;
		$PARAMETER .= "--macaddress1 $in{'mac1'} ";
		}
	if ($in{'mac2'})
		{
		$in{'mac2'} =~ s/\://g;
		$in{'mac2'} =~ s/\-//g;
		$PARAMETER .= "--macaddress2 $in{'mac2'} ";
		}
	if ($in{'mac3'})
		{
		$in{'mac3'} =~ s/\://g;
		$in{'mac3'} =~ s/\-//g;
		$PARAMETER .= "--macaddress3 $in{'mac3'} ";
		}
	if ($in{'mac4'})
		{
		$in{'mac4'} =~ s/\://g;
		$in{'mac4'} =~ s/\-//g;
		$PARAMETER .= "--macaddress4 $in{'mac4'} ";
		}
	
	my $COMMAND;
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $USER ";
		}
	$COMMAND .= $VBOXBIN."VBoxManage --nologo modifyvm \"$in{'vmname'}\" $PARAMETER  2>&1";
	my $RETURN = readpipe($COMMAND);
	
	$REMARK = "$COMMAND\n";
	
	if ($DEBUGMODE)
		{
		print "<b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br><br>";
		}
	my $DUMMY = IsError($RETURN,"PART: Setting specs...");
	$ERR = ($ERR || $DUMMY);
	
	my %INFO = GetVMInfo($USER,$in{'vmname'});
	#print "==> ".$INFO{'Config file'}."<br>";
	my $DIR = dirname($INFO{'Config file'})."/";
	$DIR =~ s/^\s+//;
	$DIR =~ s/\s+$//;
	
	
	if ($in{'IDE'})
		{
		my @IDETYPE = ("none","PIIX3","PIIX4","ICH6");
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo storagectl \"$in{'vmname'}\" ";
		$COMMAND .= "--name \"IDE Controller\" --add ide --controller @IDETYPE[$in{'IDE'}]  2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<hr><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Create IDE Controller...");
		$ERR = ($ERR || $DUMMY);
		
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo createhd --filename \"$DIR$in{'vmname'}_IDE\" --size $in{'idesize'} ";
		$COMMAND .= "--format $in{'ide_hdformat'} --variant $in{'ide_hdvariant'} 2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Creating IDE HD...");
		$ERR = ($ERR || $DUMMY);
		
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo storageattach \"$in{'vmname'}\" --storagectl \"IDE Controller\" --port 0 --device 0 ";
		$COMMAND .= "--type hdd --medium \"$DIR$in{'vmname'}_IDE.$in{'ide_hdformat'}\"  2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br><br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Registering IDE HD...");
		$ERR = ($ERR || $DUMMY);
		
		}
	
	if ($in{'SATA'})
		{
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo storagectl \"$in{'vmname'}\" ";
		$COMMAND .= "--name \"SATA Controller\" --add sata --controller IntelAhci  2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<hr><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Create SATA Controller...");
		$ERR = ($ERR || $DUMMY);
		
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo createhd --filename \"$DIR$in{'vmname'}_SATA\" --size $in{'satasize'} ";
		$COMMAND .= "--format $in{'sata_hdformat'} --variant $in{'sata_hdvariant'} 2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Creating SATA HD...");
		$ERR = ($ERR || $DUMMY);
		
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo storageattach \"$in{'vmname'}\" --storagectl \"SATA Controller\" --port 0 --device 0 ";
		$COMMAND .= "--type hdd --medium \"$DIR$in{'vmname'}_SATA.$in{'sata_hdformat'}\"  2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br><br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Registering SATA HD...");
		$ERR = ($ERR || $DUMMY);
		
		}
	
	if ($in{'SCSI'})
		{
		my @SCSITYPE = ("none","LsiLogic","BusLogic");
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo storagectl \"$in{'vmname'}\" ";
		$COMMAND .= "--name \"SCSI Controller\" --add scsi --controller @SCSITYPE[$in{'SCSI'}]  2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<hr><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Create SCSI Controller...");
		$ERR = ($ERR || $DUMMY);
		
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo createhd --filename \"$DIR$in{'vmname'}_SCSI\" --size $in{'scsisize'} ";
		$COMMAND .= "--format $in{'scsi_hdformat'} --variant $in{'scsi_hdvariant'} 2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Creating SCSI HD...");
		$ERR = ($ERR || $DUMMY);
		
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo storageattach \"$in{'vmname'}\" --storagectl \"SCSI Controller\" --port 0 --device 0 ";
		$COMMAND .= "--type hdd --medium \"$DIR$in{'vmname'}_SCSI.$in{'scsi_hdformat'}\"  2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br><br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Registering SCSI HD...");
		$ERR = ($ERR || $DUMMY);
		
		}
	
	if ($in{'SAS'})
		{
		my @SASTYPE = ("none","LSILogicSAS");
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo storagectl \"$in{'vmname'}\" ";
		$COMMAND .= "--name \"SAS Controller\" --add sas --controller @SASTYPE[$in{'SAS'}]  2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<hr><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Create SAS Controller...");
		$ERR = ($ERR || $DUMMY);
		
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo createhd --filename \"$DIR$in{'vmname'}_SAS\" --size $in{'sassize'} ";
		$COMMAND .= "--format $in{'sas_hdformat'} --variant $in{'sas_hdvariant'} 2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Creating SAS HD...");
		$ERR = ($ERR || $DUMMY);
		
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo storageattach \"$in{'vmname'}\" --storagectl \"SAS Controller\" --port 0 --device 0 ";
		$COMMAND .= "--type hdd --medium \"$DIR$in{'vmname'}_SAS.$in{'sas_hdformat'}\"  2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br><br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Registering SCSI HD...");
		$ERR = ($ERR || $DUMMY);
		
		}
	
	if ($in{'FD'})
		{
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo storagectl \"$in{'vmname'}\" ";
		$COMMAND .= "--name \"Floppy Controller\" --add floppy --controller I82078  2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Create FD Controller...");
		$ERR = ($ERR || $DUMMY);
		
		#Unknown, how to attach the local FDD to the VM or to create an FDD image and attach them.
		# Who can help ?
		
		
		}
	
	if ($in{'ISO'})
		{
		$ISO = $in{'ISO'};
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage --nologo storageattach \"$in{'vmname'}\" --storagectl \"IDE Controller\" ";
		$COMMAND .= "--port 1 --device 0 --type dvddrive --medium \"$in{'ISO'}\"  2>&1";
		my $RETURN = readpipe($COMMAND);
		$REMARK .= "$COMMAND |";
		if ($DEBUGMODE)
			{
			print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"PART: Boote vom ISO ...");
		$ERR = ($ERR || $DUMMY);
		}
	my $HASH = \%in;
	$HASH->{'SYNTAX'} = $REMARK;
	webmin_log("Create","VM","'$in{'vmname'}' ($USER)",\%in);
	
	if (! $ERR)
		{
		redirect("index.cgi?mode=vm");
		}
	
	}


ui_print_header(undef, $text{'VM_NEW'}, "", undef, 1, 1);

foreach my $DUMMY (sort keys %OSTYPES)
	{
	push (@OSTYPES , ["$DUMMY", "$OSTYPES{$DUMMY}"]);
	}

print &ui_form_start("new_vm.cgi", "Post");

my @VMUSER;
if ($MULTIUSER)
	{
	@VMUSER = GetVBoxUser();
	}
else
	{
	push (@VMUSER , "root");
	}

my (@TD) = ("width='25%'"," "," ");
my (@TABHEAD) = ("User"," "," ");
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
my @TABDATA = (
		$text{'INP_USERNAME'},
		" ",
		ui_select("vmuser",$in{'vmuser'},\@VMUSER)
		);
print ui_columns_row(\@TABDATA,\@TD);
my @RADIO = ([0,"Default"],[1,$text{'VM_BASEDIR'}]);
my @TABDATA = (
		$text{'INP_VMPATH'},
		" ",
		&ui_radio("to", 0,\@RADIO)." ".&ui_filebox("vmbasedir", "/", 40,0,50,"vmbasedir",1)
		);
print ui_columns_row(\@TABDATA,\@TD);

print &ui_columns_end();


my (@TD) = ("width='25%'"," "," ");
my (@TABHEAD) = ("System"," "," ");
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
my @TABDATA = ($text{'INP_VMNAME'}," ",ui_textbox("vmname",($in{'vmname'}?$in{'vmname'}:"MyVM"),10));
print ui_columns_row(\@TABDATA,\@TD);
my @TABDATA = ($text{'INP_OSTYPE'}," ",&ui_select("ostype",$in{'ostype'},\@OSTYPES));
print ui_columns_row(\@TABDATA,\@TD);
my @TABDATA = ($text{'INP_RAM'}," ",ui_textbox("vmram",($in{'vmram'}?$in{'vmram'}:"512"),10)." <b>MB</b>");
print ui_columns_row(\@TABDATA,\@TD);
my @BOOT = ([0,"<b>None</b>"],[1,"<b>Floppy</b>"],[2,"<b>DVD</b>"],[3,"<b>Disk</b>"],[4,"<b>Network</b>"]);
my @TABDATA = ($text{'INP_BOOT'}," ","<b>#1</b> ".ui_select("boot1",($in{'boot1'}?$in{'boot1'}:2),\@BOOT)."<b>#2</b> ".ui_select("boot2",1,\@BOOT)."<b>#3</b> ".ui_select("boot3",3,\@BOOT)."<b>#4</b> ".ui_select("boot4",0,\@BOOT));
print ui_columns_row(\@TABDATA,\@TD);
print &ui_columns_end();

my (@TD) = ("width='25%'"," "," ");
my (@TABHEAD) = ("RemoteDesktop"," "," ");
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
my @TABDATA = ($text{'INP_VRDE'}," ",ui_select("vrde",($in{'vrde'}?$in{'vrde'}:0),[[0,"No"],[1,"Yes"]])." <b>".$text{'INP_VRDEPORT'}."</b> ".ui_textbox("vrdeport",($in{'vrdeport'}?$in{'vrdeport'}:"3389"),5)." <b>".$text{'INP_VRDEAUTH'}."</b> ".ui_select("vrdeauth",($in{'vrdeauth'}?$in{'vrdeauth'}:"0"),[[0,"Null"],[1,"External"],[2,"Guest"]]));
print ui_columns_row(\@TABDATA,\@TD);
print &ui_columns_end();

my (@TD) = ("width='5%'","width='20%'"," ");
my (@TABHEAD) = ("Network"," "," ");
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);

my @BRIDGEIF = GetBridgedIfs();
my @NIC = ([0,"---"],[1,"Not attached"],[2,"Nat"]);
foreach my $DUMMY (@BRIDGEIF)
	{
	my $IF = $DUMMY->{'Name'};
	push (@NIC , ["3:$IF","Bridged $IF"]);
	}
push (@NIC , [4,"Internal"]);
push (@NIC , [5,"Host Only"]);


my @NICTYPE = ([0,"---"],[1,"PCnet-PCI II (AM79C970A)"],[2,"PCnet-PCI III (AM79C973)"],[3,"Intel PRO/1000 MT Desktop (82540EM)"],[4,"Intel PRO/1000 T Server (82543GC)"],[5,"Intel PRO/1000 MT Server (82545EM)"],[6,"Virtio-net"]);
my @TABDATA = (
		"<img src='images/nic.gif'>",
		"$text{'INP_NIC'} #1",
		"<b>$text{'NIC_HWTYPE'}</b> ".ui_select("nichw1",$in{'nichw1'},\@NICTYPE)."<b>$text{'NIC_CONNECT'}</b> ".ui_select("nic1",$in{'nic1'},\@NIC)."<b>$text{'NIC_MAC'}</b> ".ui_textbox("mac1",$in{'mac1'},17));
print ui_columns_row(\@TABDATA,\@TD);
my @TABDATA = ("<img src='images/nic.gif'>","$text{'INP_NIC'} #2","<b>$text{'NIC_HWTYPE'}</b> ".ui_select("nichw2",$in{'nichw2'},\@NICTYPE)."<b>$text{'NIC_CONNECT'}</b> ".ui_select("nic2",$in{'nic2'},\@NIC)."<b>$text{'NIC_MAC'}</b> ".ui_textbox("mac2",$in{'mac2'},17));
print ui_columns_row(\@TABDATA,\@TD);
my @TABDATA = ("<img src='images/nic.gif'>","$text{'INP_NIC'} #3","<b>$text{'NIC_HWTYPE'}</b> ".ui_select("nichw3",$in{'nichw3'},\@NICTYPE)."<b>$text{'NIC_CONNECT'}</b> ".ui_select("nic3",$in{'nic3'},\@NIC)."<b>$text{'NIC_MAC'}</b> ".ui_textbox("mac3",$in{'mac3'},17));
print ui_columns_row(\@TABDATA,\@TD);
my @TABDATA = ("<img src='images/nic.gif'>","$text{'INP_NIC'} #4","<b>$text{'NIC_HWTYPE'}</b> ".ui_select("nichw4",$in{'nichw4'},\@NICTYPE)."<b>$text{'NIC_CONNECT'}</b> ".ui_select("nic4",$in{'nic4'},\@NIC)."<b>$text{'NIC_MAC'}</b> ".ui_textbox("mac4",$in{'mac4'},17));
print ui_columns_row(\@TABDATA,\@TD);
print &ui_columns_end();

my (@TABHEAD) = ("Controller"," "," "," ");
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);

my @HDFORMAT = (["vdi","VDI"],["vmdk","VMDK"],["vhd","VHD"]);
my @HDVARIANT = (["Standard","Dynamic"],["Fixed","Fixed"]);
my @HDCREATE = ([0,"No"],[1,"Yes"]);
my @IDECTRL = ([0,"None"],[1,"PIIX3"],[2,"PIIX4"],[3,"ICH6"]);
my @TABDATA = (
		"<img src='images/controller.gif'>",
		$text{'INP_IDECTL'},
		ui_select("IDE",$in{'IDE'},\@IDECTRL),
		"<b>$text{'INP_CREATEHD'}</b> ".ui_select("createide",$in{'createide'},\@HDCREATE).
		" <b>$text{'INP_HDEXTENSION'}</b> ".ui_select("ide_hdformat",$in{'ide_hdformat'},\@HDFORMAT).
		" <b>$text{'INP_HDVARIANT'}</b> ".ui_select("ide_hdvariant",$in{'ide_hdvariant'},\@HDVARIANT).
		" <b>".$text{'INP_HDSIZE'}."</b> ".ui_textbox("idesize",($in{'idesize'}?$in{'idesize'}:"500"),10)." <b>MB</b>"
		);
print ui_columns_row(\@TABDATA,\@TD);
my @SATACTRL = ([0,"None"],[1,"AHCI"]);
my @TABDATA = (
		"<img src='images/controller.gif'>",
		$text{'INP_SATACTL'},
		ui_select("SATA",$in{'SATA'},\@SATACTRL),
		"<b>$text{'INP_CREATEHD'}</b> ".ui_select("createsata",$in{'createsata'},\@HDCREATE).
		" <b>$text{'INP_HDEXTENSION'}</b> ".ui_select("sata_hdformat",$in{'sata_hdformat'},\@HDFORMAT).
		" <b>$text{'INP_HDVARIANT'}</b> ".ui_select("sata_hdvariant",$in{'sata_hdvariant'},\@HDVARIANT).
		" <b>".$text{'INP_HDSIZE'}."</b> ".ui_textbox("satasize",($in{'satasize'}?$in{'satasize'}:"500"),10)." <b>MB</b>"
		);
print ui_columns_row(\@TABDATA,\@TD);
my @SCSICTRL = ([0,"None"],[1,"Lsilogic"],[2,"BusLogic"]);
my @TABDATA = (
		"<img src='images/controller.gif'>",
		$text{'INP_SCSICTL'},
		ui_select("SCSI",$in{'SCSI'},\@SCSICTRL),
		"<b>$text{'INP_CREATEHD'}</b> ".ui_select("createscsi",$in{'createscsi'},\@HDCREATE).
		" <b>$text{'INP_HDEXTENSION'}</b> ".ui_select("scsi_hdformat",$in{'scsi_hdformat'},\@HDFORMAT).
		" <b>$text{'INP_HDVARIANT'}</b> ".ui_select("scsi_hdvariant",$in{'scsi_hdvariant'},\@HDVARIANT).
		" <b>".$text{'INP_HDSIZE'}."</b> ".ui_textbox("scsisize",($in{'scsisize'}?$in{'scsisize'}:"500"),10)." <b>MB</b>"
		);
print ui_columns_row(\@TABDATA,\@TD);
my @SASCTRL = ([0,"None"],[1,"Lsilogic SAS"]);
my @TABDATA = (
		"<img src='images/controller.gif'>",
		$text{'INP_SASCTL'},
		ui_select("SAS",$in{'SAS'},\@SASCTRL),
		"<b>$text{'INP_CREATEHD'}</b> ".ui_select("createsas",$in{'createsas'},\@HDCREATE).
		" <b>$text{'INP_HDEXTENSION'}</b> ".ui_select("sas_hdformat",$in{'sas_hdformat'},\@HDFORMAT).
		" <b>$text{'INP_HDVARIANT'}</b> ".ui_select("sas_hdvariant",$in{'sas_hdvariant'},\@HDVARIANT).
		" <b>".$text{'INP_HDSIZE'}."</b> ".ui_textbox("sassize",($in{'sassize'}?$in{'sassize'}:"500"),10)." <b>MB</b>"
		);
print ui_columns_row(\@TABDATA,\@TD);
my @FDCTRL = ([0,"<b>None</b>"],[1,"<b>I82078</b>"]);
my @TABDATA = (
		"<img src='images/controller.gif'>",
		$text{'INP_FDCTL'},
		ui_select("FD",$in{'FD'},\@FDCTRL),
		" "
		);
print ui_columns_row(\@TABDATA,\@TD);
print &ui_columns_end();

my (@TABHEAD) = ("Setup"," "," ");
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
my @TABDATA = ("<img src='images/iso.gif'>",$text{'INP_ISO'},&ui_textbox("ISO", $in{'ISO'}, 40)." ".&file_chooser_button("ISO", 0));
print ui_columns_row(\@TABDATA,\@TD);
print &ui_columns_end();


print &ui_submit($text{'vmnew_title'}, "new");

print &ui_form_end();


# Ruecksprung zur anfordernden Seite
if ($in{'mode'})
	{
	print ui_print_footer("index.cgi?mode=hdds", $text{'index_return'});
	}
else
	{
	print ui_print_footer("index.cgi?mode=vm", $text{'index_return'});
	}


sub IsError
	{
	my ($ERROR,$REMARK) = @_;
	if ($ERROR =~ /error\:.*\n/i)
		{
		ui_print_header(undef, "", "", undef, 1, 1);
		print "<font color='red'><b>$REMARK<br>'$&'</b></font><br>";
		return 1;
		}
	return 0;
	}



