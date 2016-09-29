# log_parser.pl
# Functions for parsing this module's logs

do 'vboxctrl-lib.pl';

# parse_webmin_log(user, script, action, type, object, &params)
# Converts logged information from this module into human-readable form
sub parse_webmin_log
	{
#	my $Z = 0;
#	foreach my $DUMMY (sort @_)
#		{
#		print "#$Z '$DUMMY'<br>";
#		if ($DUMMY =~ /hash/i)
#			{
#			foreach my $KEY (sort keys %{$DUMMY})
#				{
#				print "   '$KEY' => '${$DUMMY}{$KEY}'<br>";
#				}
#			}
#		$Z++;
#		}
#	print "<hr>";
	local ($user, $script, $action, $type, $object, $p, $long) = @_;
	if ($action eq 'deletes')
		{
		# Deleting multiple jobs
		return &text('log_deletes', $object);
		}
	else
		{
		# Some action on a job
		local @files = split(/\t+/, $p->{'files'});
		local $files = @files > 1 ? scalar(@files)." files" : join(", ", @files);
		local @servers = split(/\s+/, $p->{'servers'});
		local $servers = scalar(@servers);
		return &text('log_'.$action, $files, $servers);
		}
	}

