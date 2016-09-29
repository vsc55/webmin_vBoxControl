#!/usr/bin/perl
# Copied and modify from 'export_mod.cgi' WebMin Main Modules

use File::stat;
use File::Basename

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

my $ERR = 0;
my $ERROR = "";

my $EXPORTMODE = $in{'to'};
my $TARGETTGZDIR = $in{'file_tgz'};
my $TARGETOVADIR = $in{'file_ova'};



# get Tempdir 
my $TEMPDIR = GetTempDir();

# gnerate temp tar pre-name
my $TAR_PRENAME = transname();
$TAR_PRENAME = file_basename($TAR_PRENAME);
$TAR_PRENAME =~ s/export_vm.cgi//g;

&error_setup($text{'EXPORT_ERROR'});
@VMs = split(/\0/, $in{'vms'});

@VMs || &error($text{'NO_VM'});

# Make sure we have the needed commands
&has_command("tar") || &error(&text('EXPORT_ERRCMD', "<tt>tar</tt>"));
&has_command("gzip") || &error(&text('EXPORT_ERRCMD', "<tt>gzip</tt>"));



# Expand with '/'
if (! ($TARGETTGZDIR =~ /\/$/))
	{
	$TARGETTGZDIR .= "/";
	}
if (! ($TARGETOVADIR =~ /\/$/))
	{
	$TARGETOVADIR .= "/";
	}

# set the tar archivname
if (@VMs eq "1")
	{
	my ($A,$B) = split(":" , @VMs[0]);
	$EXPORTFILE = "VirtualBox_".$B;
	}
else
	{
	$EXPORTFILE = "VirtualBox_VMs";
	}

#if EXPORTODE > 0 then print the HTML Header for logmessages, other one for upload
if ($EXPORTMODE)
	{
	&ui_print_header(undef, $text{'EXPORT_TITLE'}, "");
	}
else
	{
	print "Content-type: application/octet-stream\n";
	print "Content-Disposition: attachment; filename=\"$EXPORTFILE\.tgz\"\n";
	print "\n";
	}


if ($DEBUGMODE)
	{
	print "<b>TEMPDIR:</b> $TEMPDIR<br>";
	print "<b>TAR_PRENAME:</b> $TAR_PRENAME<br>";
	print "<b>TARGETTGZDIR:</b> $TARGETTGZDIR<br>";
	print "<b>TARGETOVADIR:</b> $TARGETOVADIR<br>";
	print "<b>EXPORTFILE:</b> $EXPORTFILE<br>";
	}


