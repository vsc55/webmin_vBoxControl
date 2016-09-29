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

ui_print_header(undef, $text{'VM_DHCPSERVERS'}, "", undef, 1, 1);


if ($in{'update'})
	{
	#print "UPDATE!!<br>";
	
	my $NETWORKNAME = $in{'NWN'};
	my $ENABLED = $in{'ENABLED'};
	my $IP = $in{'IP'};
	my $NETWORKMASK = $in{'NWM'};
	my $LOWERIP = $in{'LIP'};
	my $UPPERIP = $in{'UIP'};
	
	$COMMAND = $VBOXBIN."VBoxManage -q dhcpserver modify --netname \"$NETWORKNAME\" --ip $IP --netmask $NETWORKMASK ";
	$COMMAND .= "--lowerip $LOWERIP --upperip $UPPERIP ";
	if ($ENABLED eq "Yes")
		{
		$COMMAND .= "--enable ";
		}
	else
		{
		$COMMAND .= "--disable ";
		}
	
	$COMMAND .= " 1>&2";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
		}
	
	my $HASH = \%in;
	$HASH->{'COMMAND'} = $COMMAND;
	$HASH->{'RETURN'} = $RETURN;
	webmin_log("Modify","DHCP server","'$NETWORKNAME'",\%in);
	
	if ($RETURN)
		{
		print "<font color='red'><b>$RETURN</b></font> <p>\n";
		}
	}

my @DHCPSERVERS = GetDHCPServers();


my (@TD) = ("width=1%","width=1%");
my (@TABHEAD) = ($text{'tabhead_dhcpservers'},$text{'tabhead_dhcpserversdesc'});

print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
foreach my $DUMMY (@DHCPSERVERS)
	{
	
	my $NETWORKNAME = ${$DUMMY}{'NetworkName'};
	my $ENABLED = ${$DUMMY}{'Enabled'};
	my $IP = ${$DUMMY}{'IP'};
	my $NETWORKMASK = ${$DUMMY}{'NetworkMask'};
	my $LOWERIP = ${$DUMMY}{'lowerIPAddress'};
	my $UPPERIP = ${$DUMMY}{'upperIPAddress'};
	my $IFNAME = $NETWORKNAME;
	$IFNAME =~ s/hostinterfacenetworking\-//i;
	
	print &ui_form_start("edit_dhcpservers.cgi", "Post","_self","name=$IFNAME");
	
	print ui_columns_row(["<b>$IFNAME</b>".ui_hidden("NWN",$NETWORKNAME)],["colspan=2 align=center"]);
	print ui_columns_row(["Network Name",$NETWORKNAME],\@TD);
	print ui_columns_row(["Enabled",ui_select("ENABLED",$ENABLED,[["No","No"],["Yes","Yes"]])],\@TD);
	print ui_columns_row(["IP",ui_textbox("IP",$IP,13)],\@TD);
	print ui_columns_row(["Network Mask",ui_textbox("NWM",$NETWORKMASK,13)],\@TD);
	print ui_columns_row(["Lower IP-Address",ui_textbox("LIP",$LOWERIP,13)],\@TD);
	print ui_columns_row(["Upper IP-Address",ui_textbox("UIP",$UPPERIP,13)],\@TD);
	print ui_columns_row([&ui_submit($text{'dhcpserver_update'}, "update")],["colspan=2 align=center"]);
	
	print &ui_form_end();
	
#	my @TABDATA = (
#	
#	foreach my $KEY (sort keys %{$DUMMY})
#		{
#		#print "$KEY --> ${$DUMMY}{$KEY}<br>";
#		my @TABDATA = ($KEY,${$DUMMY}{$KEY});
#		
#		}
	
	print ui_columns_row([" "],["colspan=2"]);
	}
print &ui_columns_end();

print ui_print_footer("index.cgi?mode=host", $text{'index_return'});


