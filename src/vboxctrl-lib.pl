#!/usr/bin/perl


use WebminCore;
use File::Basename;
use Switch;
init_config();

$DEBUGMODE = $config{'DEBUGMODE'};
my $VBOXBIN = $config{'PATH_VB_BIN'};
if (! ($VBBOXBIN =~ /\/$/))
	{
	$VBOXBIN .= "/";
	}


#**********************************************************
# 
#**********************************************************
sub CheckIP()
	{
	my ($IP) = @_;
	if ($IP =~ /^([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])\.([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])\.([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])\.([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$/)
		{
		return 0;
		}
	else
		{
		return 1;
		}
	}


#**********************************************************
# 
#**********************************************************
sub DebugOut()
	{
	#ui_print_header(undef, $HEADER, "", "vboxctrl_help", 1, 1);
	&ui_print_header(undef, "DebugOut On", "","vboxctrl_help", 1,1);
	print "<hr>";
	foreach $dummy(sort keys %in)
		{
		if ($dummy =~ /^upload$/i)
			{
			print"Key: '$dummy' -> <b>UPLOADEDFILE</b> <br>";
			}
		else
			{
			print"Key: '$dummy' -> '$in{$dummy}'<br>";
			}
		}
	print "<br>";
	print "HTTP_REFERER -> '$ENV{'HTTP_REFERER'}'<br>";
	print "REQUEST_URI -> '$ENV{'REQUEST_URI'}'<hr>";
	return 1;
	}


#**********************************************************
# 
#**********************************************************
sub Read_NatXML
	{
	my ($FILE, $FILEHANDLER) = @_;
	my ($FOUND,$MAC,$NATALIAS,$NATRULE,$SLOT,$NIC);
	no strict 'refs';
	
	my $IsNATRule = 0;
	
	# Name des Filehaendler veraendern
	$FILEHANDLER++;
	
	open ($FILEHANDLER , "$FILE");
	while (<$FILEHANDLER> )
		{
		chomp;	# kein Newline	
		s/#.*//;# keine Kommentare
		s/^\s+//;# keine führende Whitespaces
		s/\s+$//;# keine anhängenden Whitespaces
		next unless length;# noch was da?
		# Sektionen
		#<Adapter slot="0" enabled="true" MACAddress="08002714900F" cable="true" speed="0" type="Am79C973"
		if ( $_ =~ /\<Adapter /i )
			{
			$FOUND = 1;
			my $LINE = $';
			$LINE =~ s/\>//g;
			$LINE =~ s/\"//g;
			$LINE =~ /slot=([0-7])/i;
			$SLOT = $1;
			$LINE =~ s/^\s+//;
			
			#print "Found at slot $SLOT<br>";
			
			foreach my $DUMMY (split(" " , $LINE))
				{
				my ($KEY,$VAL) = split("=" , $DUMMY);
				$KEY = lc($KEY);
				$VAL =~ s/false/0/;
				$VAL =~ s/true/1/;
				$NIC->{$SLOT}->{$KEY} = $VAL;
				}
			next;
			}
		
		# Daten
		if ($FOUND)
			{
			if ($_ =~ /\<alias /i)
				{
				my $LINE = $';
				my $ALIAS = 0;
				#<Alias logging="true" proxy-only="false" use-same-ports="false"/>
				#$_ =~ /\bproxy-only=\"(.+)\" \b/i;
				$LINE =~ s/\/\>//g;
				$LINE =~ s/\"//g;
				foreach my $DUMMY (split(" " , $LINE))
					{
					my ($KEY,$VAL) = split("=" , $DUMMY);
					switch (lc($KEY))
						{
						case "logging" {if ($VAL =~ /true/i){$ALIAS = 1;}}
						case "proxy-only" {if ($VAL =~ /true/i){$ALIAS = 2;}}
						case "use-same-ports" {if ($VAL =~ /true/i){$ALIAS = 4;}}
						}
					$NIC->{$SLOT}->{'alias'} = $ALIAS;
					}
				}
			if ($_ =~ /\<Forwarding /i)
				{
				
				my $LINE = $';
				my $ALIAS = 0;
				#Forwarding name="qqq" proto="0" hostip="1.1.1.1" hostport="11" guestip="2.2.2.2" guestport="22"/>
				#$_ =~ /\bproxy-only=\"(.+)\" \b/i;
				$LINE =~ s/\/\>//g;
				$LINE =~ s/\"//g;
				
				my %NATLINE;
				foreach my $DUMMY (split(" " , $LINE))
					{
					my ($KEY,$VAL) = split("=" , $DUMMY);
					$NATLINE{$KEY} = $VAL;
					}
				
				my $RULE = $NATLINE{'name'};
				delete $NATLINE{'name'};
				
				foreach my $KEY (keys %NATLINE)
					{
					my $VAL = $NATLINE{$KEY};
					if ($KEY =~ /^proto$/i)
						{
						$VAL = ($VAL)?"TCP":"UDP";
						}
					$NIC->{$SLOT}->{'natrule'}->{$RULE}->{$KEY} = $VAL;
					
					#print "Rule: $RULE $KEY -> $VAL <br>";
					}
				$IsNATRule = 1;
				}
			elsif ($_ =~ /\<NAT /i)
				{
				my $NATNET = $';
				$NATNET =~ s/>//g;
				$NATNET =~ s/\"//g;
				$NATNET =~ s/network\=//gi;
				$NIC->{$SLOT}->{'natnet'} = $NATNET;
				#print "NAT Network --> '$NATNET' <br>"
				}
			}
		}
	close ($FILEHANDLER);
	$NIC->{'NAT'} = $IsNATRule;
	return $NIC;
	}


#**********************************************************
# 
#**********************************************************
sub Read_NatXML_
	{
	my ($FILE, $FILEHANDLER) = @_;
	my ($FOUND,$MAC,$NATALIAS);
	no strict 'refs';
	
	# Name des Filehaendler veraendern
	$FILEHANDLER++;
	
	open ($FILEHANDLER , "$FILE") or ERROR(6,"Read_Config()");
	while (<$FILEHANDLER> )
		{
		chomp;	# kein Newline	
		s/#.*//;# keine Kommentare
		s/^\s+//;# keine führende Whitespaces
		s/\s+$//;# keine anhängenden Whitespaces
		next unless length;# noch was da?
		# Sektionen
		if ( $_ =~ /macaddress=\"/i )
			{
			$FOUND = 1;
			$MAC = $';
			$MAC =~ /"/;
			$MAC = $`;
			next;
			}
		
		# Daten
		if ($FOUND)
			{
			if ($_ =~ /\<alias /i)
				{
				my $LINE = $';
				my $ALIAS = 0;
				
				$LINE =~ s/\/\>//g;
				$LINE =~ s/\"//g;
				foreach my $DUMMY (split(" " , $LINE))
					{
					my ($KEY,$VAL) = split("=" , $DUMMY);
					switch (lc($KEY))
						{
						case "logging" {if ($VAL =~ /true/i){$ALIAS = 1;}}
						case "proxy-only" {if ($VAL =~ /true/i){$ALIAS = 2;}}
						case "use-same-ports" {if ($VAL =~ /true/i){$ALIAS = 4;}}
						}
					$NATALIAS->{lc($MAC)} = $ALIAS;
					}
				}
			}
		}
	close ($FILEHANDLER);
	return $NATALIAS;
	}

# Get the Tempdir depend of the ModulConfig
sub GetTempDir
	{
	my $TEMPEXPORTDIR = $config{'vboxexport'};
	
	if (! ($TEMPEXPORTDIR =~ /\/$/))
		{
		$TEMPEXPORTDIR .= "/";
		}
	
	my $TEMPDIR = &transname();
	
	if ($config{'multiuser'})
		{
		my $DUMMY = basename($TEMPDIR);
		$DUMMY =~ s/\.cgi//g;
		$TEMPEXPORTDIR = $TEMPEXPORTDIR.$DUMMY;
		}
	else
		{
		$TEMPDIR =~ s/\.cgi//g;
		$TEMPEXPORTDIR = $TEMPDIR;
		}
	
	return $TEMPEXPORTDIR;
	}


#**********************************************************
# Check if the User is in the UX-Group "Admingroup" such as <admins>
#**********************************************************
sub IsAdmin
	{
	my $USER = shift;
	
	my $RET = 0;
	my $VBADMINGROUP = $config{'ADMINGROUP'};
	my $VBADMINMODE = $config{'ADMINMODE'};
	
	# VB Admin mode is used
	if ($VBADMINMODE)
		{
		# Read the standard group file
		
		#print "Admingroup: '$VBADMINGROUP'<br>";
		$COMMAND = "cat /etc/group | grep -i \"^$VBADMINGROUP\" ";
		my $RETURN = readpipe($COMMAND);
		#print "Command: '$COMMAND' <br> Return: '$RETURN'<br>";
		$RETURN =~ s/\r|\n//g;
		my @DUMMY = split(":" , $RETURN);
		my @USER = split("," , $DUMMY[3]);
		@USER = sort(@USER);
		foreach my $DUMMY (@USER)
			{
			#print "'$DUMMY' = '$USER' ?? <br>";
			if ($DUMMY eq $USER){$RET = 1;}
			}
		#print "<hr>";
		}
	#Simulate used Adminmode
	else
		{
		$RET = 1;
		}
	
	#print "Adminmode: $RET<br>";
	return $RET;
	}


#**********************************************************
# 
#**********************************************************
sub GetVBoxUser
	{
	# Read the standard group file
	my (@USER);
	
	# VB Admin mode is used
	if (IsAdmin($remote_user))
		{
		$COMMAND = "cat /etc/group | grep -i vboxusers";
		my $RETURN = readpipe($COMMAND);
		$RETURN =~ s/\r|\n//g;
		my @DUMMY = split(":" , $RETURN);
		#print "'$RETURN' '$DUMMY[3]'<br>";
		@USER = split("," , $DUMMY[3]);
		@USER = sort(@USER);
		}
	else
		{
		push (@USER, $remote_user);
		}
	#foreach my $DUMMY (sort @USER)
	#	{
	#	print "User: '$DUMMY'<br>";
	#	}
	return @USER;
	}

#**********************************************************
# 
#**********************************************************
sub GetStartupUser
	{
	my $COMMAND = "cat $config{'FILE_STARTUPSCRIPT'} | grep -i \"VM_USER=\" ";
	my $RETURN = readpipe($COMMAND);
	$RETURN =~ s/\"//g;
	my ($VAR,$USER) = split("=",$RETURN);
	chomp($USER);
	return $USER;
	}


#**********************************************************
# 
#**********************************************************
sub ReadEnabledVM
	{
	my ($VMENABLED);
	my $ERROR = 1;
	my $FILE_VMENABLED = $config{'FILE_VM_ENABLED'};
	
	# if config alue set?
	if ($FILE_VMENABLED)
		{
		# does file exist?
		if (-f $FILE_VMENABLED)
			{
			
			my $COMMAND = "cat $FILE_VMENABLED ";
			my @RETURN = readpipe($COMMAND);
			
			foreach my $DUMMY (sort @RETURN)
				{
				$DUMMY =~ s/^\s+//;# keine führende Whitespaces
				$DUMMY =~ s/\s+$//;# keine anhängenden Whitespaces
				
				if ($DUMMY)
					{
					#print "Read --> '$DUMMY'<br>";
					$VMENABLED->{$DUMMY} = "read";
					}
				}
			$ERROR = 0;
			}
		}
	return $VMENABLED,$ERROR;
	}

#**********************************************************
# 
#**********************************************************
sub WriteEnabledVM
	{
	my $VM_ENABLED = shift;
	
	my $FILEVMENABLED = $config{'FILE_VM_ENABLED'};
	
	open (FILEHANDLER , ">$FILEVMENABLED");
	
	foreach my $KEY (sort keys %{$VM_ENABLED})
		{
		#print "Write --> '$KEY' -> '$VM_ENABLED{$KEY}'<br>";
		print FILEHANDLER "$KEY\n";
		}
	
	close (FILEHANDLER);
	}

sub IsVMRunning
	{
	my $USER = @_[0];
	my $VM = @_[1];
	my $COMMAND;
	
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $USER ";
		}
	#print "VM: '$VM'<br>";
	$COMMAND .= $VBOXBIN."VBoxManage -q list runningvms";
	my $RETURN = readpipe($COMMAND);
	
	# collect running VMs Infos
	my @DATA = split("\n",$RETURN);
	
	foreach my $DUMMY (@DATA)
		{
		#print "$VM -> $DUMMY<br>";
		if ($DUMMY =~ /^\"$VM\"/gi)
			{
			return 1;
			}
		}
	
	return 0;
	}


sub GetHDDsFromVM
	{
	my @USEDHDDS;
	my ($USER, $VM) = @_;
	
	# collect all HDDs, return: ($USER:$VM:$FILE)
	my %HDDS = ListHDDS();
	
	foreach my $KEY(sort keys %HDDS)
		{
		
		my ($TMPUSER,$TMPVM,$TMPFILE) = split (":" , $KEY);
		
		#print "A B C $TMPUSER $TMPVM $TMPFILE<br>";
		
		if ( ($USER eq $TMPUSER) && ($VM eq $TMPVM) )
			{
			#print "Use me! => $HDDS{$KEY}<br>";
			push (@USEDHDDS , $HDDS{$KEY});
			}
		}
	return @USEDHDDS;
	}

sub GetHDDsFromVM_
	{
	my @USEDHDDS;
	my ($USER, $VM) = @_;
	
	# collect all HDDs, return: ($USER:$VM:$FILE)
	my %HDDS = ListHDDS();
	
	foreach my $UUID(sort keys %HDDS)
		{
		if ($UUID =~ /^$USER\:/i)
			{
			#print "KEY: $UUID<br>";
			#print "=> ".%HDDS->{$UUID}->{'State'}."<br>";
			#print "=> ".%HDDS->{$UUID}->{'UUID'}."<br>";
			#print "=> ".%HDDS->{$UUID}->{'Usage'}."<br>";
			
			my $HDUUID = %HDDS->{$UUID}->{'UUID'};
			my $USAGE = %HDDS->{$UUID}->{'Usage'};
			#print "VM: '$VM' UUID: '$UUID' HDUUID: '$HDUUID' USAGE: '$USAGE'<br>";
			#print "index('$USAGE','$VM'): ".index ($USAGE,$VM)."<br>";
			if ($USAGE =~ /^$VM /i)
				{
				#print "<b> '$USAGE' '$VM' '$HDUUID'</b><br>";
				my %HDINFO = GetHDInfo($USER,$HDUUID);
				push (@USEDHDDS , \%HDINFO);
				}
			}
		}
	return @USEDHDDS;
	}

sub GetDHCPServers
	{
	my (@DHCPSERVERS);
	
	$COMMAND = $VBOXBIN."VBoxManage -q list dhcpservers";
	my $RETURN = readpipe($COMMAND);
	
	# collect IFs Infos
	my @DATA = split("\n\n",$RETURN);
	
	foreach my $DUMMY (@DATA)
		{
		#print "'$DUMMY'<br>\n";
		
		# collect dhcpserver Infos
		my @DATA2 = split("\n",$DUMMY);
		
		# create new object
		my(%DHCPSERVERS);
		#print "================<br>";
		
		foreach my $DUMMY2 (@DATA2)
			{
			#print "--> '$DUMMY2'<br>\n";
			
			my (@DUMMY3) = split("\n" , $DUMMY2);
			
			foreach my $DUMMY3 (@DUMMY3)
				{
				my ($KEY,$VAL) = split(":" , $DUMMY3);
				$KEY =~ s/^\s+//g;
				$KEY =~ s/\s+$//g;
				$VAL =~ s/^\s+//g;
				$VAL =~ s/\s+$//g;
				$DHCPSERVERS{$KEY} = $VAL;
				
				#print "'$KEY' --> '$VAL'<br>";
				}
			}
		
		push(@DHCPSERVERS , \%DHCPSERVERS);
		}
	
	return @DHCPSERVERS;
	}

#**********************************************************
# 
#**********************************************************
sub GetSystemProperties
	{
	my (@VBOXUSER);
	if ($config{'multiuser'})
		{
		@VBOXUSER = GetVBoxUser();
		}
	else
		{
		@VBOXUSER = "root";
		}
	
	my $PROPERTIES;
	
	foreach my $USER (sort @VBOXUSER)
		{
		#print "USER: $USER<br>";
		my $SYSTEMPROPERTIES;
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		$COMMAND .= $VBOXBIN."VBoxManage -q list systemproperties 2>&1";
		my $RETURN = readpipe($COMMAND);
		
		#print "<hr>$COMMAND<br>$RETURN<hr>";
		if ($RETURN =~ /error\:/)
			{
			$PROPERTIES->{$USER}->{'ERROR'} = $RETURN;
			}
		
		
		my @DUMMY = split("\n",$RETURN);
		
		foreach my $DUMMY (@DUMMY)
			{
			$DUMMY =~ s/^\s+//g;
			$DUMMY =~ s/\s+$//g;
			next unless length($DUMMY);
			
			my ($KEY,$VAL) = split(":" , $DUMMY);
			$KEY =~ s/^\s+//g;
			$KEY =~ s/\s+$//g;
			$VAL =~ s/^\s+//g;
			$VAL =~ s/\s+$//g;
			#print "'$KEY' -> '$VAL'<br>";
			$PROPERTIES->{$USER}->{$KEY} = $VAL;
			}
		
		#$PROPERTIES{$USER} = \$SYSTEMPROPERTIES;
		}
	
	return $PROPERTIES;
	}


sub GetHOSTInfo
	{
	my (@DUMMY);
	my (%HOSTINFO);
	$COMMAND = $VBOXBIN."VBoxManage -q list hostinfo";
	my $RETURN = readpipe($COMMAND);
	
	my @DUMMY = split("\n",$RETURN);
	
	foreach my $DUMMY (@DUMMY)
		{
		$DUMMY =~ s/^\s+//g;
		$DUMMY =~ s/\s+$//g;
		next unless length($DUMMY);
		
		my ($KEY,$VAL) = split(": " , $DUMMY);
		$KEY =~ s/^\s+//g;
		$KEY =~ s/\s+$//g;
		$VAL =~ s/^\s+//g;
		$VAL =~ s/\s+$//g;
		$HOSTINFO{$KEY} = $VAL;
		}
	return %HOSTINFO;
	}

sub GetBridgedIfs
	{
	my (@BRIDGEDIF);
	
	$COMMAND = $VBOXBIN."VBoxManage -q list bridgedifs";
	my $RETURN = readpipe($COMMAND);
	
	# collect IFs Infos
	my @DATA = split("\n\n",$RETURN);
	
	foreach my $DUMMY (@DATA)
		{
		#print "'$DUMMY'<br>\n";
		
		# collect IFs Infos
		my @DATA2 = split("\n",$DUMMY);
		
		# create new object
		my(%BRIDGEDIF);
		
		foreach my $DUMMY2 (@DATA2)
			{
			#print "--> '$DUMMY2'<br>\n";
			
			my (@DUMMY3) = split("\n" , $DUMMY2);
			
			foreach my $DUMMY3 (@DUMMY3)
				{
				my ($KEY,$VAL) = split(": " , $DUMMY3);
				$KEY =~ s/^\s+//g;
				$KEY =~ s/\s+$//g;
				$VAL =~ s/^\s+//g;
				$VAL =~ s/\s+$//g;
				$BRIDGEDIF{$KEY} = $VAL;
				
				#print "'$KEY' --> '$VAL'<br>";
				}
			}
		
		push(@BRIDGEDIF , \%BRIDGEDIF);
		}
	
	return @BRIDGEDIF;
	}


sub GetHostOnlyIfs
	{
	my (@HOSTONLYIF);
	
	$COMMAND = $VBOXBIN."VBoxManage -q list hostonlyifs";
	my $RETURN = readpipe($COMMAND);
	
	# collect IFs Infos
	my @DATA = split("\n\n",$RETURN);
	
	foreach my $DUMMY (@DATA)
		{
		#print "'$DUMMY'<br>\n";
		
		# collect IFs Infos
		my @DATA2 = split("\n",$DUMMY);
		
		# create new object
		my(%HOSTONLYIF);
		
		foreach my $DUMMY2 (@DATA2)
			{
			#print "--> '$DUMMY2'<br>\n";
			
			my (@DUMMY3) = split("\n" , $DUMMY2);
			
			foreach my $DUMMY3 (@DUMMY3)
				{
				my ($KEY,$VAL) = split(": " , $DUMMY3);
				$KEY =~ s/^\s+//g;
				$KEY =~ s/\s+$//g;
				$VAL =~ s/^\s+//g;
				$VAL =~ s/\s+$//g;
				$HOSTONLYIF{$KEY} = $VAL;
				
				#print "'$KEY' --> '$VAL'<br>";
				}
			}
		
		push(@HOSTONLYIF , \%HOSTONLYIF);
		}
	
	return @HOSTONLYIF;
	}


sub GetNIC
	{
	if (IsVB32())
		{
		my %NIC;
		
		my $USER = @_[0];
		my $VM = @_[1];
		
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage -q showvminfo \"$VM\"";
		my $RETURN = readpipe($COMMAND);
		my @DUMMY = split("\n",$RETURN);
		
		foreach my $DUMMY (@DUMMY)
			{
			#print "'$DUMMY'<br>\n";
			if ($DUMMY =~ /^nic.([1-9])\:/i)
				{
				my $NIC_N = $1;
				my $last = $';
				$last =~ s/\(file\: ?/(/gi;
				
				#print "found: <i>'$DUMMY'</i> $1<br>\n";
				#print "-> '$last'<br>";
				
				my %DUMMY;
				my @VALS = split("," , $last);
				my $FOUND = 0;
				foreach my $DUMMY2 (@VALS)
					{
					my ($KEY2,$VAL2) = split(":" , $DUMMY2);
					
					$KEY2 =~ s/^\s+//g;
					$KEY2 =~ s/\s+$//g;
					$VAL2 =~ s/^\s+//g;
					$VAL2 =~ s/\s+$//g;
					
					if (!($KEY2 =~ /disabled/i))
						{
						#print "STORE: #$NIC_N '$KEY2' -> '$VAL2'<br>";
						$DUMMY{$KEY2} = $VAL2;
						$FOUND = 1;
						}
					}
				if ($FOUND)
					{
					$NIC{$NIC_N} = \%DUMMY;
					}
				#print;
				}
			}
		return %NIC;
		}
	else
		{
		return false;
		}
	}



sub GetNATPF
	{
	if (IsVB32())
		{
		my %NATPF;
		
		my $USER = @_[0];
		my $VM = @_[1];
		
		my $COMMAND;
		
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		$COMMAND .= $VBOXBIN."VBoxManage -q showvminfo \"$VM\"";
		my $RETURN = readpipe($COMMAND);
		my @DUMMY = split("\n",$RETURN);
		
		foreach my $DUMMY (@DUMMY)
			{
			#print "'$DUMMY'\n";
			if ($DUMMY =~ /rule\(/i)
				{
				my($KEY,$VAL) = split(":" , $DUMMY);
				$KEY =~ /rule\(/i;
				my $NIC = $`;
				$NIC =~ s/^\s+//g;
				$NIC =~ s/\s+$//g;
				$NIC =~ s/nic //i;
				
				my %DUMMY;
				my @VALS = split("," , $VAL);
				foreach my $DUMMY2 (@VALS)
					{
					my ($KEY2,$VAL2) = split("=" , $DUMMY2);
					
					$KEY2 =~ s/^\s+//g;
					$KEY2 =~ s/\s+$//g;
					$VAL2 =~ s/^\s+//g;
					$VAL2 =~ s/\s+$//g;
					
					$DUMMY{$KEY2} = $VAL2;
					}
				$NAME = "$NIC\_$DUMMY{'name'}";
				$NATPF{$NAME} = \%DUMMY;
				#print;
				}
			}
		return %NATPF;
		}
	else
		{
		return false;
		}
	}

# New for VB 3.2.6
sub GetVBVersion
	{
	$COMMAND = $VBOXBIN."VBoxManage --nologo -v";
	my $RETURN = readpipe($COMMAND);
	return $RETURN;
	}

sub GetGuestAddonVersion
	{
	my $USER = shift;
	my $VM = shift;
	
	my $COMMAND;
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $USER ";
		}

	$COMMAND .= $VBOXBIN."VBoxManage -q guestproperty get \"$VM\" /VirtualBox/GuestAdd/Version";
	my $RETURN = readpipe($COMMAND);
	
	$RETURN =~ s/value\://gi;
	$RETURN =~ s/^\s+//g;
	$RETURN =~ s/\s+$//g;
	
	
	return $RETURN;
	}


# Check if Version 3.2.xx
sub IsVB32
	{
	my $DUMMY = GetVBVersion();
	
	if ($DUMMY =~ /^3\.2/)
		{
		return true;
		}
	else
		{
		return false;
		}
	}


sub GetAllDVDS
	{
	
	#*********************************
	# Collect all known ISOs by User
	#*********************************
	if ($config{'multiuser'})
		{
		@VBOXUSER = GetVBoxUser();
		}
	else
		{
		@VBOXUSER = "root";
		}
	
	my %DVDS;
	
	foreach my $USER (sort @VBOXUSER)
		{
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		# collect VM ISOs
		$COMMAND .= $VBOXBIN."VBoxManage -q list dvds";
		my $RETURN = readpipe($COMMAND);
		#print "<b>Command:</b> $COMMAND - <br><b>RETURN:</b> $RETURN <br>";
		
		# seperate blocks
		my @BLOCKS = split("\n\n",$RETURN);
		
		foreach my $BLOCK (@BLOCKS)
			{
			my %DVD;
			my ($UUID,$VM);
			my @DUMMY = split ("\n", $BLOCK);
			
			my @DOUBLE;
			
			foreach my $LINE (@DUMMY)
				{
				$LINE =~ /\:+?/;
				my $KEY = $`;
				my $VALUE = $';
				$VALUE =~ s/^\s+//g;
				
				#print "'$KEY' -> '$VALUE'<br>";
				
				if ($KEY =~ /\(uuid$/i)
					{
					my $VMTMP = $KEY;
					$VMTMP =~ s/\(uuid//i;
					$VMTMP =~ s/^\s+//g;
					$VMTMP =~ s/\s+$//g;
					
					$VALUE = "$KEY: $VALUE";
					$VALUE =~ s/^\s+//g;
					$VALUE =~ s/\s+$//g;
					$DVD{'Usage'} .= "<br>$VALUE";
					push(@DOUBLE , $VMTMP);
					
					#print "'$KEY' -> '$VALUE' -> '$VMTMP'<br>";
					}
				else
					{
					$DVD{$KEY} = $VALUE;
					#print "'$KEY' -> '$VALUE'<br>";
					}
				
				if ($LINE =~ /location/i)
					{
					$LINE =~ /\:/;
					my $KEY = $`;
					my $VALUE = $';
					$VALUE =~ s/^\s+//g;
					$LOCATION = $VALUE;
					}
				elsif ($LINE =~ /Usage/i)
					{
					$LINE =~ /\:/;
					my $KEY = $`;
					$VM = $';
					$VM =~ /\(/;
					$VM = $`;
					$VM =~ s/\s+$//g;
					$VM =~ s/^\s+//g;
					}
				}
			#print "$USER:$VM:$LOCATION<hr>";
			$DVDS{"$USER:$VM:$LOCATION"} = \%DVD;
			
			if (@DOUBLE)
				{
				foreach my $VM (@DOUBLE)
					{
					#print "Double: $USER:$VM:$LOCATION<br>";
					$DVDS{"$USER:$VM:$LOCATION"} = \%DVD;
					}
				}
			
			}
		}
	return %DVDS;
	}

