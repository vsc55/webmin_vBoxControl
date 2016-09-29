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

my $VBOXBIN = $config{'PATH_VB_BIN'};
if (! ($VBBOXBIN =~ /\/$/))
	{
	$VBOXBIN .= "/";
	}

my $VM = $in{'vm'};
my $USER = $in{'user'};
my $MODE = $in{'mode'};

#Mode -> request for confirm
if ($MODE eq "1")
	{
	$HEADER = "$module_info{'desc'} (V $module_info{'version'})<br>";
	$HEADER .= "<font size='3'>VirtualBox ".GetVBVersion()."</font>";
	
	$HEADER = "";
	ui_print_header(undef, $HEADER, "", "", 1, 1);
	print &ui_form_start("delete_vm.cgi", "Post");
	print ui_hidden("user",$USER);
	print ui_hidden("vm",$VM);

	print "<center><font size='+1' color='red'><b>Do you really want to delete the VM '$VM'?</b></font><br><br>";
	print "If you choose <b><i>'".$text{'butt_vmdel_yes'}."'</i></b> all VM Entrys will be delete but not the HD-Files like *.VMDK/*.VDI.<br>";
	print "If you choose <b><i>'".$text{'butt_vmfulldel'}."'</i></b> all VM Entrys AND all HD-Files *.VMDK/*.VDI will be deleted too.<br><br>";
	print " ";
	
	
	print &ui_submit($text{'butt_vmdel_yes'}, "del")." ".&ui_submit($text{'butt_vmfulldel'}, "fulldel");
	
	print &ui_form_end();
	
	
	}
