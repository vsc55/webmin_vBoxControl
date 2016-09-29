#!/usr/bin/perl

use Data::Dumper;
use Switch;
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

my $ERR = 0;
my $VM = $in{'vm'};
my $USER = $in{'user'};

my %CONTROLLER = ('IDE'=>'IDE-Controller','SCSI'=>'SCSI-Controller','SATA'=>'SATA-Controller','SAS'=>'SAS-Controller');

my $TEXT = text('HDD4VM',$VM);
ui_print_header(undef, $TEXT, "", undef, 1, 1);

if (exists($in{'attach'}))
	{
	my @DEV = split(/\0/, $in{'ADD'});
	foreach my $DEV (@DEV)
		{
		my ($CONTROLLER,$PORT,$DEVICE) = split(":" , $in{'DEV_'.$DEV});
		my $HD = $in{'DEV_'.$DEV.'HD'};
		my $TYPE = $in{'MTYPE_'.$DEV};
		
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		$COMMAND .= $VBOXBIN."VBoxManage -q storageattach \"$VM\" --storagectl \"$CONTROLLER\" --port $PORT ";
		$COMMAND .= "--device $DEVICE --type hdd --mtype $TYPE --medium \"$HD\" 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "COMMAND: $COMMAND - <br>RETURN: $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"Attach HD $CONTROLLER:$PORT:$CTRL:$HD");
		$ERR = ($ERR || $DUMMY);
		}
	}
elsif (exists($in{'detach'}))
	{
	my @SELECT = split(/\0/, $in{'SELECT'});
	foreach my $IDX (@SELECT)
		{
		
		my ($CONTROLLER,$PORT,$DEVICE) = split(":" , $in{'DEVICE_OLD_'.$IDX});
		
		
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		$COMMAND .= $VBOXBIN."VBoxManage -q storageattach \"$VM\" --storagectl \"$CONTROLLER\" --port $PORT ";
		$COMMAND .= "--device $DEVICE --medium none 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "COMMAND: $COMMAND - <br>RETURN: $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"Detach HD $CONTROLLER:$PORT:$CTRL");
		$ERR = ($ERR || $DUMMY);
		}
	}
elsif (exists($in{'update'}))
	{
	my @SELECT = split(/\0/, $in{'SELECT'});
	foreach my $IDX (@SELECT)
		{
		
		my ($CONTROLLER,$PORT,$DEVICE) = split(":" , $in{'DEVICE_OLD_'.$IDX});
		my ($NEWPORT,$NEWDEVICE) = split(":" , $in{'DEVICE_'.$IDX});
		my $FILE = $in{'PATH_'.$IDX};
		
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		# First detach the HD from the current connection
		$COMMAND .= $VBOXBIN."VBoxManage -q storageattach \"$VM\" --storagectl \"$CONTROLLER\" --port $PORT ";
		$COMMAND .= "--device $DEVICE --medium none 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "COMMAND: $COMMAND - <br>RETURN: $RETURN<br>";
			}
		my $DUMMY = IsError($RETURN,"Step1: Detach HD $CONTROLLER:$PORT:$CTRL");
		
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		# Second attach the HDto the new connection
		$COMMAND .= $VBOXBIN."VBoxManage -q storageattach \"$VM\" --storagectl \"$CONTROLLER\" --port $NEWPORT ";
		$COMMAND .= "--device $NEWDEVICE --type hdd --medium \"$FILE\" 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "COMMAND: $COMMAND - <br>RETURN: $RETURN<br>";
			}
		$DUMMY .= IsError($RETURN,"Step2: Attach HD $CONTROLLER:$NEWPORT:$NEWCTRL:$FILE");
		
		$ERR = ($ERR || $DUMMY);
		}
	}