sub GetHDInfo
	{
	
	my %HDDINFO;
	my $USER = @_[0];
	my $FILE = @_[1];
	
	my $COMMAND;
	if ( ($config{'multiuser'}) && ($USER) )
		{
		$COMMAND = "sudo -H -u $USER ";
		}
	$COMMAND .= $VBOXBIN."VBoxManage -q showhdinfo '$FILE'";
	my $RETURN = readpipe($COMMAND);
	
	#print "<b>Command:</b> $COMMAND - <br><b>RETURN:</b> $RETURN <br>";
	
	
	my @DUMMY = split("\n",$RETURN);
	
	foreach $DUMMY (@DUMMY)
		{
		#print "HDINFO: '$DUMMY'<br>";
		if ($DUMMY =~ /([a-zA-Z \-]+)\:{1}/)
			{
			my $KEY = $1;
			my $VALUE = $';
			$VALUE =~ s/^\s+//g;
			$VALUE =~ s/\s+$//g;
			
			#print "HDINFO: '$KEY' -> '$VALUE'<br>";
			
			$HDDINFO{$KEY} = $VALUE;
			}
		}
	
	return %HDDINFO;
	}


sub ListPoolHDDS
	{
	
	my %HDD;
	my $FILE;
	
	$POOLDIR = $config{'PATH_VB_DEFAULTHDPATH'};
	if (! ($POOLDIR =~ /\/$/))
		{
		$POOLDIR .= "/";
		}
	
	$COMMAND = "ls $POOLDIR | grep -i .v*";
	my $RETURN = readpipe($COMMAND);
	
	my @HDDS = split("\n" , $RETURN);
	
	foreach my $FILE (@HDDS)
		{
		my %HD;
		#print "Untersuche '$FILE'<br>";
		
		my $COMMAND = 
		$COMMAND = $VBOXBIN."VBoxManage -q showhdinfo \"$POOLDIR/$FILE\"";
		#print "$COMMAND <br>";
		my $RETURN = readpipe($COMMAND);
		
		my @LINES = split("\n",$RETURN);
		
		foreach my $LINE (@LINES)
			{
			#print "LINE: $LINE<br>";
			
			$LINE =~ /\:/;
			my $KEY = $`;
			my $VALUE = $';
			$VALUE =~ s/^\s+//g;
			
			#print "'$KEY' -> '$VALUE'<br>";
			
			$HD{$KEY} = $VALUE;
			
			if ($KEY eq "UUID")
				{
				$UUID = $VALUE;
				}
			#print "'$KEY' -> '$VALUE'<br>";
			
			$HD{$KEY} = $VALUE;
			}
		#print "MASTER: $POOLDIR$FILE <br>";
		$HDD{$UUID} = \%HD;
		}
	return %HDD;
	}


sub ListHDDS
	{
	
	my %HDD;
	my %FILE;
	my $LOC;
	
	#*********************************
	# Collect all known HDs by VB
	#*********************************
	if ($config{'multiuser'})
		{
		@VBOXUSER = GetVBoxUser();
		}
	else
		{
		@VBOXUSER = "root";
		}
	
	my %HDDS;
	
	foreach my $USER (sort @VBOXUSER)
		{
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		$COMMAND .= $VBOXBIN."VBoxManage -q list hdds";
		my $RETURN = readpipe($COMMAND);
		#print "Command: $COMMAND - <br>RETURN: $RETURN <br>";
		
		# seperate blocks
		my @BLOCKS = split("\n\n",$RETURN);
		
		foreach my $BLOCK (@BLOCKS)
			{
			#print "<hr>";
			my %HDD;
			my ($UUID,$VM);
			my @DUMMY = split ("\n", $BLOCK);
			
			my @DOUBLE;
			
			foreach my $LINE (@DUMMY)
				{
				$LINE =~ /\:+?/;
				my $KEY = $`;
				my $VALUE = $';
				$VALUE =~ s/^\s+//g;
				
				#print "'$KEY' -> '$VALUE'<br>";
				
				if ($KEY =~ /\(uuid$/i)
					{
					my $VMTMP = $KEY;
					$VMTMP =~ s/\(uuid//i;
					$VMTMP =~ s/^\s+//g;
					$VMTMP =~ s/\s+$//g;
					
					$VALUE = "$KEY: $VALUE";
					$VALUE =~ s/^\s+//g;
					$VALUE =~ s/\s+$//g;
					$HDD{'Usage'} .= "<br>$VALUE";
					push(@DOUBLE , $VMTMP);
					
					#print "'$KEY' -> '$VALUE' -> '$VMTMP'<br>";
					}
				else
					{
					$HDD{$KEY} = $VALUE;
					#print "'$KEY' -> '$VALUE'<br>";
					}
				
				if ($LINE =~ /location/i)
					{
					$LINE =~ /\:/;
					my $KEY = $`;
					my $VALUE = $';
					$VALUE =~ s/^\s+//g;
					$LOCATION = $VALUE;
					}
				elsif ($LINE =~ /Usage/i)
					{
					$LINE =~ /\:/;
					my $KEY = $`;
					$VM = $';
					$VM =~ /\(/;
					$VM = $`;
					$VM =~ s/\s+$//g;
					$VM =~ s/^\s+//g;
					}
				}
			#print "$USER:$VM:$LOCATION<hr>";
			$HDDS{"$USER:$VM:$LOCATION"} = \%HDD;
			
			if (@DOUBLE)
				{
				foreach my $VM (@DOUBLE)
					{
					#print "Double: $USER:$VM:$LOCATION<br>";
					$HDDS{"$USER:$VM:$LOCATION"} = \%HDD;
					}
				}
			
			$LOC .= "'$LOCATION' ";
			}
		}
	
	#************************************************
	# Collect all HDs in the Pooldir and test
	# if there not allready exists on the collection
	#************************************************
	$POOLDIR = $config{'PATH_VB_DEFAULTHDPATH'};
	if (! ($POOLDIR =~ /\/$/))
		{
		$POOLDIR .= "/";
		}
	$COMMAND = "ls $POOLDIR | grep -i .v*";
	#print "$COMMAND<br>";
	my $RETURN = readpipe($COMMAND);
	my @HDD = split("\n" , $RETURN);
	
	foreach my $FILE (@HDD)
		{
		my %HDD;
		my $LOCATION = $POOLDIR.$FILE;
		if (! ($LOC =~ /\'$LOCATION\'/i) )
			{
			#print "POOL: '$LOCATION' <br>";
			#my %HDD;
			$HDD{'location'} = $LOCATION;
			$HDDS{"::$LOCATION"} = \%HDD;
			}
		}
	
	return %HDDS;
	}

sub ListHDDS_
	{
	
	my %HDD;
	my $FILE;
	
	if ($config{'multiuser'})
		{
		@VBOXUSER = GetVBoxUser();
		}
	else
		{
		@VBOXUSER = "root";
		}
	
	foreach my $USER (sort @VBOXUSER)
		{
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		$COMMAND .= $VBOXBIN."VBoxManage -q list hdds";
		my $RETURN = readpipe($COMMAND);
		#print "Command: $COMMAND - RETURN: $RETURN <br>";
		
		my @DUMMY = split("\n\n",$RETURN);
		
		foreach $DUMMY (@DUMMY)
			{
			my %HD;
			my @DUMMY2 = split ("\n", $DUMMY);
			
			foreach my $LINE (@DUMMY2)
				{
				$LINE =~ /\:/;
				my $KEY = $`;
				my $VALUE = $';
				$VALUE =~ s/^\s+//g;
				
				#print "'$KEY' -> '$VALUE'<br>";
				
				$HD{$KEY} = $VALUE;
				
				if ($KEY eq "UUID")
					{
					$UUID = $VALUE;
					}
				}
			
			$HDD{"$USER:$UUID"} = \%HD;
			}
		}
	
	return %HDD;
	}


sub ListAllVM
	{
	my @VMS;
	my @VBOXUSER;
	my $COMMAND;
	
	if ($config{'multiuser'})
		{
		@VBOXUSER = GetVBoxUser();
		}
	else
		{
		@VBOXUSER = "root";
		}
	
	
	foreach my $USER (sort @VBOXUSER)
		{
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		$COMMAND .= $VBOXBIN."VBoxManage -q list vms";
		my $RETURN = readpipe($COMMAND);
		
		#print "<hr>$RETURN<hr>";
		
		my @DUMMY = split("\n",$RETURN);
		
		foreach my $DUMMY (@DUMMY)
			{
			($VM,$UID) = split("\" \{", $DUMMY);
			$VM =~ s/\"//gi;
			push (@VMS, "$USER:$VM");
			#print "$USER:$VM<br>";
			}
		}
	return @VMS;
	}


######################
#
######################
sub GetControllerMatrix
	{
	
	my $INFO = shift;
	my $XML = $INFO ->{'Config file'};
	
	my ($MATRIX,$CONTROLLER,$CTRL);
	my $FLAG = 0;
	# Controller definition - <Name><port><deviceport>
	my @CONTROLLER = (
			['IDE',2,2],
			['SCSI',16,1],
			['SATA',30,1],
			['SAS',8,1],
			);
	
	
	open (XML , $XML);
	while (<XML> )
		{
		chomp;			# kein Newline	
		s/^\s+//;		# keine führende Whitespaces
		s/\s+$//;		# keine anhängenden Whitespaces
		next unless length;	# noch was da?
		# Sektionen
		
		if ( $_ =~ /^\<StorageController /i )
			{
			my $LINE = $_;
			chomp $LINE;
			
			$LINE =~ / name=\"(.+?)\" /i;
			$CTRL = $1;
			
			$LINE =~ / type=\"(.+?)\" /i;
			my $TYPE = $1;
			
			
			
			# FD Special, while various cases for floppydisk
			if ($TYPE eq "I82078")
				{
				my $NAME = "$CTRL:FD";
				my $PORT = 2;
				my $DEVICE = 1;
				# loop for "PORT"
				for (my $p=0;$p<$PORT;$p++)
					{
					# loop for "PORTDEVICE"
					for (my $d=0;$d<$DEVICE;$d++)
						{
						# update the Controller matrix
						#my $KEY = $NAME."-Controller ($p, $d)";
						my $KEY = "$CTRL ($d, $p)";
						my $dd = sprintf ("%02d",$d);
						if (exists($INFO->{$KEY}))
							{
							$MATRIX->{$NAME}->{$dd}->{$p} = $INFO->{$KEY};
							}
						else
							{
							$MATRIX->{$NAME}->{$dd}->{$p} = "unused";
							}
						}
					
					}
				}
			else
				{
				my $z = 0;
				# loop over all possible Controller items
				foreach my $XX (@CONTROLLER)
					{
					my $CONT = @{@CONTROLLER[$z]}[0];
					# check if current Controller used by the VM
					if ($CTRL =~ /$CONT/gi)
						{
						# set the matrix of each used Controller
						foreach my $CONTROLLER (@CONTROLLER[$z])
							{
							#my $NAME = "@{$CONTROLLER}[0]:$CONT";
							my $PORT = @{$CONTROLLER}[1];
							my $DEVICE = @{$CONTROLLER}[2];
							
							# loop for "PORT"
							for (my $p=0;$p<$PORT;$p++)
								{
								
								# loop for "PORTDEVICE"
								for (my $d=0;$d<$DEVICE;$d++)
									{
									# update the Controller matrix
									my $KEY = "$CTRL ($p, $d)";
									my $NAME = "$CTRL:$CONT";
									my $pp = sprintf ("%02d",$p);
									if (exists($INFO->{$KEY}))
										{
										$MATRIX->{$NAME}->{$pp}->{$d} = $INFO->{$KEY};
										}
									else
										{
										$MATRIX->{$NAME}->{$pp}->{$d} = "unused";
										}
									}
								
								}
							}
						}
					$z++;
					}
				}
			
			next;
			}
		
		}
	close (XML);
	return $MATRIX;
	}


######################
#
######################
sub GetControllerMatrix_
	{
	
	my $INFO = shift;
	
	# Controller definition
	my @CONTROLLER = (
			['IDE',2,2],
			['SCSI',16,1],
			['SATA',30,1],
			['Disketten',2,1],
			['SAS',8,1],
			);
	
	# Check the INFO Hash for used Controller
	foreach my $DUMMY (sort keys %{$INFO})
		{
		if ($DUMMY =~ /^Storage Controller Name/g)
			{
			my $NAME = $INFO->{$DUMMY};
			$NAME =~ s/^\s+//;# keine führende Whitespaces
			$NAME =~ s/\s+$//;# keine anhängenden Whitespaces
			my $z = 0;
			# loop over all possible Controller items
			foreach my $XX (@CONTROLLER)
				{
				# check if current Controller used by the VM
				if ($NAME =~ /@{@CONTROLLER[$z]}[0]/gi)
					{
					# set the matrix of each used Controller
					foreach my $CONTROLLER (@CONTROLLER[$z])
						{
						my $NAME = @{$CONTROLLER}[0];
						my $PORT = @{$CONTROLLER}[1];
						my $DEVICE = @{$CONTROLLER}[2];
						
						# loop for "PORT"
						for (my $p=0;$p<$PORT;$p++)
							{
							# loop for "PORTDEVICE"
							for (my $d=0;$d<$DEVICE;$d++)
								{
								# update the Controller matrix
								my $KEY = $NAME."-Controller ($p, $d)";
								print "- $KEY -<br>";
								if (exists($INFO->{$KEY}))
									{
									$MATRIX->{$NAME}->{$p}{$d} = $INFO->{$KEY};
									print " used<br>";
									}
								else
									{
									$MATRIX->{$NAME}->{$p}{$d} = "unused";
									print " unused<br>";
									}
								}
							
							}
						}
					}
				$z++;
				}
			}
		}
	return $MATRIX;
	}

sub SetButtons
	{
	my @VISIBLE = split(",",@_[0]);
	my @DATA;
	@TEXT = ("Start","Pause","Resume","Reset","PowerOff","SaveState","acpi");
	$LINE = 0;
	
	foreach my $DUMMY(@VISIBLE)
		{
		push(@DATA, &ui_submit(@TEXT[$LINE], "action",$DUMMY));
		$LINE++;
		
		}
	
	return @DATA;
	
	}


sub GetVMExtradata
	{
	my %VMEXTRADATA;
	my $USER = @_[0];
	my $VM = @_[1];
	
	my $COMMAND;
	
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $USER ";
		}
	
	$COMMAND .= $VBOXBIN."VBoxManage --nologo getextradata \"$VM\" enumerate";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		#print "COMMAND: $COMMAND<br>RETURN: $RETURN<br>";
		}
	my @INFO = split("\n",$RETURN);
	
	foreach my $DUMMY (@INFO)
		{
		#print "'$DUMMY'<br>";
		my ($KEY,$VALUE) = split("," , $DUMMY);
		
		$KEY =~ s/key\://gi;
		$KEY =~ s/^\s+//g;
		$KEY =~ s/\s+$//g;
		$VALUE =~ s/value\://gi;
		$VALUE =~ s/^\s+//g;
		$VALUE =~ s/\s+$//g;
		
		$VMEXTRADATA{$KEY} = $VALUE;
		}
	
	return %VMEXTRADATA;
	}


sub GetVMExtraNICData
	{
	my $USER = @_[0];
	my $VM = @_[1];
	
	my %EXTRA = GetVMExtradata($USER, $VM);
	my %DAT;
	
	foreach $KEY (keys %EXTRA)
		{
		if ($KEY =~ /.*\/LUN.*(.*\/.*port)|.*\/LUN.*(.*\/protocol)/i)
			{
			# NIC
			if ($1)
				{
				my @DUMMY = split("/" , $KEY);
				#print "$LINE '$KEY' -> '$DUMMY[2]' '$DUMMY[3]' '$DUMMY[6]' '$DUMMY[7]'<br>";
				$DAT{$DUMMY[3]}{$DUMMY[6]}{$DUMMY[7]} = "$DUMMY[2]:$EXTRA{$KEY}";
				}
			# Protocol
			elsif($2)
				{
				my @DUMMY = split("/" , $KEY);
				#print "$LINE '$KEY' -> '$DUMMY[2]' '$DUMMY[3]' '$DUMMY[6]' '$DUMMY[7]'<br>";
				$DAT{$DUMMY[3]}{$DUMMY[6]}{$DUMMY[7]} = "$DUMMY[2]:$EXTRA{$KEY}";
				}
			}
		}
	return %DAT;
	}




sub GetVMProperty
	{
	my%VMPROPERTY;
	my $USER = @_[0];
	my $VM = @_[1];
	my $COMMAND;
	
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $USER ";
		}
	$COMMAND .= $VBOXBIN."VBoxManage -q guestproperty enumerate \"$VM\"";
	#print "COMMAND: $COMMAND<br>";
	my $RETURN = readpipe($COMMAND);
	my @INFO = split("\n",$RETURN);
	
	foreach my $DUMMY (@INFO)
		{
		#print "DUMMY2: $DUMMY<br>";
		if ($DUMMY =~ /value\:/)
			{
			my $KEY = $`;
			my $VALUE = $';
			
			$KEY =~ s/name\://gi;
			$KEY =~ s/,//g;
			$KEY =~ s/^\s+//g;
			$KEY =~ s/\s+$//g;
			$VALUE =~ s/^\s+//g;
			$VALUE =~ s/\s+$//g;
			#print "$KEY -> $VALUE<br>";
			$VMPROPERTY{$KEY} = $VALUE;
			}
		
		}
	#%VMPROPERTY = sort keys %VMPROPERTY;
	return %VMPROPERTY;
	}


sub GetOStypes
	{
	my %OSTYPES;
	my $VM = @_[0];
	$COMMAND = $VBOXBIN."VBoxManage --nologo list ostypes";
	#print "COMMAND: $COMMAND<br>";
	my $RETURN = readpipe($COMMAND);
	my @INFO = split("\n",$RETURN);
	
	my ($KEY, $VALUE);
	
	foreach my $DUMMY (@INFO)
		{
		
		if ($DUMMY =~ /ID\:/)
			{
			$KEY = $';
			$KEY =~ s/^\s+//g;
			$KEY =~ s/\s+$//g;
			}
		elsif ($DUMMY =~ /Description\:/)
			{
			$VALUE = $';
			$VALUE =~ s/^\s+//g;
			$VALUE =~ s/\s+$//g;
			#print "'$KEY' --> '$VALUE'<br>";
			$OSTYPES{$KEY} = $VALUE;
			undef ($KEY);
			undef ($VALUE);
			}
		}
	return %OSTYPES;
	}

sub GetVMDesc
	{
	my ($FROM, $TO, $DESCRIPTION);
	my (@XML);
	my $VMXML = shift;
	
	# figure out the description start
	my $COMMAND = "cat $VMXML | grep -in '<description>' ";
	my $RETURN = readpipe($COMMAND);
	
	if ($RETURN =~ /(^[0-9]+)\:?/)
		{
		$FROM = $1;
		# figure out the description end
		my $COMMAND = "cat $VMXML | grep -in \"</description>\" ";
		my $RETURN = readpipe($COMMAND);
		$RETURN =~ /(^[0-9]+)\:?/;
		$TO = $1;
		
		open (XML,"<$VMXML");
		@XML= <XML>;
		close XML;
		
		for ($i=($FROM-1);$i <= ($TO-1);$i++)
			{
			$DESCRIPTION .= @XML[$i];
			}
		
		$DESCRIPTION =~ s/\<description\>//gi;
		$DESCRIPTION =~ s/\<\/description\>//gi;
		$DESCRIPTION =~ s/^\s+//g;
		$DESCRIPTION =~ s/\s+$//g;
		
		}
	return $DESCRIPTION;
	}

sub GetVMInfo
	{
	my $USER = @_[0];
	my $VM = @_[1];
	my %VMINFO;
	my $NIC = 0;
	my $COMMAND;
	
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $USER ";
		}
	
	$COMMAND .= $VBOXBIN."VBoxManage --nologo showvminfo \"$VM\"";
	#print "COMMAND: $COMMAND<br>";
	#my $RETURN = readpipe($COMMAND);
	my @INFO = readpipe($COMMAND);
	#my @INFO = split("\n",$RETURN);
	
	foreach my $DUMMY (@INFO)
		{
		my ($KEY,$VALUE);
		#print "<b>$DUMMY</b><br>";
		if ($DUMMY =~ /\:/)
			{
			$KEY = $`;
			$VALUE = $';
			}
		#print "'$KEY' -> '$VALUE'<br>";
		
		$VALUE =~ s/^\s+//g;
		$VALUE =~ s/\s+$//g;
		
		$VMINFO{$KEY} = $VALUE;
		}
	return %VMINFO;
	}


