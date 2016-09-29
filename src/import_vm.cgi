#!/usr/bin/perl
# install_mod.cgi
# Copied and modify from 'install_mod.cgi' WebMin Main Modules

use WebminCore;
use File::Basename;

init_config();
require 'vboxctrl-lib.pl';

my $VBOXBIN = $config{'PATH_VB_BIN'};
if (! ($VBBOXBIN =~ /\/$/))
	{
	$VBOXBIN .= "/";
	}

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
if ($DEBUGMODE)
	{
	DebugOut();
	}

my $USER;
my @VMs;

my $IMPORTMODE = $in{'to'};
my $UPLOADFILE = $in{'upload_filename'};
my $UPLOADDATA = $in{'upload'};
my $USER = $in{'imp_user'};
my $TGZFILE = $in{'file_tgz'};
my $OVAFILE = $in{'file_ova'};
my $ERR = 0;


#output autoflash
$| = 1;

&ui_print_header(undef, $text{'IMPORT_TITLE'}, "");

my $TEMPDIR = GetTempDir();
if (! (-e $TEMPDIR))
	{
	$COMMAND .= "mkdir $TEMPDIR 2>&1";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
		}
	}

# Mode Local *.tgz File
if ($IMPORTMODE == 1)
	{
	if ($DEBUGMODE)
		{
		print "Mode: Local *.tgz File<br>";
		print "Local tgz<br>";
		print "Used TempDir: $TEMPDIR<br>";
		}
	
	&error_setup(&text('IMPORT_ERR', $TGZFILE));
	
	if (!(-r $TGZFILE))
		{
		&inst_error($text{'IMPORT_ERRNOFILE'});
		$ER = 1;
		}
	else
		{
		
		if (!&has_command("gunzip") && !&has_command("gzip"))
			{
			return &text('IMPORT_ERRGZIP1', "<tt>gunzip</tt>");
			}
		
		$COMMAND = "tar -xvf \"$TGZFILE\" -C \"$TEMPDIR\" 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			$RETURN =~ s/\n/<br>/g;
			print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		$COMMAND = "find \"$TEMPDIR\" | grep .ova 2>&1";
		my @RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> @RETURN<br>";
			}
		
		foreach my $OVA (sort @RETURN)
			{
			$BASE = basename($OVA);
			$DIR = dirname($OVA);
			
			$OVA =~ s/^\s+//;# delete leading Whitespaces
			$OVA =~ s/\s+$//;# delete appended Whitespaces
			
			if ($DIR =~ /$TEMPDIR/gi)
				{
				$USER = $';
				$USER =~ s/^\///g;
				}
			
			if ($DEBUGMODE)
				{
				print "TEMPDIR: $TEMPDIR<br>";
				print "DIR: $DIR<br>";
				print "BASE: $BASE<br>";
				print "OVA: '$OVA'<br>";
				print "USER: $USER<br>";
				}
			
			
			push(@VMs , "$USER:$OVA");
			}
		webmin_log("Import (local *.tgz)","VM"," ",\%in);
		}
	}
# Mode Local *.ova File
elsif ($IMPORTMODE == 2)
	{
	if ($DEBUGMODE)
		{
		print "Local *.ova<br>";
		}
	
	&error_setup(&text('IMPORT_ERR', $OVAFILE));
	if (!(-r $OVAFILE))
		{
		&inst_error($text{'IMPORT_ERRNOFILE'});
		$ERR = 1;
		}
	else
		{
		my $COMMAND;
		if ($config{'multiuser'})
			{
			push (@VMs , "$USER:$OVAFILE");
			}
		else
			{
			push (@VMs , ":$OVAFILE");
			}
		
		webmin_log("Import (local *.ova)","VM"," ",\%in);
		}
	}
# Mode Upload *.tgz
else
	{
	if ($DEBUGMODE)
		{
		print "Upload tgz<br>";
		print "Used TempDir: $TEMPDIR<br>";
		}
	
	&error_setup($text{'IMPORT_ERRUPLOAD'});
	
	if ($no_upload)
		{
		&inst_error($text{'IMPORT_ERRBROWSER'});
		}
	else
		{
		$file = "$TEMPDIR/$UPLOADFILE";
		open(MOD, ">$file");
		binmode(MOD);
		print MOD $UPLOADDATA;
		close(MOD);
		
		#print "'$file' ready.<br>";
		
		$COMMAND = "tar -xvzf $file -C \"$TEMPDIR\" 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			$RETURN =~ s/\n/<br>/g;
			print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
			}
		
		$COMMAND = "find \"$TEMPDIR\" | grep .ova";
		my @RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "<hr>cmd: $COMMAND<br>";
			}
		
		foreach my $OVA (sort @RETURN)
			{
			$BASE = basename($OVA);
			$DIR = dirname($OVA);
			
			$OVA =~ s/^\s+//;# delete leading Whitespaces
			$OVA =~ s/\s+$//;# delete appended Whitespaces
			
			if ($DIR =~ /$TEMPDIR/gi)
				{
				$USER = $';
				$USER =~ s/^\///g;
				}
			
			if ($DEBUGMODE)
				{
				print "TEMPDIR: $TEMPDIR<br>";
				print "DIR: $DIR<br>";
				print "BASE: $BASE<br>";
				print "OVA: '$OVA'<br>";
				print "USER: $USER<br>";
				}
			
			push(@VMs , "$USER:$OVA");
			}
		
		webmin_log("Import (upload *.tgz)","VM"," ",\%in);
		}
	}



foreach my $OVA (sort @VMs)
	{
	my ($USER, $OVAFILE) = split(":" , $OVA);
	
	my $COMMAND;
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $USER ";
		}
	$COMMAND .= $VBOXBIN."VBoxManage -q import \"$OVAFILE\" 2>&1";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		$RETURN =~ s/\n/<br>/g;
		print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
		}
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

&ui_print_footer("index.cgi?mode=vm", $text{'IMPORT_RETURN'});

sub inst_error
	{
	print "<b>$main::whatfailed : $_[0]</b> <p>\n";
	&ui_print_footer("", $text{'IMPORT_TITLE'});
	exit;
	}