elsif (exists($in{'add'}))
	{
	if ($in{'SELECT'} && $in{'FREECTRL'})
		{
		my $SHORT = $in{'FREECTRL'};
		my $LONG = $CONTROLLER{$SHORT};
		
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		$COMMAND .= $VBOXBIN."VBoxManage -q storagectl \"$VM\" --name \"$LONG\" --add $SHORT 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "COMMAND: $COMMAND - <br>RETURN: $RETURN<br>";
			}
		$DUMMY .= IsError($RETURN,"Step2: Attach HD $CONTROLLER:$NEWPORT:$NEWCTRL:$FILE");
		
		$ERR = ($ERR || $DUMMY);
		}
	}
elsif (exists($in{'delete'}))
	{
	my $SHORT = $in{'ADD'};
	if ($SHORT)
		{
		my ($CONTROLLER,$PORT,$DEVICE) = split(":" , $in{'DEV_'.$SHORT});
		
		if ($config{'multiuser'})
			{
			$COMMAND = "sudo -H -u $USER ";
			}
		
		$COMMAND .= $VBOXBIN."VBoxManage -q storagectl \"$VM\" --name \"$CONTROLLER\" --remove 2>&1";
		my $RETURN = readpipe($COMMAND);
		if ($DEBUGMODE)
			{
			print "COMMAND: $COMMAND - <br>RETURN: $RETURN<br>";
			}
		$DUMMY .= IsError($RETURN,"Step2: Attach HD $CONTROLLER:$NEWPORT:$NEWCTRL:$FILE");
		
		$ERR = ($ERR || $DUMMY);
		}
	}



my $TEXT = text('HDD4VM',$VM);
if ($in{'print'})
	{
	$TEXT .= " (".get_system_hostname().")<br>($USER)";
	}


my %DEVICENAME;
my (@FD,@IDE,@SCSI,@SATA,@SAS);
my (@FD_FREE,@IDE_FREE,@SCSI_FREE,@SATA_FREE,@SAS_FREE);



#foreach my $KEY (sort keys %CONTROLLER)
#	{
#	print "'$KEY' => '$CONTROLLER{$KEY}'<br>";
#	}

my %VMINFO = GetVMInfo($USER,$VM);
my $MATRIX = GetControllerMatrix(\%VMINFO);

$DEVICENAME{'FD,00,0'} = "Floppy Device 0";
$DEVICENAME{'FD,00,1'} = "Floppy Device 1";
$DEVICENAME{'IDE,00,0'} = "IDE Primary Master";
$DEVICENAME{'IDE,00,1'} = "IDE Primary Slave";
$DEVICENAME{'IDE,01,0'} = "IDE Secundary Master";
$DEVICENAME{'IDE,01,1'} = "IDE Secundary Slave";

#*****************************************
# Fill the hash for all and free devices
#*****************************************
foreach my $CTRL (sort keys %{$MATRIX})
	{
	my ($LONG,$SHORT) = split(":" , $CTRL);
	
	# Delete allready used controller
	delete $CONTROLLER{$SHORT};
	
	foreach my $PORT (sort keys %{$MATRIX->{$CTRL}})
		{
		my $PPORT = $PORT *1;
		
		foreach my $DEV (sort keys %{$MATRIX->{$CTRL}->{$PORT}})
			{
			#print "$LONG($SHORT) => $PORT => CTRL -> ".$MATRIX->{$CTRL}->{$PORT}->{$DEV}."<br>";
			switch ($SHORT)
				{
				case "FD"
					{
					if ($MATRIX->{$CTRL}->{$PORT}->{$DEV} eq "unused")
						{
						push(@FD,["$LONG:$PPORT:$DEV",$DEVICENAME{"$SHORT,$PORT,$DEV"}]);
						push(@FD_FREE,["$LONG:$PPORT:$DEV",$DEVICENAME{"$SHORT,$PORT,$DEV"}]);
						}
					else
						{
						push(@FD,["$PPORT:$DEV",$DEVICENAME{"$SHORT,$PORT,$DEV"}." *"]);
						}
					}
				case "IDE"
					{
					if ($MATRIX->{$CTRL}->{$PORT}->{$DEV} eq "unused")
						{
						push(@IDE,["$PPORT:$DEV",$DEVICENAME{"$SHORT,$PORT,$DEV"}]);
						push(@IDE_FREE,["$LONG:$PPORT:$DEV",$DEVICENAME{"$SHORT,$PORT,$DEV"}]);
						}
					else
						{
						push(@IDE,["$PPORT:$DEV",$DEVICENAME{"$SHORT,$PORT,$DEV"}." *"]);
						}
					}
				else
					{
					if ($MATRIX->{$CTRL}->{$PORT}->{$DEV} eq "unused")
						{
						my $eval = "push(\@".$SHORT.", ['$PPORT:$DEV','$SHORT Port $PPORT'])";
						eval($eval);
						my $eval = "push(\@".$SHORT."_FREE, ['$LONG:$PPORT:$DEV','$SHORT Port $PPORT'])";
						eval($eval);
						}
					else
						{
						my $eval = "push(\@".$SHORT.", ['$PPORT:$DEV','$SHORT Port $PPORT *'])";
						eval($eval);
						}
					}
				}
			}
		}
	}