sub IsVMNIC
	{
	my $USER = @_[0];
	my $VM = @_[1];
	#print "VM: '$VM'<br>";
	my %INFO = GetVMInfo($USER,$VM);
	
	my $NIC = 0;
	
	for ($i=1;$i <= 8;$i++)
		{
		my $DUMMY = "NIC $i";
		#print "NIC $i --> ".$INFO{$DUMMY}."<br>";
		if (! ($INFO{"NIC $i"} =~ /disabled/i) )
			{
			#print "NIC vorhanden !!<br>";
			$NIC = 1;
			}
		}
	
	return $NIC;
	}


sub GetSystemInfo
	{
	my %SYSINFO;
	$COMMAND = $VBOXBIN."VBoxManage --nologo list systemproperties";
	#print "COMMAND: $COMMAND<br>";
	my $RETURN = readpipe($COMMAND);
	my @SYSINFO = split("\n",$RETURN);
	
	foreach my $DUMMY (@SYSINFO)
		{
		#print "DUMMY2: $DUMMY<br>";
		if ($DUMMY =~ /\:/)
			{
			$KEY = $`;
			$VALUE = $';
			}
		#print "$KEY -> $VALUE<br>";
		$SYSINFO{$KEY} = $VALUE;
		}
	return %SYSINFO;
	}

sub StartVM
	{
	my $USER = @_[0];
	my $VM = @_[1];
	
	my $COMMAND;
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $USER ";
		}
	
	# with V4 and higher "-type vrdp" will not longer supported
	# with V4.0.10 the start is only in headless mode possible
	$COMMAND .= $VBOXBIN."VBoxManage --nologo startvm \"$VM\" --type headless 2>&1"; #-type vrdp ";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
		}
	
	my $HASH = \%in;
	$HASH->{'COMMAND'} = $COMMAND;
	$HASH->{'RETURN'} = $RETURN;
	my $ACTION;
	if ($RETURN =~ /error/gi)
		{
		$ACTION = "Start VM with Error";
		}
	else
		{
		$ACTION = "Start VM";
		}
	webmin_log($ACTION,"","'$VM' ($USER)",\%in);
	return $RETURN;
	}


sub StopVM
	{
	my (@STOPMODE) = ("pause","resume","reset","poweroff","savestate","acpipowerbutton");
	my ($USER,$VM,$MODE) = @_;
	
	my $COMMAND;
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $USER ";
		}
	
	$COMMAND .= $VBOXBIN."VBoxManage --nologo controlvm \"$VM\" $STOPMODE[$MODE] 2>&1";
	$RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
		}
	my $HASH = \%in;
	$HASH->{'COMMAND'} = $COMMAND;
	$HASH->{'RETURN'} = $RETURN;
	my $ACTION;
	if ($RETURN =~ /error/gi)
		{
		$ACTION = "Stop VM with Error";
		}
	else
		{
		$ACTION = "Stop VM";
		}
	webmin_log($ACTION,$STOPMODE[$MODE],"'$VM' ($USER)",\%in);
	
	return $RETURN;
	}






=head2 file_basename(name)

Returns the part of a filename after the last /.

=cut
sub file_basename
	{
	local $rv = $_[0];
	$rv =~ s/^.*[\/\\]//;
	return $rv;
	}


#**********************************************************
# erzeugt eine schoene Datums Ausgabe als Rueckgabewert
#**********************************************************
sub cgsdatum 
	{
	($SEK,$MIN,$STD,$MTAG,$MON,$JAHR,$WTAG,$JTAG,$ISDST) = localtime(time);
	$JAHR += 1900;
	$MON++;
	$WOCHENTAG = (qw/So Mo Di Mi Do Fr Sa/)[$WTAG];
	my $cgsdatum = sprintf ("%s %02d.%02d.%4d %02d:%02d:%02d",$WOCHENTAG, $MTAG, $MON,$JAHR,$STD,$MIN,$SEK);
	return ($cgsdatum);
	}

