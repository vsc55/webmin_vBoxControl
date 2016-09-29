#!/usr/bin/perl

require 'vboxctrl-lib.pl';
init_config();

if ($ENV{REQUEST_METHOD} eq "POST")
	{
	&ReadParseMime();
	}
else
	{
	&ReadParse();
	$no_upload = 1;
	}

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

my $USER = $in{'user'};
my $VM = $in{'vm'};
my $DUMMY;

my $CMD_MULTIUSER;

if ($config{'multiuser'})
	{
	$CMD_MULTIUSER = "sudo -H -u $USER ";
	}
else
	{
	$CMD_MULTIUSER = "";
	}


if ($in{'import'})
	{
	# check the selected source
	# select local file
	if ($in{'source'} == 0)
		{
		&error_setup(&text('IMPORT_EXTRAERR', $in{'file'}));
		$file = $in{'file'};
		# check if file exist
		if (!(-r $file))
			{
			&ui_print_header(undef, $text{'IMPORT_VMEXTRATITLE'}, "");
			print "<b>$main::whatfailed : </b> <p>\n";
			&ui_print_footer("forward_vm.cgi?vm=$VM", $text{'PORTFORWARD_VM'});
			$ERR = 1;
			}
		webmin_log("Import (local file)","NATRules","'$VM' ($USER)",\%in);
		}
	
	# select uploaded file
	elsif ($in{'source'} == 1)
		{
		&error_setup($text{'IMPORT_ERREXTRAUPLOAD'});
		$need_unlink = 1;
		if ($no_upload)
			{
			&inst_error($text{'IMPORT_ERRBROWSER'});
			}
		$file = &transname(&file_basename($in{'upload_filename'}));
		#print"Save File to: $file<br>";
		
		# HINT !!!
		# After finished the script, the dowloaded file will be automtically
		# delete from the /tmp/.webmin directory
		open(EXTRA, ">$file");
		binmode(EXTRA);
		print EXTRA $in{'upload'};
		close(EXTRA);
		
		webmin_log("Import (Upload file)","NATRules","'$VM' ($USER)",\%in);
		}
	#&ui_print_header(undef, undef, "");
	print "Content-type: text/html"."\n\n";
	print "<html><body>";
	print "<br><br><br><br><br><center><img src='images/boxguy.gif'></center>";
	
	#print "FILE: $file<br>";
	open(EXTRA, "$file");
	while (<EXTRA>)
		{
		
		chomp;	# no newline
		s/^#.*//;# no comments
		s/^\s+//;# no starting whitespaces
		s/\s+$//;# no ending whitespaces
		next unless length;# noch was da?
		
		print "<b>'$_'</b><br>";
		
		# rules via natpf
		if ($_ =~ /^natpf/i)
			{
			#print "natpf rule found<br>";
			my ($NATPF,$VALUE) = split(":" , $_);
			
			print "$NATPF,$VALUE";
			
			my %VALUE;
			my @VALUES = split("," , $VALUE);
#			foreach my $DUMMY(@VALUES)
#				{
#				my ($KEY,$VALUE) = split("=" , $DUMMY);
#				$VALUE{$KEY} = $VALUE;
#				}
			my ($NIC) = @VALUES[0];
			my ($RULE) = @VALUES[1];
			my ($PROTOCOL) =  @VALUES[2];
			my ($HOSTIP) =  @VALUES[3];
			my ($HOSTPORT) =  @VALUES[4];
			my ($GUESTIP) =  @VALUES[5];
			my ($GUESTPORT) =  @VALUES[6];
			
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage --nologo modifyvm \"$VM\" ";
			$COMMAND .= "--natpf$NIC $RULE,$PROTOCOL,$HOSTIP,$HOSTPORT,$GUESTIP,$GUESTPORT";
			my $RETURN = readpipe($COMMAND);
			if($DEBUGMODE)
				{
				print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
				}
			$DUMMY = IsError($RET,"PART: $KEY");
			$ERR = ($ERR || $DUMMY);
			
			}
		# rules via extradata
		elsif ($_ =~ /^key\: /i)
			{
			#print "extradata rule found<br>";
			my ($KEY,$VALUE) = split("," , $_);
			
			$KEY =~ s/key\://gi;
			$KEY =~ s/^\s+//g;
			$KEY =~ s/\s+$//g;
			$VALUE =~ s/value\://gi;
			$VALUE =~ s/^\s+//g;
			$VALUE =~ s/\s+$//g;
			
			my $COMMAND = $CMD_MULTIUSER;
			$COMMAND .= $VBOXBIN."VBoxManage --nologo setextradata \"$VM\" ";
			$COMMAND .= " \"$KEY\" $VALUE";
			my $RET = readpipe($COMMAND);
			if($DEBUGMODE)
				{
				print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
				}
			$DUMMY = IsError($RET,"PART: $KEY");
			$ERR = ($ERR || $DUMMY);
			}
		}
	close(EXTRA);
	
	if ($ERR)
		{
		#
		}
	else
		{
		if (! $DEBUGMODE)
			{
			print "<script type=\"text/javascript\">";
			#print "setTimeout(\"self.location.href='forward_vm.cgi?vm=$VM'\",5);";
			print "window.location=\"forward_vm.cgi?vm=$VM&user=$USER\";";
			print "</script>";
			}
		}
	}

&ui_print_header(undef, $text{'IMPORT_VMEXTRATITLE'}." '$VM'", "");

print &ui_form_start("vmextra_import.cgi?vm=$VM&user=$USER","form-data");
print &ui_table_start($text{'TABHEADER_EXTRAIMPORT'}, undef, 2);
print ui_hidden("import",1);
print ui_hidden("vm",$VM);
print ui_hidden("user",$USER);
my @ROW;
push(@ROW, [ 0, $text{'IMPORT_VMEXTRALOCALFILE'},&ui_textbox("file", undef, 40)." ".&file_chooser_button("file", 0) ]);
push(@ROW, [ 1, $text{'IMPORT_VMEXTRAFILE'},&ui_upload("upload", 40) ]);
print &ui_table_row($text{'IMPORT_VMEXTRASOURCE'},&ui_radio_table("source", 1,\@ROW));

print &ui_table_end();
print &ui_form_end([ [ "ok", $text{'IMPORT_VMEXTRAOK'} ] ]);
&ui_print_footer("forward_vm.cgi?vm=$VM&user=$USER", $text{'PORTFORWARD_VM'});


#########################################
#
#########################################
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


