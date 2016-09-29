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

$VM = $in{'vm'};
$USER = $in{'user'};

my $VBVERSION = GetVBVersion();

my $CMD_MULTIUSER;

if ($config{'multiuser'})
	{
	$CMD_MULTIUSER = "sudo -H -u $USER ";
	}
else
	{
	$CMD_MULTIUSER = "";
	}


# activate this headercode only for debuging
ui_print_header(undef, $text{'PORTFORWARD_VM'}." '$VM'<br><font size='-1'>(Account $USER)</font>", "", undef, 1, 1);

my $VMRUNNING = IsVMRunning($USER,$VM);

# "<Service>:<NIC>"
if (exists $in{'natpf'})
	{
	# print html header with ani gif
	PrintWait();
	
	my @NATPF = split(/\0/, $in{'natpf'});
	
	foreach my $DUMMY (@NATPF)
		{
		#print "<hr>";
		#print "\$DUMMY --> '$DUMMY'<br>";
		
		my ($OLDSERVICE,$OLDNIC) = split(":" , $in{"NAT_OLDNIC_$DUMMY"});
		my $NEWNIC = $in{"NAT_NEWNIC_$DUMMY"};
		my ($NEWSERVICE) = $in{"NAT_TAG_$DUMMY"};
		my $PROTOCOL = $in{"NAT_PROT_$DUMMY"};
		my $HOSTIP = $in{"NAT_HIP_$DUMMY"};
		my $HOSTPORT = $in{"NAT_HPORT_$DUMMY"};
		my $GUESTIP = $in{"NAT_GIP_$DUMMY"};
		my $GUESTPORT = $in{"NAT_GPORT_$DUMMY"};
		
		my (%NATPF) = GetNATPF($USER,$VM);
		my $OLDHOSTIP = $NATPF{"$NEWNIC\_$NEWSERVICE"}{'host ip'};
		my $OLDHOSTPORT = $NATPF{"$NEWNIC\_$NEWSERVICE"}{'host port'};
		my $OLDGUESTIP = $NATPF{"$NEWNIC\_$NEWSERVICE"}{'guest ip'};
		my $OLDGUESTPORT = $NATPF{"$NEWNIC\_$NEWSERVICE"}{'guest port'};
		
		if ($in{'delete'})
			{
			# delete rule
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage -q controlvm \"$VM\" ";
			$COMMAND .= "natpf$OLDNIC delete \"$OLDSERVICE\" 2>&1";
			my $RETURN = readpipe($COMMAND);
			if ($DEBUGMODE)
				{
				print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
				}
			if ($RETURN)
				{
				print "$RETURN<br>";
				}
			my $HASH = \%in;
			$HASH->{'COMMAND'} = $COMMAND;
			$HASH->{'RETURN'} = $RETURN;
			webmin_log("Delete NATRule","'$OLDSERVICE'","'$VM' ($USER)",\%in);
			}
		elsif ($in{'update'})
			{
			if ($HOSTIP)
				{
				if ( CheckIP($HOSTIP) )
					{
					$ERROR .= "ERROR: ".text('HOSTIP_ERR',$HOSTIP)."<br>";
					}
				}
				
			if ($GUESTIP)
				{
				if ( CheckIP($GUESTIP) )
					{
					$ERROR .= "ERROR: ".text('GUESTIP_ERR',$HOSTIP)."<br>";
					}
				}
			
			if ( ($OLDNIC ne $NEWNIC) || ($OLDSERVICE ne $NEWSERVICE) )
				{
				# check if the new valua exists by the protocol key
				if (exists $NATPF{"$NEWNIC\_$NEWSERVICE"}{'protocol'})
					{
					$ERROR .= text('VMEXTRA_RENAMEERROR',$NEWSERVICE,$NEWNIC,"natpf")."<br>";
					}
				}
			
			if (! $ERROR)
				{
				# its not posssible to edit rules, there fore delete first
				# and add at second step
				
				# 1) delete rule
				my $COMMAND = $CMD_MULTIUSER;
				$COMMAND .= $VBOXBIN."VBoxManage -q controlvm \"$VM\" ";
				$COMMAND .= "natpf$OLDNIC delete \"$OLDSERVICE\" 2>&1";
				my $RETURN = readpipe($COMMAND);
				if ($DEBUGMODE)
					{
					print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
					}
				
				if ($RETURN)
					{
					print "$RETURN<br>";
					}
				
				# 2) add the same rule with new values
				if ($OLDSERVICE ne $NEWSERVICE)
					{
					#print "$OLDSERVICE --> $NEWSERVICE<br>";
					$SERVICE = $NEWSERVICE;
					}
				#print "Edit $OLDSERVICE<br>";
				my $COMMAND = $CMD_MULTIUSER;
				$COMMAND .= $VBOXBIN."VBoxManage -q controlvm \"$VM\" natpf$NEWNIC ";
				$COMMAND .= "\"$NEWSERVICE\",$PROTOCOL,$HOSTIP,";
				$COMMAND .= "$HOSTPORT,$GUESTIP,$GUESTPORT 2>&1";
				my $RETURN = readpipe($COMMAND);
				if ($DEBUGMODE)
					{
					print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
					}
				if ($RETURN)
					{
					print "$RETURN<br>";
					}
				
				webmin_log("Update NATRule","'$NEWSERVICE'","'$VM' ($USER)",\%in);
				}
			else
				{
				print "<font color='red'><b>$ERROR</b></font> <p>\n";
				}
			}
		}
	# if natpf only, then print html redirect
	if (!(exists $in{'vmextra'}))
		{
		GoBack();
		}
	}

