#!/usr/bin/perl

use Switch;
require 'vboxctrl-lib.pl';
&ReadParse();


my $TEXT = $text{'VM_VMS'};
$TEXT .= "<br>(".get_system_hostname().")";

ui_print_header(undef, $TEXT, "", undef, 1, 1);

print "<script type='text/javascript'>";
print "window.print();";
print "</script>";

my ($STARTUPVM,$ERROR) = ReadEnabledVM();
my $STARTUPUSER = GetStartupUser();

my @VMS = ListAllVM();
my @VRDP;

my (@TD) = (
		"align='center'",
		"align='center'",
		"align='center'",
		"align='center'",
		"align='center'",
		"align='center'"
		);
my (@TABHEAD) = (
		$text{'tabhead_account'},
		$text{'tabhead_vm'},
		$text{'tabhead_vmvrdp'},
		$text{'tabhead_vmos'},
		$text{'tabhead_vmstate'},
		$text{'tabhead_currentuser'}
		);

#my (@linksrow) = ("<a href='new_vm.cgi'>$text{'VM_NEW'}</a>");

#print &ui_links_row(\@linksrow);
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);

foreach my $DUMMY (sort @VMS)
	{
	
	($USER,$DUMMY) = split(":" , $DUMMY);
	#print "Form: $formno - index.cgi<br>";
	print &ui_form_start("index.cgi", "post");
	my %VMINFO = GetVMInfo($USER,$DUMMY);
	my %VMPROP=GetVMProperty($USER,$DUMMY);
	
	my ($PRODUCT, $USERS);
	
	my $STATE = $VMINFO{'State'};
	
	if (exists $VMPROP{'/VirtualBox/GuestInfo/OS/Product'})
		{
		$PRODUCT = $VMPROP{'/VirtualBox/GuestInfo/OS/Product'};
		if ($PRODUCT =~ /\,/)
			{
			$PRODUCT = $`;
			}
		}
	else
		{
		$PRODUCT = "-";
		}
	
	if (exists $VMPROP{'/VirtualBox/GuestInfo/OS/LoggedInUsersList'})
		{
		$USERS = $VMPROP{'/VirtualBox/GuestInfo/OS/LoggedInUsersList'};
		if ($USERS =~ /timestamp/i)
			{
			$USERS = $`;
			$USERS =~ s/, //;
			}
		}
	
	my ($VRDEPORT, $VRDPAUTH);
	my $LINE = $VMINFO{'VRDE'};
	my ($VRDE,$B) = split(" " , $LINE);
	$VRDE =~ s/\(//;
	$VRDE =~ s/\s//;
	$VRDE =($VRDE eq "enabled")?1:0;
	
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
				#$VRDEPORT ="($VRDEPORT)";
				}
			elsif ($DUMMY3 =~ /address/gi)
					{
					$VRDEIP = $';
					$VRDEIP =~ s/\s//;
					}
			}
		}
	
	if ($VRDE)
		{
		$VRDEIPPORT = "($VRDEIP:$VRDEPORT)";
		}
	else
		{
		$VRDEIPPORT = "";
		}
	
	$X = "";
	if ( (! $ERROR) && ($STARTUPUSER eq $USER) )
		{
		if (exists $STARTUPVM->{$DUMMY})
			{
			my $TITLE = text('VM_DISABLE',$DUMMY,$config{'FILE_VM_ENABLED'});
			$VM_EN_TXT = "<a href='toggle_vmenabled.cgi?clear=$DUMMY' title='$TITLE'><img src='images/not.gif3.png' border='0'></a>";
			}
		else
			{
			my $TITLE = text('VM_ENABLE',$DUMMY,$config{'FILE_VM_ENABLED'});
			$VM_EN_TXT = "<a href='toggle_vmenabled.cgi?set=$DUMMY' title='$TITLE'><img src='images/down.gif.png' border='0'></a>";
			}
		}
	
	
	my (@TABDATA, @DUMMY2);
	push (@TABDATA, "<b>$USER</b>");
	push (@TABDATA, "$DUMMY<br>$VM_EN_TXT");
	push (@TABDATA, "<img src='images/vrde".($VRDP?"_on":"_off").".gif' border='0'></a><br>$VRDEIPPORT");
	push (@TABDATA, $VMINFO{'Guest OS'});
	
	switch($STATE)
		{
		$STATE =~ /\(/;
		
		case /running/
			{
			push(@TABDATA,"<image src='images/up.gif.png' alt='$text{'img_on'}'><br>$`");
			}
		case /powered off/
			{
			push(@TABDATA,"<image src='images/down.gif.png' alt='$text{'img_off'}'><br>$`");
			}
		case /saved/
			{
			push(@TABDATA,"<image src='images/down.gif.png' alt='$text{'img_off'}'><br>$`");
			}
		case /paused/
			{
			push(@TABDATA,"<image src='images/paused.gif' alt='$text{'img_off'}'><br>$`");
			}
		case /restoring/
			{
			push(@TABDATA,"<image src='images/up.gif.png' alt='$text{'img_on'}'><br>$`");
			}
		case /starting/
			{
			push(@TABDATA,"<image src='images/up.gif.png' alt='$text{'img_on'}'><br>$`");
			}
		default:
			{
			push(@TABDATA,"<image src='images/blank.gif'><br>$`");
			}
		}
	
	#window.confirm('Link folgen?');
	
	#push (@TABDATA, &ui_submit($text{'vmdel_title'}, "delete"));
	#push (@TABDATA ,"&nbsp;<a href='#' onclick=\"return ConfirmDelete('".$USER."','".$DUMMY."');\"><img src='images/trash.png' border='0'></a>&nbsp;");
	push (@TABDATA, $USERS);
	
	print ui_columns_row(\@TABDATA,\@TD);
	
	print &ui_form_end();
	
	}

print &ui_columns_end();
#print &ui_links_row(\@linksrow);


	