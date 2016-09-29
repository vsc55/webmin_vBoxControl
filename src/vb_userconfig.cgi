#!/usr/bin/perl

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

if ($in{'save'})
	{
	my $PRECOMMAND;
	if ($config{'multiuser'})
		{
		$PRECOMMAND = "sudo -H -u $in{'user'} ";
		}
	
	my $COMMAND = $PRECOMMAND.$VBOXBIN."VBoxManage -q setproperty machinefolder \"".$in{'mfolder'}."\" 2>&1";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "COMMAND: $COMMAND - <br>RETURN: $RETURN<br>";
		}
	
	my $COMMAND = $PRECOMMAND.$VBOXBIN."VBoxManage -q setproperty vrdeauthlibrary \"".$in{'vrdelib'}."\" 2>&1";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "COMMAND: $COMMAND - <br>RETURN: $RETURN<br>";
		}
	
	my $COMMAND = $PRECOMMAND.$VBOXBIN."VBoxManage -q setproperty websrvauthlibrary \"".$in{'weblib'}."\" 2>&1";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "COMMAND: $COMMAND - <br>RETURN: $RETURN<br>";
		}
	
	my $COMMAND = $PRECOMMAND.$VBOXBIN."VBoxManage -q setproperty vrdeextpack \"".$in{'extpack'}."\" 2>&1";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "COMMAND: $COMMAND - <br>RETURN: $RETURN<br>";
		}
	
	my $COMMAND = $PRECOMMAND.$VBOXBIN."VBoxManage -q setproperty loghistorycount ".$in{'histcount'}." 2>&1";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "COMMAND: $COMMAND - <br>RETURN: $RETURN<br>";
		}
	
	webmin_log("VB User Settings","update"," (".$in{'user'}.")",\%in);
	
	}

my $TEXT = $text{'VM_USERSETTINGS'};
if ($in{'print'})
	{
	$TEXT .= " (".get_system_hostname().")";
	}
ui_print_header(undef, $TEXT, "", undef, 1, 1);

my $SYSPROPS = GetSystemProperties();

foreach my $USER (sort keys %{$SYSPROPS})
	{
	my (@TD) = ("width=8%","width=30%");
	my (@TABHEAD) = ("User $USER","");
	
	print &ui_form_start("vb_userconfig.cgi", "Post");
	print ui_hidden("user",$USER);
	print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
	
	my $TXT = "Default machine folder";
	#my @TABDATA = ("<b>$TXT:</b>" , ui_textbox('mfolder', $SYSPROPS->{$USER}->{$TXT}, 50));
	my @TABDATA = ("<b>$TXT:</b>" , ui_filebox('mfolder', $SYSPROPS->{$USER}->{$TXT}, 50,0,300,"",1));
	print ui_columns_row(\@TABDATA,\@TD);
	
	my $TXT = "VRDE auth library";
	my @TABDATA = ("<b>$TXT:</b>", ui_textbox('vrdelib', $SYSPROPS->{$USER}->{$TXT}, 50));
	print ui_columns_row(\@TABDATA,\@TD);
	
	my $TXT = "Webservice auth. library";
	my @TABDATA = ("<b>$TXT:</b>", ui_textbox('weblib', $SYSPROPS->{$USER}->{$TXT}, 50));
	print ui_columns_row(\@TABDATA,\@TD);
	
	my $TXT = "Remote desktop ExtPack";
	my @TABDATA = ("<b>$TXT:</b>", ui_textbox('extpack', $SYSPROPS->{$USER}->{$TXT}, 50));
	print ui_columns_row(\@TABDATA,\@TD);
	
	my $TXT = "Log history count";
	my @TABDATA = ("<b>$TXT:</b>", ui_textbox('histcount', $SYSPROPS->{$USER}->{$TXT}, 50));
	print ui_columns_row(\@TABDATA,\@TD);
	
	
	print &ui_columns_end();
	print "<br><br>";
	if (! ($in{'print'}) )
		{
		print &ui_submit(' Save ', "save")." ".&ui_submit(' Cancel ', "cancel");
		}
	print &ui_form_end();
	print "<br>";
	}

if ($in{'print'})
	{
	print "<script type='text/javascript'>";
	print "window.print();";
	print "</script>";
	}
else
	{
	print "<br>";
	print "<a href='#' onclick=\"javascript:window.open('vb_userconfig.cgi?print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a> <br>";
	print ui_print_footer("index.cgi?mode=host", $text{'index_return'});
	}



