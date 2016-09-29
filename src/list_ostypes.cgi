#!/usr/bin/perl

require 'vboxctrl-lib.pl';

init_config();
$DEBUGMODE = $config{'DEBUGMODE'};
if ($DEBUGMODE)
	{
	DebugOut();
	}

ui_print_header(undef, $text{'VM_OSTYPES'}, "", undef, 1, 1);

my %OSTYPES = GetOStypes();

my (@TD) = ("width=1%","width=1%");
my (@TABHEAD) = ($text{'tabhead_ostypes'},$text{'tabhead_ostypesdesc'});

print &ui_columns_start(\@TABHEAD, 100, 0, \@TD);

foreach my $KEY (sort keys %OSTYPES)
	{
	my @TABDATA = ($KEY,$OSTYPES{$KEY});
	print ui_columns_row(\@TABDATA,\@TD);
	}
print &ui_columns_end();

print ui_print_footer("index.cgi?mode=host", $text{'index_return'});