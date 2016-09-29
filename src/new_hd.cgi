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

my $VBDEFAULTHDPATH = $config{'PATH_VB_DEFAULTHDPATH'};
if (! ($VBDEFAULTHDPATH =~ /\/$/))
	{
	$VBDEFAULTHDPATH .= "/";
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

my $ERR = 0;

if ($in{'new'})
	{
	
	my $VMUSER = $in{'vmuser'};
	#
#	Key: 'hd_ext' -> 'vmdk'
#	Key: 'hd_format' -> 'NT4_Client_DE_SP6:root'
#	Key: 'hd_name' -> 'eff'
#	Key: 'hd_size' -> '5000'
#	Key: 'hd_type' -> 'writetrough'
#	Key: 'hd_variant' -> 'Fixed'
#	Key: 'new' -> 'Create new Harddisk'
#	Key: 'to' -> '0'
#	Key: 'vmbasedir' -> '/'
#	Key: 'vmuser' -> 'ctna005
	
	# Create HD
	my $COMMAND;
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $VMUSER ";
		}
	$COMMAND .= $VBOXBIN."VBoxManage --nologo createhd ";
	
	if ($in{'hd_to'})
		{
		$COMMAND .= "--filename \"$in{'hd_basedir'}/$in{'hd_name'}\" ";
		}
	else
		{
		$COMMAND .= "--filename \"$config{'PATH_VB_DEFAULTHDPATH'}/$in{'hd_name'}\" ";
		}
	
	$COMMAND .= "--size $in{'hd_size'} --format $in{'hd_ext'} --variant $in{'hd_variant'} ";
	$COMMAND .= "2>&1";
	
	my $RETURN = readpipe($COMMAND);
	$REMARK = "$COMMAND ";
	if ($DEBUGMODE)
		{
		print "<b>COMMAND:</b> $COMMAND - <br><b>RETURN:</b> $RETURN<br>";
		}
	
	# Set the needed access rights
	unless ($in{'hd_to'})
		{
		my $FILE = $config{'PATH_VB_DEFAULTHDPATH'}."/".$in{'hd_name'}.".".$in{'hd_ext'};
		# Add the group 'vboxusers' to the new HD
		my $COMMAND = "chgrp vboxusers \"$FILE\" 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <br><b>RETURN:</b> $RETURN<br>";
			}
		
		# set the group access 'vboxusers' to the new HD
		my $COMMAND = "chmod g+rw \"$FILE\" 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <br><b>RETURN:</b> $RETURN<br>";
			}
		}
	
	
	
	my $DUMMY = IsError($RETURN,"PART: Creating HD...");
	$ERR = ($ERR || $DUMMY);
	
	my $HASH = \%in;
	$HASH->{'SYNTAX'} = $REMARK;
	webmin_log("Create","HD","$in{'hd_basedir'}/$in{'hd_name'}",\%in);
	
	if (! $ERR)
		{
		redirect("list_hdds.cgi");
		}
	
	}

ui_print_header(undef, $text{'HD_NEW'}, "", undef, 1, 1);

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

print &ui_form_start("new_hd.cgi", "Post");

print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
my @TABDATA = (
		$text{'INP_USERNAME'},
		" ",
		ui_select("vmuser",$in{'vmuser'},\@VMUSER)
		);
print ui_columns_row(\@TABDATA,\@TD);
my @RADIO = ([0,$text{'HD_POOLDIR'}],[1,$text{'HD_TODIR'}]);
my @TABDATA = (
		$text{'INP_HDPATH'},
		" ",
		&ui_radio("hd_to", ($in{'hd_to'}?$in{'hd_to'}:"0"),\@RADIO)." ".&ui_filebox("hd_basedir",($in{'hd_basedir'}?$in{'hd_basedir'}:"/"), 40,0,50,"hd_basedir",1)
		);
print ui_columns_row(\@TABDATA,\@TD);
print &ui_columns_end();

my @HDEXT = (["vdi","VDI"],["vmdk","VMDK"],["vhd","VHD"]);
my @HDVARIANT = (["Standard","Standard"],["Fixed","Fixed"]);
my (@TD) = (" "," "," "," "," ");
my (@TABHEAD) = ("Harddisk"," "," "," "," ");
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
my @TABDATA = (
		"<img src='images/hdd.png'>",
		"<b>$text{'INP_HDNAME'}</b><br>".ui_textbox("hd_name",($in{'hd_name'}?$in{'hd_name'}:"MyHD"),10),
		"<b>$text{'INP_HDEXTENSION'}</b><br>".ui_select("hd_ext",$in{'hd_ext'},\@HDEXT),
		"<b>$text{'INP_HDTYPE'}</b><br>".ui_select("hd_variant",$in{'hd_variant'},\@HDVARIANT),
		"<b>$text{'INP_HDSIZE'}</b><br>".ui_textbox("hd_size",($in{'hd_size'}?$in{'hd_size'}:"500"),10)." <b>MB</b>"
		);
print ui_columns_row(\@TABDATA,\@TD);

print &ui_columns_end();

print &ui_submit($text{'HD_NEW'}, "new");

print &ui_form_end();


# Ruecksprung zur anfordernden Seite
#print ui_print_footer("index.cgi?mode=hdds", $text{'index_return'});
print ui_print_footer("list_hdds.cgi", $text{'index_return'});

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