my $EXTRAPATH = "VBoxInternal/Devices";

# Updating a forwarding extradata rule
if (exists $in{'vmextra'})
	{
	# if vmextra only, then print html-header with ani gif
	if (!(exists $in{'natpf'}))
		{
		PrintWait();
		}
	my @EXTRA = split(/\0/, $in{'vmextra'});
	
	foreach my $DUMMY (@EXTRA)
		{
		#print "\$DUMMY --> '$DUMMY'<br>";
		#print "UPDATE Extradata<br>";
		
		my ($A,$B,$OLDNIC) = split(":" , $DUMMY);
		my ($OLDSERVICE,$OLDNICTYPE) = split(":" , $in{"EXT_$DUMMY"});
		my $NEWSERVICE= $in{"EXT_TAG_$DUMMY"};
		my ($NEWNICTYPE,$NEWNIC) = split(":" , $in{"EXT_NIC_$DUMMY"});
		my $GUESTPORT = $in{"EXT_GPORT_$DUMMY"};
		my $HOSTPORT = $in{"EXT_HPORT_$DUMMY"};
		my $PROTOCOL = $in{"EXT_PROT_$DUMMY"};
		
		# VBoxInternal/Devices 
		
		my $OLDREGISTRY = "$EXTRAPATH/$OLDNICTYPE/$OLDNIC/LUN#0/Config/$OLDSERVICE";
		my $NEWREGISTRY = "$EXTRAPATH/$NEWNICTYPE/$NEWNIC/LUN#0/Config/$NEWSERVICE";
		
		# Delete Extradata Rule
		if (exists $in{'delete'})
			{
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$OLDREGISTRY/Protocol\" 2>&1 ";
			my $RETURN = readpipe($COMMAND);
			if ($DEBUGMODE)
				{
				print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
				}
			if ($RETURN)
				{
				print "$RETURN<br>";
				}
			
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$OLDREGISTRY/GuestPort\" 2>&1";
			my $RETURN = readpipe($COMMAND);
			if ($DEBUGMODE)
				{
				print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
				}
			if ($RETURN)
				{
				print "$RETURN<br>";
				}
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$OLDREGISTRY/HostPort\" 2>&1";
			my $RETURN = readpipe($COMMAND);
			if ($DEBUGMODE)
				{
				print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
				}
			if ($RETURN)
				{
				print "$RETURN<br>";
				}
			webmin_log("Delete EXTRADATARule","'$OLDSERVICE'","'$VM' ($USER)",\%in);
			}
		
		# Update Extradata Rule
		elsif (exists $in{'update'})
			{
			my %EXTRA = GetVMExtradata($VM);
			#Change SERVICE or NIC value
			if ($OLDREGISTRY ne $NEWREGISTRY)
				{
				#check data via 'protocol'-entry
				if (exists $EXTRA{"$NEWREGISTRY/Protocol"})
					{
					if ($OLDSERVICE eq $NEWSERVICE)
						{
						$ERROR .= "<b>".text('VMEXTRA_RENAMEERROR',$NEWSERVICE,($NEWNIC+1),"extradata")."</b><br>";
						}
					elsif ($OLDNIC eq $NEWNIC)
						{
						$ERROR .= "<b>".text('VMEXTRA_RENAMEERROR',$NEWSERVICE,($OLDNIC+1),"extradata")."</b><br>";
						}
					}
				
				if (! $ERROR)
					{
					#print "Umbenennen...<br>";
					# First delete the old entrys
					my $COMMAND = $CMD_MULTIUSER;
					$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$OLDREGISTRY/Protocol\" 2>&1";
					my $RETURN = readpipe($COMMAND);
					if ($DEBUGMODE)
						{
						print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
						}
					if ($RETURN)
						{
						print "$RETURN<br>";
						}
					my $COMMAND = $CMD_MULTIUSER;
					$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$OLDREGISTRY/GuestPort\" 2>&1";
					my $RETURN = readpipe($COMMAND);
					if ($DEBUGMODE)
						{
						print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
						}
					if ($RETURN)
						{
						print "$RETURN<br>";
						}
					my $COMMAND = $CMD_MULTIUSER;
					$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$OLDREGISTRY/HostPort\" 2>&1";
					my $RETURN = readpipe($COMMAND);
					if ($DEBUGMODE)
						{
						print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
						}
					if ($RETURN)
						{
						print "$RETURN<br>";
						}
					
					# than create the new entrys
					my $COMMAND = $CMD_MULTIUSER;
					$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$NEWREGISTRY/Protocol\" $PROTOCOL 2>&1";
					my $RETURN = readpipe($COMMAND);
					if ($DEBUGMODE)
						{
						print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
						}
					if ($RETURN)
						{
						print "$RETURN<br>";
						}
					my $COMMAND = $CMD_MULTIUSER;
					$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$NEWREGISTRY/GuestPort\" $GUESTPORT 2>&1";
					my $RETURN = readpipe($COMMAND);
					if ($DEBUGMODE)
						{
						print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
						}
					if ($RETURN)
						{
						print "$RETURN<br>";
						}
					my $COMMAND = $CMD_MULTIUSER;
					$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$NEWREGISTRY/HostPort\" $HOSTPORT 2>&1";
					my $RETURN = readpipe($COMMAND);
					if ($DEBUGMODE)
						{
						print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
						}
					if ($RETURN)
						{
						print "$RETURN<br>";
						}
					webmin_log("Rename EXTRADATARule","'$OLDSERVICE' -> '$NEWSERVICE'","'$VM' ($USER)",\%in);
					}
				else
					{
					print "<font color='red'><b>$ERROR</b></font> <p>\n";
					}
				}
			#Only change values for ports and protocol
			else
				{
				if ( ($EXTRA{"$NEWREGISTRY/Protocol"} eq $PROTOCOL) &&
					($EXTRA{"$NEWREGISTRY/GuestPort"} eq $GUESTPORT) &&
						($EXTRA{"$NEWREGISTRY/HostPort"} eq $HOSTPORT) )
					{
					print "<font color='red'><b>".text('VMEXTRA_EXISTERROR',$NEWSERVICE,$NEWNIC)."</b></font> <p>";
					}
				else
					{
					my $COMMAND = $CMD_MULTIUSER;
					$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$OLDREGISTRY/Protocol\" $PROTOCOL 2>&1";
					my $RETURN = readpipe($COMMAND);
					if ($DEBUGMODE)
						{
						print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
						}
					if ($RETURN)
						{
						print "$RETURN<br>";
						}
					my $COMMAND = $CMD_MULTIUSER;
					$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$OLDREGISTRY/GuestPort\" $GUESTPORT 2>&1";
					my $RETURN = readpipe($COMMAND);
					if ($DEBUGMODE)
						{
						print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
						}
					if ($RETURN)
						{
						print "$RETURN<br>";
						}
					my $COMMAND = $CMD_MULTIUSER;
					$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$OLDREGISTRY/HostPort\" $HOSTPORT 2>&1";
					my $RETURN = readpipe($COMMAND);
					if ($DEBUGMODE)
						{
						print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
						}
					if ($RETURN)
						{
						print "$RETURN<br>";
						}
					webmin_log("Update EXTRADATARule","'$OLDSERVICE'","'$VM' ($USER)",\%in);
					}
				}
			}
		}
	# print html redirect
	GoBack();
	}