#print Dumper(\@SATA)."<br>";
#print Dumper(\@SATA_FREE)."<br>";

#*****************************************
# Create the Form for all Connections
#*****************************************
my $INDEX = 0;
my @USEDHDDS;
print &ui_form_start("edit_hdds4vm.cgi", "post");

print ui_hidden("vm",$VM);
print ui_hidden("user",$USER);

my (@TD) = ("align='left'");
my (@TABHEADDESCR) = ($text{'tabhead_hd_controller_descr'});
print &ui_columns_start(\@TABHEADDESCR, 100, 0, \@TD);
print &ui_columns_end();

my (@TD) = ("width='1%'","width='20%'","width='*'","width='5%'");
my (@TABHEAD) = ("",$text{'tabhead_hd_controller'},$text{'tabhead_hd'}," ");
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
foreach my $CTRL (sort keys %{$MATRIX})
	{
	foreach my $PORT (sort keys %{$MATRIX->{$CTRL}})
		{
		my $PPORT = $PORT *1;
		my ($LONG,$SHORT) = split(":" , $CTRL);
		
		foreach my $DEV (sort keys %{$MATRIX->{$CTRL}->{$PORT}})
			{
			#print "$CTRL -> $PORT -> $DEV => $MATRIX->{$CTRL}->{$PORT}->{$DEV}<br>";
			
			if (! ($MATRIX->{$CTRL}->{$PORT}->{$DEV} eq "unused") )
				{
				
				my @DUMMY;
				switch($SHORT)
					{
					case "FD"
						{
						#@DUMMY = @FD;
						}
					case "IDE"
						{
						@DUMMY = @IDE;
						}
					case "SCSI"
						{
						
						@DUMMY = @SCSI;
						}
					case "SATA"
						{
						@DUMMY = @SATA;
						}
					case "SAS"
						{
						@DUMMY = @SAS;
						}
					}
				
				my ($FILENAME, $PATH, $TEXT);
				my $HD = $MATRIX->{$CTRL}->{$PORT}->{$DEV};
				
				if ($HD =~ / \(/g)
					{
					$FILENAME = $`;
					$FILENAME = basename($FILENAME);
					$PATH = dirname($HD);
					$PATH =~ s/^\s+//g;
					$TEXT = "<b>$FILENAME (<i>$PATH</i>)</b>";
					}
				else
					{
					$FILENAME = $HD;
					$TEXT = "<b>$FILENAME</b>";
					$PATH = "";
					}
				if (! ($SHORT eq "FD"))
					{
					if ($FILENAME =~ /\.iso$/i)
						{
						my @TABDATA;
						foreach my $ARRAY (@DUMMY)
							{
							#print "Huhu=> '@{$ARRAY}[0]' '$PPORT:$DEV'<br>";
							if ( @{$ARRAY}[0] =~ /^$PPORT\:$DEV/ )
								{
								@TABDATA = (
										" ",
										"<b><i>@{$ARRAY}[1]</i></b>",
										$TEXT,
										" "
										);
								}
							}
						print ui_columns_row(\@TABDATA,\@TD);
						
						}
					else
						{
						if (! ($FILENAME =~ /\.iso$/i) )
							{
							push(@USEDHDDS , "$PATH"."/".$FILENAME);
							}
						
						my @TABDATA = (
							ui_hidden("DEVICE_OLD"."_$INDEX","$LONG:$PPORT:$DEV").
							ui_select("DEVICE"."_$INDEX","$PPORT:$DEV",\@DUMMY),
							ui_hidden("PATH"."_$INDEX",$PATH."/".$FILENAME).$TEXT,
							" "
							);
							#print ui_checked_columns_row(\@TABDATA,\@TD,"SELECT_"."$SHORT,$PORT,$DEV","$LONG");
							print ui_checked_columns_row(\@TABDATA,\@TD,"SELECT","$INDEX");
						}
					
					
					
#					my @TABDATA = (
#							ui_hidden("DEVICE_OLD"."_$INDEX","$LONG:$PPORT:$DEV").
#							ui_select("DEVICE"."_$INDEX","$PPORT:$DEV",\@DUMMY),
#							ui_hidden("PATH"."_$INDEX",$PATH."/".$FILENAME).$TEXT,
#							" "
#							);
#					#print ui_checked_columns_row(\@TABDATA,\@TD,"SELECT_"."$SHORT,$PORT,$DEV","$LONG");
#					print ui_checked_columns_row(\@TABDATA,\@TD,"SELECT","$INDEX");
					$INDEX++;
					}
				}
			}
		}
	}
print &ui_columns_end();
print &ui_submit($text{'hd_update_title'}, "update"),&ui_submit($text{'hd_detach_title'}, "detach"),"<br>\n";
print &ui_form_end();

#*****************************************
# Create the Form for Free Connections
# Collect all free HDs 
#*****************************************
my @FREEHD;
my %HDDS = ListHDDS();
foreach my $KEY (sort keys %HDDS)
	{
	my ($USER,$VM,$FILE) = split(":" , $KEY);
	#print "$USER,$VM,$FILE<br>";
	
	if ($VM eq "none")
		{
		#print "=> $USER,$VM,$FILE<br>";
		my $FILENAME = basename($FILE);
		my $PATH = dirname($FILE);
		push(@FREEHD , ["$FILE","$FILENAME ($PATH)"]);
		}
	}

print &ui_form_start("edit_hdds4vm.cgi", "post");
print ui_hidden("vm",$VM);
print ui_hidden("user",$USER);

my (@TD) = ("align='left'");
my (@TABHEADDESCR) = ($text{'tabhead_hd_connection_descr'});
print &ui_columns_start(\@TABHEADDESCR, 100, 0, \@TD);
print &ui_columns_end();

my (@TD) = ("width='1%'","width='20%'","width='20%'","width='*'");
my (@TABHEAD) = ("",$text{'tabhead_hd_controller_port'},$text{'tabhead_hd_writemode'},$text{'tabhead_free_hd'});
my @MTYPE = (["normal","Normal"],["writethrough","Write Through"]);
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
#if (@FD_FREE)
#	{
#	my @TABDATA = (
#			ui_select("DEV_FD","",\@FD_FREE),
#			"",
#			"",
#			);
#	print ui_checked_columns_row(\@TABDATA,\@TD,'ADD',"FD");
#	}
if (@IDE_FREE)
	{
	my @TABDATA = (
			ui_select("DEV_IDE","",\@IDE_FREE),
			ui_select("MTYPE_IDE","",\@MTYPE),
			ui_select("DEV_IDEHD","",\@FREEHD),
			);
	print ui_checked_columns_row(\@TABDATA,\@TD,'ADD',"IDE");
	}
if (@SAS_FREE)
	{
	my @TABDATA = (
			ui_select("DEV_SAS","",\@SAS_FREE),
			ui_select("MTYPE_SAS","",\@MTYPE),
			ui_select("DEV_SASHD","",\@FREEHD),
			);
	print ui_checked_columns_row(\@TABDATA,\@TD,'ADD',"SAS");
	}
if (@SATA_FREE)
	{
	my @TABDATA = (
			ui_select("DEV_SATA","",\@SATA_FREE),
			ui_select("MTYPE_SATA","",\@MTYPE),
			ui_select("DEV_SATAHD","",\@FREEHD),
			);
	print ui_checked_columns_row(\@TABDATA,\@TD,'ADD',"SATA");
	}
if (@SCSI_FREE)
	{
	my @TABDATA = (
			ui_select("DEV_SCSI","",\@SCSI_FREE),
			ui_select("MTYPE_SCSI","",\@MTYPE),
			ui_select("DEV_SCSIHD","",\@FREEHD),
			);
	print ui_checked_columns_row(\@TABDATA,\@TD,'ADD',"SCSI");
	}

print &ui_columns_end();
print &ui_submit($text{'hd_attach_title'},"attach"),&ui_submit($text{'ctrl_delete_title'},"delete")."<br>\n";
print &ui_form_end();


#*****************************************
# Create the Form for Free Controller
#*****************************************
print &ui_form_start("edit_hdds4vm.cgi", "post");
print ui_hidden("vm",$VM);
print ui_hidden("user",$USER);

my (@TD) = ("align='left'");
my (@TABHEADDESCR) = ($text{'tabhead_add_controller_descr'});
print &ui_columns_start(\@TABHEADDESCR, 100, 0, \@TD);
print &ui_columns_end();

my (@TD) = ("width='1%'","width='20%'","width='5%'","width='*'");
my (@TABHEAD) = ("",$text{'tabhead_hd_controller'}," "," "," ");
print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
my (@FREECONTROLLER);
foreach my $KEY (sort keys %CONTROLLER)
	{
	push(@FREECONTROLLER , [$KEY,$CONTROLLER{$KEY}]);
	}
my @TABDATA = (
		ui_select("FREECTRL","",\@FREECONTROLLER),
		"",
		"",
		"",
		);
print ui_checked_columns_row(\@TABDATA,\@TD,"SELECT","1");
print &ui_columns_end();
print &ui_submit($text{'ctrl_add_title'}, "add"),"<br>\n";
print &ui_form_end();


#*******************************************
# Print out the properties of each used HDD
#*******************************************

my (@TD) = ("width='*'","width='*'");
my (@TABHEAD) = ($text{'tabhead_hdspec'},$text{'tabhead_hdspecdesc'});

my (@TD) = ("align='left'");
my (@TABHEADDESCR) = ($text{'tabhead_hdinfo_descr'});
print &ui_columns_start(\@TABHEADDESCR, 100, 0, \@TD);
print &ui_columns_end();

print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);
my $HD = 1;

foreach my $FILE (@USEDHDDS)
	{
	my %HDINFO = GetHDInfo($USER,$FILE);
	#print "=> $FILE<br>";
	print ui_columns_row(["<b> HDD #$HD </b>"],["colspan='2'"]);
	foreach my $KEY (sort keys %HDINFO)
		{
		#print "$KEY -> $HDINFO{$KEY}<br>";
		my @TABDATA = ($KEY,$HDINFO{$KEY});
		print ui_columns_row(\@TABDATA,\@TD);
		}
	print ui_columns_row([" "],["colspan='2'"]);
	$HD++;
	}
print &ui_columns_end();

if ($in{'print'})
	{
	print "<script type='text/javascript'>";
	print "window.print();";
	print "</script>";
	}
else
	{
	print "<br>";
	print "<a href='#' onclick=\"javascript:window.open('list_hdds4vm.cgi?vm=$VM&user=$USER&print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a> <br>";
	print ui_print_footer("index.cgi?mode=vm", $text{'index_return'});
	}

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

