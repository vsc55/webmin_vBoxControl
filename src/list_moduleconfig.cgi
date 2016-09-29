#!/usr/bin/perl

require 'vboxctrl-lib.pl';

init_config();
&ReadParse();


$DEBUGMODE = $config{'DEBUGMODE'};
if ($DEBUGMODE)
	{
	DebugOut();
	}

my (@keys);

ui_print_header(undef, $text{'MOD_CONF_VAL'}, "", undef, 1, 1);

my $CONFIG = module_root_directory('vboxctrl').'/config.info';
#print "$CONFIG<br>";


open (MODULECONFIG , $CONFIG);
while (<MODULECONFIG>)
	{
	chomp;	# kein Newline	
	s/#.*//;# keine Kommentare
	s/^\s+//;# keine führende Whitespaces
	s/\s+$//;# keine anhängenden Whitespaces
	next unless length;# noch was da?
	# Sektionen
	#SEP_SVNDEBUG=VBox Manager default options,11,
	my $LINE = $_;
	my $KEY;
	if ( $_ =~ /\=+?/i )
		{
		$KEY = $`;
		$KEY =~ s/\s+$//;# keine anhängenden Whitespaces
		$VAL = $';
		
		if ($VAL =~ /\,11+?/)
			{
			$VAL = "";
			}
		
		if ($VAL)
			{
			$VAL =~ /\,+?/;
			$TXT = $`;
			
			push(@KEYS , "$KEY:$TXT");
			}
		}
	}
close(MODULECONFIG);

my (@TD) = ("width=1%","width=1%");
my (@TABHEAD) = ($text{'TABHEAD_MODCONF_KEY'},$text{'TABHEAD_MODCONF_VAL'});

print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);

foreach my $KEY (sort @KEYS)
	{
	my ($A,$B) = split(":", $KEY);
	my @TABDATA = ($B,$config{$A});
	print ui_columns_row(\@TABDATA,\@TD);
	}
print &ui_columns_end();

#print ui_print_footer("index.cgi?mode=host", $text{'index_return'});

if ($in{'print'})
	{
	print "<script type='text/javascript'>";
	print "window.print();";
	print "</script>";

	}
else
	{
	
	print "<br>";
	print "<a href='#' onclick=\"javascript:window.open('list_moduleconfig.cgi?print=1','popup', 'toolbar=0,width=840, height=600')\">";
	print "<img src='images/printer.png' border='0'></a>";
	print "<br>";
	print ui_print_footer("index.cgi?mode=host", $text{'index_return'});
	}