# Add a new forwarding rule
elsif (exists $in{'add'})
	{
	
	if (!($in{'SERVICE'}))
		{
		$ERROR = "ERROR: $text{'VMEXTRA_ERRNOSERVICE'}<br>";
		}
	if (!($in{'HOSTPORT'}))
		{
		$ERROR .= "ERROR: $text{'VMEXTRA_ERRNOHOSTPORT'}<br>";
		}
	if (!($in{'GUESTPORT'}))
		{
		$ERROR .= "ERROR: $text{'VMEXTRA_ERRNOGUESTPORT'}<br>";
		}
	
	if ($in{'SRC'} eq "natpf")
		{
		if ($in{'HOSTIP'})
			{
			if ( CheckIP($in{'HOSTIP'}) )
				{
				$ERROR .= "ERROR: ".text('HOSTIP_ERR',$in{'HOSTIP'})."<br>";
				}
			}
		
		if ($in{'GUESTIP'})
			{
			
			if ( CheckIP($in{'GUESTIP'}) )
				{
				$ERROR .= "ERROR: ".text('GUESTIP_ERR',$in{'GUESTIP'})."<br>";
				}
			}
		}
	
	if ($ERROR)
		{
		print "<font color='red'><b>$ERROR</b></font> <p>\n";
		}
	else
		{
		
		if ($in{'SRC'} eq "natpf")
			{
			my ($NICTYPE,$NIC) = split(":" , $in{'NIC'});
			$NIC++;
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage -q controlvm \"$VM\" natpf$NIC ";
			$COMMAND .= "\"$in{'SERVICE'}\",$in{'PROTOCOL'},$in{'HOSTIP'},$in{'HOSTPORT'},";
			$COMMAND .= "$in{'GUESTIP'},$in{'GUESTPORT'} 2>&1";
			my $RETURN = readpipe($COMMAND);
			if ($DEBUGMODE)
				{
				print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
				}
			webmin_log("Add NATRule","'$in{'SERVICE'}'","'$VM' ($USER)",\%in);
			}
		else
			{
			
			my ($NICTYPE,$COUNT) = split(":" , $in{'NIC'});
			
			my $REGISTRY = "$EXTRAPATH/$NICTYPE/$COUNT/LUN#0/Config/$in{'SERVICE'}";
			
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$REGISTRY/Protocol\" $in{'PROTOCOL'} 2>&1";
			my $RETURN = readpipe($COMMAND);
			if ($DEBUGMODE)
				{
				print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
				}
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$REGISTRY/GuestPort\" $in{'GUESTPORT'} 2>&1";
			my $RETURN = readpipe($COMMAND);
			if ($DEBUGMODE)
				{
				print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
				}
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" \"$REGISTRY/HostPort\" $in{'HOSTPORT'} 2>&1";
			my $RETURN = readpipe($COMMAND);
			if ($DEBUGMODE)
				{
				print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
				}
			
			webmin_log("Add EXTRADATARule","'$in{'SERVICE'}'","'$VM' ($USER)",\%in);
			}
		
		# Clear Inputvalues
		#delete $in{'SRC'};
		#delete $in{'NIC'};
		#delete $in{'SERVICE'};
		#delete $in{'PROTOCOL'};
		#delete $in{'HOSTIP'};
		#delete $in{'HOSTPORT'};
		#delete $in{'GUESTIP'};
		#delete $in{'GUESTPORT'};
		
		}
	}