# set TempDir for MultiUser and modify the ACL
if ($config{'multiuser'})
	{
	# check if TempDir via mudul Config set
	if (! (-e $config{'vboxexport'}))
		{
		$ERROR .= "<b>",$text{'EXPORT_ERREXPORTDIR'},"</b><p>\n";
		$ERR = 1;
		}
	else
		{
		# create Tempdir
		$RETURN = mkdir($TEMPDIR);
		if (! $RETURN)
			{
			$ERROR .= "Error creating directory '$TMPDIR'<br>";
			$ERR = 1;
			}
		$RETURN = mkdir("$TEMPDIR/VM");
		if (! $RETURN)
			{
			$ERROR .= "Error creating directory '$TMPDIR/VM'<br>";
			$ERR = 1;
			}
		# change group from root to vboxusers
		$COMMAND = "chgrp -R vboxusers $TEMPDIR 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		
		# change tempdir mode
		$COMMAND = "chmod -R 770 $TEMPDIR 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		}
	
	}

# check if no problem exist
if (! $ERR)
	{
	
	my ($USER,$VM);
	
	# export all VMs to the tempdir
	# sort the VMs for each user
	my %USERVM;
	foreach my $DUMMY (@VMs)
		{
		($USER,$VM) = split(":" , $DUMMY);
		$USERVM{$USER} .= " \"$VM\" ";
		#print "$USER $VM $USERVM{$USER} <br>";
		}
	
	# create a subdirectory and export a VM for each user
	foreach my $EXPUSER (sort keys %USERVM)
		{
		#print "<b><i>Prepare VMExport $EXPUSER => $USERVM{$EXPUSER}</i></b><br>";
		
		my $DUMMYUSERDIR = "$TEMPDIR/VM/$EXPUSER";
		
		# create a user subdir
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $EXPUSER ";
			}
		$COMMAND .= "mkdir $DUMMYUSERDIR 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		
		# export VMs for every user
		my $COMMAND;
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $EXPUSER ";
			}
		$COMMAND .= $VBOXBIN."VBoxManage -q export $USERVM{$EXPUSER} ";
		$COMMAND .= "--output \"$DUMMYUSERDIR"."/VirtualBoxExport.ova\" 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			$RETURN =~ s/\n/<br>/g;
			print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		}
	
	# Here start the Exportmodes
	# Save *.tgz to the selected Targetdir
	if ($EXPORTMODE == 1)
		{
		
		# create *.tgz archive
		$COMMAND = "tar -cvzf \"$TARGETTGZDIR$EXPORTFILE\.tgz\" -C \"$TEMPDIR/VM/\" . 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		
		if ($DEBUGMODE)
			{
			print "<p><b>Delete manual the directory '<b>$TEMPDIR</b>'.</p>";
			}
		else
			{
			$COMMAND = "rm -fr $TEMPDIR 2>&1";
			my $RETURN = readpipe($COMMAND);
			}
		
		print "<b>",&text('EXPORT_DONE', "<tt>$TARGETTGZDIR$EXPORTFILE\.tgz</tt>"),"</b><p>\n";
		
		webmin_log("Export (local *.tgz)","VM"," ",\%in);
		
		&ui_print_footer("index.cgi?mode=export", $text{'EXPORT_RETURN'});
		}
	
	# Save *.ova to the selected Targetdir
	elsif ($EXPORTMODE == 2)
		{
		my $ACTION;
		my $COMMAND;
		$COMMAND = "mv -f $TEMPDIR/* \"$TARGETOVADIR\" 2>&1";
		$RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		
		if ($RETURN)
			{
			print "<font color=red><b>ERROR: $RETURN</b></font><br>";
			$ACTION = "Export with Errors (local *.ova)";
			}
		else
			{
			
			$COMMAND = "rm -fr $TEMPDIR 2>&1";
			if ($DEBUGMODE)
				{
				print "<p><b>Delete manual the directory '<b>$TEMPDIR</b>'.</p>";
				}
			else
				{
				$COMMAND = "rm -fr $TEMPDIR 2>&1";
				my $RETURN = readpipe($COMMAND);
				}
			print "<b>",&text('EXPORT_DONE', ":<tt>$TARGETOVADIR</tt>"),"</b><p>\n";
			$ACTION = "Export (local *.ova)";
			}
		
		webmin_log($ACTION,"VM"," ",\%in);
		
		&ui_print_footer("index.cgi?mode=export", $text{'EXPORT_RETURN'});
		}
	#Download file
	else
		{
		#print "Content-type: application/octet-stream\n";
		#print "Content-Disposition: attachment; filename=\"$EXPORTFILE\.tgz\"\n";
		#print "\n";
		
		if ($DEBUGMODE)
			{
			print "<br>";
			
			}
		
		#tar cvf me.tar /VBoxExport/395422_1_export_vm/*
		
		# create *.tgz archive
		$COMMAND = "tar cvzf \"$TEMPDIR/$EXPORTFILE\.tgz\" -C \"$TEMPDIR/VM/\" . 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			$RETURN =~ s/\n/<br>/g;
			print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		
		if ($DEBUGMODE)
			{
			print "<p><b>Normally would send the Exportfile '$TEMPDIR/$EXPORTFILE\.tgz</b>'</p>";
			
			}
		else
			{
			open(TEMP, "$TEMPDIR/$EXPORTFILE\.tgz");
			while(<TEMP>) {
				print $_;
				}
			close(TEMP);
			}
		
		webmin_log("Export (download)","VM"," ",\%in);
		
		if ($DEBUGMODE)
			{
			print "<p><b>Delete manual the directory '<b>$TEMPDIR</b>'.</p>";
			}
		else
			{
			$COMMAND = "rm -fr $TEMPDIR 2>&1";
			my $RETURN = readpipe($COMMAND);
			}
		
		}
	}
else
	{
	print $EERROR;
	}

