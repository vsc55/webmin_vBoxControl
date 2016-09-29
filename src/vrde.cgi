#!/usr/bin/perl

require 'vboxctrl-lib.pl';
&ReadParse();
init_config();

my $VM = $in{'vm'};
my $USER = $in{'user'};

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

if ($in{'GO'})
	{
	
	my @AUTH = ("null","external","guest");
	$PARAMETER = "--vrde ".($in{'vrde'}?"on":"off")." --vrdeport $in{'vrdeport'} --vrdeauthtype $in{'vrdeauth'} ";
	$PARAMETER .= "--vrdemulticon ".($in{'vrdemulti'}?"on":"off")." ";
	
	if ($in{'vrdeip'})
		{
		$PARAMETER .= "--vrdeaddress $in{'vrdeip'} ";
		}
	else
		{
		$PARAMETER .= "--vrdeaddress 0.0.0.0 ";
		}
	
	my $COMMAND;
	if ($config{'multiuser'})
		{
		$COMMAND = "sudo -H -u $USER ";
		}
	
	$COMMAND .= $VBOXBIN."VBoxManage --nologo modifyvm \"$VM\" $PARAMETER 2>&1";
	my $RETURN = readpipe($COMMAND);
	
	if ($DEBUGMODE)
		{
		print "COMMAND: $COMMAND - RETURN: $RETURN<br>";
		}
	
	my $HASH = \%in;
	$HASH->{'COMMAND'} = $COMMAND;
	$HASH->{'RETURN'} = $RETURN;
	webmin_log("Modify","VRDE settings","'$VM' ($USER)",\%in);
	
	#print "<hr>$COMMAND<hr>$RETURN<hr>";
	my $ERR = IsError($RETURN," ");
	if ($ERR)
		{
		#
		}
	else
		{
		redirect("index.cgi?mode=vm");
		}
	}

ui_print_header(undef, "$text{'VRDE'} '$in{'vm'}'", "", undef, 1, 1);

my %DATA =GetVMExtraNICData($USER, $VM);


my %VMINFO = GetVMInfo($USER,$VM);

my ($VRDEIP, $VRDEPORT, $VRDEAUTH);
my $LINE = $VMINFO{'VRDE'};
my ($VRDE,$B) = split(" " , $LINE);
$VRDE =~ s/\(//;
$VRDE =~ s/\s//;
$VRDE =($VRDE eq "enabled")?1:0;

#If VRDE, then figure out Port and the Login Method
if ($VRDE)
	{
	$LINE =~ /.*(\(.*\))/g;
	$LINE = $1;
	$LINE =~ s/\(//;
	$LINE =~ s/\)//;
	
	@VRDE = split(", " , $LINE);
	
	foreach my $DUMMY3 (@VRDE)
		{
		if ($DUMMY3 =~ /ports/gi)
			{
			$VRDEPORT = $';
			$VRDEPORT =~ s/\s//;
			}
		elsif ($DUMMY3 =~ /Authentication type\:/gi)
			{
			$VRDEAUTH = $';
			$VRDEAUTH =~ s/\s//;
			}
		elsif ($DUMMY3 =~ /address/gi)
			{
			$VRDEIP = $';
			$VRDEIP =~ s/\s//;
			}
		}
	}

#print "$DUMMY <b>$VRDP $VRDPPORT $VRDPAUTH</b><br>";

print &ui_form_start("vrde.cgi", "Post");
print ui_hidden("GO","1");
print ui_hidden("vm",$in{'vm'});
print ui_hidden("user",$in{'user'});
my (@TD) = ("width='25%'"," "," ");
my (@TABHEAD) = ("VRDE"," "," ");
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
my @TABDATA = ("<b>$text{'INP_VRDE'}</b>"," ",ui_select("vrde",($VRDE?1:0),[[0,"No"],[1,"Yes"]]));
print ui_columns_row(\@TABDATA,\@TD);
my @TABDATA = ("<b>$text{'INP_VRDEIP'}</b>"," ",ui_textbox("vrdeip",$VRDEIP,14));
print ui_columns_row(\@TABDATA,\@TD);
my @TABDATA = ("<b>$text{'INP_VRDEPORT'}</b>"," ",ui_textbox("vrdeport",($VRDEPORT?$VRDEPORT:"3389"),5));
print ui_columns_row(\@TABDATA,\@TD);
my @TABDATA = ("<b>$text{'INP_VRDEAUTH'}</b> "," ",ui_select("vrdeauth",($VRDEAUTH?$VRDEAUTH:"1"),[["null","Null"],["external","External"],["guest","Guest"]]));
print ui_columns_row(\@TABDATA,\@TD);
my @TABDATA = ("<b>$text{'INP_VRDEMULTI'}</b>"," ",ui_select("vrdemulti",($VRDE?1:0),[[0,"No"],[1,"Yes"]]));
print ui_columns_row(\@TABDATA,\@TD);
print &ui_columns_end();
print &ui_submit($text{'vrde_title'}, "update");
print &ui_form_end();

print ui_print_footer("index.cgi?mode=vm", $text{'index_return'});


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