ui_print_header(undef, $text{'PORTFORWARD_VM'}." '$VM'", "", undef, 1, 1);

my (%NATPF, %INFO, %EXTRA, %DATAEXTRA, %DATANAT);
my (@NICEXTRA,@NICNATPF,@NICDATA,@TABHEAD,@TD, @linksrow);

%NATPF = GetNATPF($USER,$VM);
%INFO = GetVMInfo($USER,$VM);
%EXTRA = GetVMExtradata($USER,$VM);

my $COUNT = 0;

# Find out wich NICs are installed
foreach my $DUMMY (sort keys %INFO)
	{
	if ($DUMMY =~ /NIC.[0-9]$/i)
		{
		#print "NIC '$DUMMY' -> '$INFO{$DUMMY}'<br>";
		
		if (! ($INFO{$DUMMY} =~ /disabled/i) )
			{
			if ($INFO{$DUMMY} =~ /.*type\:.([0-9a-zA-Z]+)\, /i)
				{
				my $NICTYPE = $1;
				#print "\$NICTYPE = '$1<br>";
				switch ($NICTYPE)
					{
					case "Am79C970A"
						{
						push (@NICDATA , ["pcnet:$COUNT","#".($COUNT+1)." (PCnet-PCI II)"]);
						push (@NICEXTRA , [$COUNT , "#".($COUNT+1)." (PCnet-PCI II)"]);
						push (@NICNATPF , [$COUNT+1 , "#".($COUNT+1)." (PCnet-PCI II)"]);
						}
					
					case "Am79C973"
						{
						push (@NICDATA , ["pcnet:$COUNT","#".($COUNT+1)." (PCnet-PCI III)"]);
						push (@NICEXTRA , [$COUNT , "#".($COUNT+1)." (PCnet-PCI III)"]);
						push (@NICNATPF , [$COUNT+1 , "#".($COUNT+1)." (PCnet-PCI III)"]);
						}
					
					case "82540EM"
						{
						push (@NICDATA , ["e1000:$COUNT","#".($COUNT+1)." (Intel PRO/1000 MT Desktop)"]);
						push (@NICEXTRA , [$COUNT , "#".($COUNT+1)." (Intel PRO/1000 MT Desktop)"]);
						push (@NICNATPF , [$COUNT+1 , "#".($COUNT+1)." (Intel PRO/1000 MT Desktop)"]);
						}
					
					case "82543GC"
						{
						push (@NICDATA , ["e1000:$COUNT","#".($COUNT+1)." (Intel PRO/1000 T Server)"]);
						push (@NICEXTRA , [$COUNT , "#".($COUNT+1)." (Intel PRO/1000 T Server)"]);
						push (@NICNATPF , [$COUNT+1 , "#".($COUNT+1)." (Intel PRO/1000 T Server)"]);
						}
					
					case "82545EM"
						{
						push (@NICDATA , ["e1000:$COUNT","#".($COUNT+1)." (Intel PRO/1000 MT Server)"]);
						push (@NICEXTRA , [$COUNT , "#".($COUNT+1)." (Intel PRO/1000 MT Server)"]);
						push (@NICNATPF , [$COUNT+1 , "#".($COUNT+1)." (Intel PRO/1000 MT Server)"]);
						}
					
					case "virtio"
						{
						push (@NICDATA , ["virtio-net:$COUNT","#".($COUNT+1)." (Virtio-net)"]);
						push (@NICEXTRA , [$COUNT , "#".($COUNT+1)." (Virtio-net)"]);
						push (@NICNATPF , [$COUNT+1 , "#".($COUNT+1)." (Virtio-net)"]);
						}
					}
				}
			}
		else
			{
			#push (@NIC , "disabled");
			}
		
		$COUNT++;
		}
	}

