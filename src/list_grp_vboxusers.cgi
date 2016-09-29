#!/usr/bin/perl

require 'vboxctrl-lib.pl';
&ReadParse();
init_config();

$DEBUGMODE = $config{'DEBUGMODE'};
if ($DEBUGMODE)
	{
	DebugOut();
	}

my $COMMAND = "cat /etc/group | grep -i -n vboxusers";
my $RETURN = readpipe($COMMAND);
if ($DEBUGMODE)
	{
	print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
	}
my @DUMMY = split(":" , $RETURN);
my $GROUPID = @DUMMY[3];
my $GROUPLINE =  @DUMMY[0] -1;
my @VBOXUSERS = split("," , @DUMMY[4]);


my $TEXT = $text{'VM_VBOXUSERS'};
if ($in{'print'})
	{
	$TEXT .= " (".get_system_hostname().")";
	}
ui_print_header(undef, $TEXT, "", undef, 1, 1);

my (@TD) = (
		"width=1%",
		"width=1%",
		"width=1%",
		"width=1%",
		"width=1%",
		"width=1%"
		);
my (@TABHEAD) = (
		$text{'tabhead_vboxusers_group'},
		$text{'tabhead_vboxusers_groupid'},
		$text{'tabhead_vboxusers_user'},
		$text{'tabhead_vboxusers_userid'},
		$text{'tabhead_vboxusers_remark'},
		$text{'tabhead_vboxusers_home'}
		);


print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);

foreach my $USER (sort @VBOXUSERS)
	{
	my $COMMAND = "cat /etc/passwd | grep -i -n $USER";
	my $RETURN = readpipe($COMMAND);
	if ($DEBUGMODE)
		{
		print "<br><b>COMMAND:</b> $COMMAND - <b>RETURN:</b> $RETURN<br>";
		}
	my @DUMMY = split(":" , $RETURN);
	
	my @TABDATA = (
			"<a href='../useradmin/edit_group.cgi?num=$GROUPLINE'>vboxusers</a>",
			"<a href='../useradmin/edit_group.cgi?num=$GROUPLINE'>$GROUPID</a>",
			"<a href='../useradmin/edit_user.cgi?num=".(@DUMMY[0] - 1)."'>$USER</a>",
			"<a href='../useradmin/edit_user.cgi?num=".(@DUMMY[0] - 1)."'>@DUMMY[3]</a>",
			"<a href='../useradmin/edit_user.cgi?num=".(@DUMMY[0] - 1)."'>@DUMMY[5]</a>",
			"<a href='../useradmin/edit_user.cgi?num=".(@DUMMY[0] - 1)."'>@DUMMY[6]</a>",
			);
	print ui_columns_row(\@TABDATA,\@TD);
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
	print "<a href='#' onclick=\"javascript:window.open('list_grp_vboxusers.cgi?print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a> <br>";
	print ui_print_footer("index.cgi?mode=host", $text{'index_return'});
	}


