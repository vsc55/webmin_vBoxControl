#!/usr/bin/perl

require 'vboxctrl-lib.pl';
&ReadParse();

my $VM = $in{'vm'};
my $USER = $in{'user'};

init_config();

$DEBUGMODE = $config{'DEBUGMODE'};
if($DEBUGMODE)
	{
	DebugOut();
	}


if ($in{'export'})
	{
	# figure out the natdata
	my %INFO = GetVMInfo($USER,$VM);
	my $XMLFILE = $INFO{'Config file'};
	#print "Config File: $XMLFILE <br>";
	my $VMNAT = Read_NatXML($XMLFILE, 'fh00');
	
	# figure out the extradata
	my %EXTRA = GetVMExtradata($USER,$VM);
	
	# download File 
	if ($in{'source'})
		{
		my $FILENAME = "\"PORTFORWARDING_$VM\.txt\"";
		
		print "Content-type: application/octet-stream\n";
		print "Content-Disposition: attachment; filename=$FILENAME\n";
		print "\n";
		
		print "# Webminmodule '$module_info{'desc'} (V $module_info{'version'})'\n";
		print "# portforwarding rules for VM '$VM'\n";
		print "# created on ".cgsdatum()."\n\n";
		
		for (my $NIC=1; $NIC <= 8; $NIC++)
			{
			foreach my $RULE (keys %{$VMNAT->{$NIC-1}->{'natrule'}})
				{
				my ($PROTOCOL) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'proto'};
				my ($HOSTIP) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'hostip'};
				my ($HOSTPORT) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'hostport'};
				my ($GUESTIP) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'guestip'};
				my ($GUESTPORT) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'guestport'};
				
				print "natpf:$NIC,$RULE,$PROTOCOL,$HOSTIP,$HOSTPORT,$GUESTIP,$GUESTPORT\n";
				}
			}
		
		foreach $KEY (keys %EXTRA)
			{
			if ( ($KEY =~ /port/gi) || ($KEY =~ /protocol/gi) )
				{
				print "Key: $KEY, Value: $EXTRA{$KEY}\n";
				}
			}
		
		webmin_log("Export (Download)","NATRules","'$VM' ($USER)",\%in);
		}
	# local File
	else
		{
		
		&ui_print_header(undef, $text{'EXPORT_VMEXTRATITLE'}." '$VM'", "");
		
		my $TARGETDIR = $in{'file'};
		# Expand with '/'
		if (! ($TARGETDIR =~ /\/$/))
			{
			$TARGETDIR .= "/";
			}
		
		# targetdir exists ??
		if (! (-e $TARGETDIR))
			{
			&ui_print_header(undef, $text{'EXPORT_VMEXTRATITLE'}." '$VM'", "");
			print "<b>",text('EXPORT_VMEXTRAERRDIR'," <tt>'$TARGETDIR'</tt>"),"</b><p>\n";
			&ui_print_footer("vmextra_export.cgi?vm=$VM", $text{'EXPORT_VMEXTRATITLE'});
			$ERR = 1;
			}
		else
			{
			$TARGETDIR .= "PORTFORWARDING_$VM.txt";
			
			open (EXTRA , "> $TARGETDIR");
			print EXTRA "# Webminmodule '$module_info{'desc'} (V $module_info{'version'})'\n";
			print EXTRA "# portforwarding rules for VM '$VM'\n";
			print EXTRA "# created on ".cgsdatum()."\n\n";
			
			#my %GETNATPF = GetNATPF($USER,$VM);
			for (my $NIC=1; $NIC <= 8; $NIC++)
				{
				
				foreach my $RULE (keys %{$VMNAT->{$NIC-1}->{'natrule'}})
					{
					my ($PROTOCOL) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'proto'};
					my ($HOSTIP) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'hostip'};
					my ($HOSTPORT) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'hostport'};
					my ($GUESTIP) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'guestip'};
					my ($GUESTPORT) = $VMNAT->{$NIC-1}->{'natrule'}->{$RULE}->{'guestport'};
					
					print EXTRA "natpf:$NIC,$RULE,$PROTOCOL,$HOSTIP,$HOSTPORT,$GUESTIP,$GUESTPORT\n";
					}
				}
			
			
			foreach $KEY (keys %EXTRA)
				{
				#print "'$KEY' --> '$EXTRA{$KEY}<br>";
				if ( ($KEY =~ /port/gi) || ($KEY =~ /protocol/gi) )
					{
					print EXTRA "Key: $KEY, Value: $EXTRA{$KEY}\n";
					}
				}
			close(EXTRA);
			
			&ui_print_header(undef, $text{'EXPORT_VMEXTRATITLE'}." '$VM'", "");
			print "<b>",&text('EXPORT_VMEXTRADONE', "<tt>$TARGETDIR</tt>"),"</b><p>\n";
			&ui_print_footer("forward_vm.cgi?vm=$VM&user=$USER", $text{'PORTFORWARD_VM'});
			webmin_log("Export (local file)","NATRules","'$VM' ($USER)",\%in);
			}
		}
	}
else
	{
	&ui_print_header(undef, $text{'EXPORT_VMEXTRATITLE'}." '$VM'", "");
	print &ui_form_start("vmextra_export.cgi","post");
	print &ui_table_start($text{'TABHEADER_EXTRAEXPORT'}, undef, 2);
	print ui_hidden("export",1);
	print ui_hidden("vm",$VM);
	print ui_hidden("user",$USER);
	my @ROW;
	#push(@ROW, [ 0, $text{'EXPORT_VMEXTRALOCALFILE'},&ui_textbox("file", undef, 40) ]);
	
	push(@ROW, [ 0, $text{'EXPORT_VMEXTRALOCALFILE'},&ui_filebox("file", "/", 40,0,50,"file",1) ]);
	#print "<tr><td>".&ui_radio("to", 0,\@RADIO)."</td><td>".&ui_filebox("file_tgz", "/", 40,0,50,"file_tgz",1)."</td></tr>";
	
	push(@ROW, [ 1, $text{'EXPORT_VMEXTRAFILE'}," "]);
	print &ui_table_row($text{'EXPORT_VMEXTRASOURCE'},&ui_radio_table("source", 1,\@ROW));
	
	print &ui_table_end();
	print &ui_form_end([ [ "ok", $text{'EXPORT_VMEXTRAOK'} ] ]);
	&ui_print_footer("forward_vm.cgi?vm=$VM&user=$USER", $text{'PORTFORWARD_VM'});
	}