(@TABHEAD) = ($text{'tabhead_set'},
		$text{'tabhead_source'},
		$text{'tabhead_nic'},
		$text{'tabhead_service'},
		$text{'tabhead_protocol'},
		$text{'tabhead_hostip'},
		$text{'tabhead_hostport'},
		$text{'tabhead_direction'},
		$text{'tabhead_guestip'},
		$text{'tabhead_guestport'});
@TD = ("width=1%","width=30%","width=30%","width=1%","width=10%","width=10%","width=10%","width=1% align='center'","width=10%","width=10%");

#%DATANAT = GetNATPF($USER,$VM);
%DATAEXTRA =GetVMExtraNICData($USER, $VM);

my $XMLFILE = $INFO{'Config file'};
my $VMNAT = Read_NatXML($XMLFILE, 'fh00');

if (IsVMNIC($USER,$VM))
	{
	my $XMLFILE = $INFO{'Config file'};
	#print "Config File: $XMLFILE <br>";
	my $VMNAT = Read_NatXML($XMLFILE, 'fh00');
	#print keys (%{$VMNAT->{0}->{'natrule'}})."<br>";
	
	push(@linksrow , "<a href='vmextra_import.cgi?vm=$VM&user=$USER'>$text{'IMPORT_FORWARDING'}</a>");
	if (%DATAEXTRA | $VMNAT->{'NAT'})
		{
		push(@linksrow , "<a href='vmextra_export.cgi?vm=$VM&user=$USER'>$text{'EXPORT_FORWARDING'}</a>");
		}
	
	print &ui_form_start("forward_vm.cgi", "post");
	print ui_hidden("vm",$VM);
	print ui_hidden("user",$USER);
	
	print &ui_links_row(\@linksrow);
	print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
	
	# Portforwarding via NATRules - New Version
	for (my $NIC=1; $NIC <= 8; $NIC++)
		{
		
		foreach my $RULE (keys %{$VMNAT->{$NIC-1}->{'natrule'}})
			{
			
			
			my ($SERVICE) = $RULE;
			my ($PROTOCOL) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'proto'};
			my ($HOSTIP) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'hostip'};
			my ($HOSTPORT) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'hostport'};
			my ($GUESTIP) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'guestip'};
			my ($GUESTPORT) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'guestport'};
			
			#print "# $NIC $SERVICE $PROTOCOL $HOSTIP $HOSTPORT $GUESTIP $GUESTPORT <br>";
			
			my @TABDATA = (
				ui_hidden("NAT_SRC_$SERVICE:$NIC","natpf").ui_textbox("NAT_SRC_$SERVICE:$NIC","natpf",10,1),
				ui_hidden("NAT_OLDNIC_$SERVICE:$NIC","$SERVICE:$NIC").ui_select("NAT_NEWNIC_$SERVICE:$NIC",$NIC,\@NICNATPF),
				ui_textbox("NAT_TAG_$SERVICE:$NIC",$SERVICE,10,0),
				&ui_select("NAT_PROT_$SERVICE:$NIC",$PROTOCOL,[[ "TCP", "TCP" ],[ "UDP", "UDP" ]]),
				ui_textbox("NAT_HIP_$SERVICE:$NIC",$HOSTIP,13,0),
				ui_textbox("NAT_HPORT_$SERVICE:$NIC",$HOSTPORT,5,0),
				"-->",
				ui_textbox("NAT_GIP_$SERVICE:$NIC",$GUESTIP,13,0),
				ui_textbox("NAT_GPORT_$SERVICE:$NIC",$GUESTPORT,5,0)
				);
			print ui_checked_columns_row(\@TABDATA,\@TD,'natpf',"$SERVICE:$NIC");
			}
		}
	
	# Portforwarding via ExtraData - Old Version
	foreach $DUMMY(sort keys %DATAEXTRA)
		{
		
		foreach $DUMMY2(sort keys %{$DATAEXTRA{$DUMMY}})
			{
			#print"Key1: '$DUMMY' Key2: '$DUMMY2' -> '${$DATAEXTRA{$DUMMY}}{$DUMMY2}{'Protocol'}'<br>";
			
			my $SERVICE = $DUMMY2;
			my ($NICTYPE,$PROTOCOL) = split(":" , ${$DATAEXTRA{$DUMMY}}{$DUMMY2}{'Protocol'});
			#print "$NICTYPE $PROTOCOL <br>";
			my ($NICTYPE,$GUESTPORT) = split(":" , ${$DATAEXTRA{$DUMMY}}{$DUMMY2}{'GuestPort'});
			my ($NICTYPE,$HOSTPORT) = split(":" , ${$DATAEXTRA{$DUMMY}}{$DUMMY2}{'HostPort'});
			my $NIC = "$NICTYPE:$DUMMY";
			
			#print "NIC: $NIC NICTYPE: $NICTYPE SERVICE: $SERVICE<br>";
			
			my @TABDATA = (
					ui_hidden("EXT_SRC_$SERVICE:$NIC","extradata").ui_textbox("EXT_SRC_$SERVICE:$NIC","extradata",10,1),
					ui_hidden("EXT_$SERVICE:$NIC","$SERVICE:$NICTYPE").ui_select("EXT_NIC_$SERVICE:$NIC",$NIC,\@NICDATA,1,0,0,0),
					ui_textbox("EXT_TAG_$SERVICE:$NIC",$SERVICE,10,0),
					&ui_select("EXT_PROT_$SERVICE:$NIC",$PROTOCOL,[[ "TCP", "TCP" ],[ "UDP", "UDP" ]],1,0,0,0),
					ui_textbox("EXT_HIP_$SERVICE:$NIC","",13,1,0),
					ui_textbox("EXT_HPORT_$SERVICE:$NIC",$HOSTPORT,5,0),
					"-->",
					ui_textbox("EXT_GIP_$SERVICE:$NIC","",13,1,0),
					ui_textbox("EXT_GPORT_$SERVICE:$NIC",$GUESTPORT,5,0)
					);
			print ui_checked_columns_row(\@TABDATA,\@TD,'vmextra',"$SERVICE:$NIC");
			}
		}
	
	print &ui_columns_end();
	print &ui_links_row(\@linksrow);
	print &ui_submit($text{'vmextraupdate_title'}, "update"),&ui_submit($text{'vmextradelete_title'}, "delete"),"<br>\n";
	
	print &ui_form_end();
	
	# Add New Extradata for VM
	
	# If VM Offline
	#if (! $VMRUNNING)
	#	{
		# delete "Set" from @TABHEAD
		shift @TABHEAD;
		unshift @TABHEAD, " ";
		
		@TABDATA = (
				" ",
				&ui_select("SRC", $in{'SRC'},[[ "natpf", "natpf" ],[ "extradata", "extradata" ]]),
				&ui_select("NIC", $in{'NIC'},\@NICDATA,1,0,0,$VMRUNNING),
				ui_textbox("SERVICE",$in{'SERVICE'},10),
				&ui_select("PROTOCOL", $in{'PROTOCOL'},[[ "TCP", "TCP" ],[ "UDP", "UDP" ]],1,0,0,0),
				ui_textbox("HOSTIP",$in{'HOSTIP'},13),
				ui_textbox("HOSTPORT",$in{'HOSTPORT'},5),
				"-->",
				ui_textbox("GUESTIP",$in{'GUESTIP'},13),
				ui_textbox("GUESTPORT",$in{'GUESTPORT'},5)
				);
		
		print &ui_form_start("forward_vm.cgi", "post");
		print ui_hidden("vm",$VM);
		print ui_hidden("user",$USER);
		print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
		print ui_columns_row(\@TABDATA,\@TD);
		print &ui_columns_end();
		print &ui_submit($text{'vmextraadd_title'}, "add"),"<br>\n";
		print &ui_form_end();
	#	}
	}
else
	{
	print "<b>$text{'VMEXTRA_NONICERROR'}</b> <p>\n";
	}

# Ruecksprung zur anfordernden Seite
if ($in{'mode'})
	{
	#print "return -> index.cgi?mode=$in{'mode'}<br>";
	print ui_print_footer("index.cgi?mode=$in{'mode'}", $text{'index_return'});
	}
elsif ($in{state})
	{
	print ui_print_footer("list_all_pfs.cgi", $text{'PORTFORWARD_ALL_VMS'});
	}
else
	{
	print ui_print_footer("index.cgi?mode=vm", $text{'index_return'});
	}

sub PrintWait
	{
	#print "Content-type: text/html"."\n\n";
	print "<html><body>";
	print "<br><br><br><br><br>";
	print "<center><img src='images/boxguy.gif'></center>";
	}


sub GoBack
	{
	if ($DEBUGMODE)
		{
		print "redirect to forward_vm.cgi?vm=$VM&user=$USER <br>";
		}
	else
		{
		print "<script type=\"text/javascript\">";
		print "window.location=\"forward_vm.cgi?vm=$VM&user=$USER\";";
		print "</script>";
		}
	}