# confirm to delete
# First detach HD from Controller
# Second remove Controller from VM
# Third unregister VM from 
if ( ($in{'del'}) || ($in{'fulldel'}) )
	{
	if ($config{'multiuser'})
		{
		$CMD_MULTIUSER = "sudo -H -u $USER ";
		}
	else
		{
		$CMD_MULTIUSER = "";
		}
	
	#DebugOut();
	
	my %VMINFO = GetVMInfo($USER,$VM);
	
	$ERR = 0;
	
	my @HDLOCATION;
	my %HDDS = ListHDDS();
	
	foreach my $KEY (keys %HDDS)
		{
		#print "KEY: $KEY <br>";
		if ($KEY =~ /^$USER\:$VM/)
			{
			#print "Meins!!!<br>";
			my ($A,$B,$LOCATION);
			($A,$B,$LOCATION) = split (":" , $KEY);
			$LOCATION = quotemeta($LOCATION);
			#print "Location: '$LOCATION' <br>";
			push (@HDLOCATION , "$LOCATION");
			}
		}

	foreach $KEY (sort keys %VMINFO)
		{
		
		switch ($KEY)
			{
			case /IDE Controller/
				{
				
				$KEY =~ /\(.*\)/g;
				my ($PORT,$CTRL) = split("," , $&);
				$PORT =~ s/\(//;
				$CTRL =~ s/\)//;
				
				my $COMMAND = $CMD_MULTIUSER;
				$COMMAND .= $VBOXBIN."VBoxManage --nologo storageattach \"$VM\" --storagectl \"IDE Controller\" ";
				$COMMAND .= "--port $PORT --device $CTRL --medium none";
				my $RETURN = readpipe($COMMAND);
				if ($DEBUGMODE)
					{
					print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
					}
				my $DUMMY = IsError($RETURN,"Part: Detach IDE $PORT:$CTRL");
				$ERR = ($ERR || $DUMMY);
				
				}
			case /SATA Controller/
				{
				$KEY =~ /\(.*\)/g;
				my ($PORT,$CTRL) = split("," , $&);
				$PORT =~ s/\(//;
				$CTRL =~ s/\)//;
				
				my $COMMAND = $CMD_MULTIUSER;
				$COMMAND .= $VBOXBIN."VBoxManage --nologo storageattach \"$VM\" --storagectl \"SATA Controller\" ";
				$COMMAND .= "--port $PORT --device $CTRL --medium none";
				my $RETURN = readpipe($COMMAND);
				if ($DEBUGMODE)
					{
					print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
					}
				my $DUMMY = IsError($RETURN,"Part: Detach SATA $PORT:$CTRL");
				$ERR = ($ERR || $DUMMY);
				
				}
			case /SCSI Controller/
				{
				$KEY =~ /\(.*\)/g;
				my ($PORT,$CTRL) = split("," , $&);
				$PORT =~ s/\(//;
				$CTRL =~ s/\)//;
				
				my $COMMAND = $CMD_MULTIUSER;
				$COMMAND .= $VBOXBIN."VBoxManage --nologo storageattach \"$VM\" --storagectl \"SCSI Controller\" ";
				$COMMAND .= "--port $PORT --device $CTRL --medium none";
				my $RETURN = readpipe($COMMAND);
				if ($DEBUGMODE)
					{
					print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
					}
				my $DUMMY = IsError($RETURN,"Part: Detach SCSI $PORT:$CTRL");
				$ERR = ($ERR || $DUMMY);
				
				}
			case /Floppy Controller/
				{
				$KEY =~ /\(.*\)/g;
				my ($PORT,$CTRL) = split("," , $&);
				$PORT =~ s/\(//;
				$CTRL =~ s/\)//;
				
				my $COMMAND = $CMD_MULTIUSER;
				$COMMAND .= $VBOXBIN."VBoxManage --nologo storageattach \"$VM\" --storagectl \"Floppy Controller\" ";
				$COMMAND .= "--port $PORT --device $CTRL --medium none";
				my $RETURN = readpipe($COMMAND);
				if ($DEBUGMODE)
					{
					print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
					}
				my $DUMMY = IsError($RETURN,"Part: Detach Floppy $PORT:$CTRL");
				$ERR = ($ERR || $DUMMY);
				
				}
			}
		}
	
	
	foreach $KEY (sort keys %VMINFO)
		{
		if ($KEY =~ /Storage Controller Name/gi)
			{
			$VMINFO{$KEY} =~ s/^\s+//g;
			$VMINFO{$KEY} =~ s/\s+$//g;
			
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage --nologo storagectl \"$VM\" --name \"$VMINFO{$KEY}\" --remove";
			my $RETURN = readpipe($COMMAND);
			if ($DEBUGMODE)
				{
				print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
				}
			my $DUMMY = IsError($RETURN,"Part: Remove $VMINFO{$KEY}");
			$ERR = ($ERR || $DUMMY);
			
			}
		}
	my $COMMAND = $CMD_MULTIUSER;
	$COMMAND .= $VBOXBIN."VBoxManage --nologo unregistervm \"$VM\" --delete";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
		}
	
	if ($in{'fulldel'})
		{
		foreach my $LOCATION (sort @HDLOCATION)
			{
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage --nologo closemedium disk $LOCATION --delete 2>&1";
			my $RETURN = readpipe($COMMAND);
			if ($DEBUGMODE)
				{
				print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
				}
			}
		}
	
	
	
	webmin_log("Delete","VM","'$VM' ($USER)",\%in);
	
	my $DUMMY = IsError($return,"Part: Unregister VM $VM");
	$ERR = ($ERR || $DUMMY);
	}


if ( ($ERR) || ($MODE eq "1") )
	{
	print ui_print_footer("index.cgi?mode=vm", $text{'index_return'});
	}
else
	{
	redirect("index.cgi?mode=vm");
	}


sub IsError
	{
	my ($ERROR,$REMARK) = @_;
	if ($ERROR =~ /error\:.*\n/i)
		{
		ui_print_header(undef, "", "", undef, 1, 1);
		print "<b>$REMARK<br>'$&'</b><br>";
		return 1;
		}
	return 0;
	}




