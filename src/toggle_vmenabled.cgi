#!/usr/bin/perl

require 'vboxctrl-lib.pl';
&ReadParse();
init_config();

$VMSET = $in{'set'};
$VMCLEAR = $in{'clear'};

$DEBUGMODE = $config{'DEBUGMODE'};
if($DEBUGMODE)
	{
	DebugOut();
	}

my ($STARTUPVM,$A) = ReadEnabledVM();

if ($VMSET)
	{
	#print "TOGGLE: Set -> '$VMSET'<br>";
	$STARTUPVM->{$VMSET} = "toggle2";
	}
elsif ($VMCLEAR)
	{
	#print "TOGGLE: Clear -> '$VMCLEAR'<br>";
	delete($STARTUPVM->{$VMCLEAR});
	}

WriteEnabledVM($STARTUPVM);

redirect("index.cgi?mode=vm");


