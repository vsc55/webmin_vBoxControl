#!/usr/bin/perl

use Switch;

require 'vboxctrl-lib.pl';
&ReadParse();

init_config();
$DEBUGMODE = $config{'DEBUGMODE'};
if ($DEBUGMODE)
	{
	DebugOut();
	}

my $VBOXBIN = $config{'PATH_VB_BIN'};
if (! ($VBBOXBIN =~ /\/$/))
	{
	$VBOXBIN .= "/";
	}
@VMHDs = split(/\0/, $in{'vmhd'});

foreach $DUMMY (@VMHDs)
	{
	
	my($USER,$VM,$FILE) = split(":" , $DUMMY);
	
	my ($COMMAND, $return);
	
	# unregistered pool HD?
	if ( ($USER eq "none") && ($VM eq "none") )
		{
		$COMMAND = "rm -f $FILE 2>1&";
		$RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <br><b>RETURN:</b> $RETURN<br>";
			}
		}
	else
		{
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		$COMMAND .= $VBOXBIN."VBoxManage -q closemedium disk $FILE --delete 2>&1 ";
		$RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "<b>COMMAND:</b> $COMMAND - <br><b>RETURN:</b> $RETURN<br>";
			}
		}
	
	my $DUMMY = IsError($RETURN,"Remove HD from media registry");
	$ERR = ($ERR || $DUMMY);
	}

if ($ERR)
	{
	#print ui_print_footer("index.cgi?mode=hdds", $text{'index_return'});
	print ui_print_footer("list_hdds.cgi", $text{'index_return'});
	}
else
	{
	#redirect("index.cgi?mode=hdds");
	redirect("list_hdds.cgi");
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



