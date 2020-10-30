package GenModel;

use strict;
use DBI;
use GenError;
use DbConfig;
use Data::Dumper;
use Benchmark;
use CGI::Carp;

sub new
{
	my $class = shift;
	my $self  = {}; 
	$self->{PARMS} = shift;
	$self->{ROWCOUNT} = ();
	bless ($self,$class);
	return $self;
}

sub genSQL
{
	my $self = shift();
	if (ref $_[0] eq 'SessionObject') {
		my $sessObj = shift;
		my %requestParms = %{$self->{PARMS}};
		my $page = defined $requestParms{page} ?  $requestParms{page} : 1 ;
		my $rowsPerPage = $requestParms{rowsPerPage} if defined $requestParms{rowsPerPage};
		$rowsPerPage = $rowsPerPage || 30;
		$self->{ROWCOUNT} = scalar(@{$sessObj->{DATA}});
		my $data = ();
		my $i = 0;
		my $j = 0;

		my $sqlStr = "SELECT ta_number, firm_symbol, limit_price, order_quantity, original_order_datetime from orders WHERE  ta_number in ( ";

		my $totRows = scalar(@{$sessObj->{DATA}});

	  	if ($page > 1) {
			$i = --$page * $rowsPerPage;
			$j = ++$page * $rowsPerPage;
			$j = $j > $totRows ? $totRows : $j; 
		} else {
			$i = 0;
			$j = $rowsPerPage;  
		}
		

		print STDERR (Dumper($sessObj));
				
		$data = $sessObj->{DATA}->[$i];

		$sqlStr .= " '$data' ";

		for(++$i; $i < $j; $i++) {
			$data = $sessObj->{DATA}->[$i];
			$sqlStr .= ", '$data'"; 
		}


                if ((not defined $sessObj->{SORT}) || ($sessObj->{SORT} =~ /^\s*$/))
                {
                        $sqlStr .= " ) ORDER BY limit_price ASC, order_quantity  ";
                }
                else
                {

                        if ($sessObj->{SORT} eq "SORT_PRICE_DESC")
                        {
                                $sqlStr .= " )  ORDER BY limit_price DESC, order_quantity ";
                        }
                        elsif ($sessObj->{SORT} eq "SORT_PRICE_ASC")
                        {
                                $sqlStr .= " )  ORDER BY limit_price ASC, order_quantity ";
                        }
                        elsif ($sessObj->{SORT} eq "SORT_ORDER_ASC")
                        {
                                $sqlStr .= " )  ORDER BY order_quantity ASC, limit_price ";
                        }
                        elsif ($sessObj->{SORT} eq "SORT_ORDER_DESC")
                        {
                                $sqlStr .= " )  ORDER BY order_quantity DESC, limit_price ";
                        }
                        elsif ($sessObj->{SORT} eq "SORT_DATE_DESC")
                        {
                                $sqlStr .= " )  ORDER BY original_order_datetime DESC, limit_price ";
                        }
                        elsif ($sessObj->{SORT} eq "SORT_DATE_ASC")
                        {
                                $sqlStr .= " )  ORDER BY original_order_datetime ASC, limit_price ";
                        }

                }


		$self->{SQLSTR} = $sqlStr;
		carp("$self->{SQLSTR} : SESSIONOBJECTSQL");

	} else {
                my %requestParms = %{$self->{PARMS}};

                my $sqlStr = "SELECT ta_number from orders WHERE ";
                $sqlStr   .= " stock_symbol = " . "'". $requestParms{stkName} . "'";
                $sqlStr   .= " AND limit_price >= " . $requestParms{minPrice}  if ($requestParms{minPrice} || $requestParms{minPrice} eq 0);
                $sqlStr   .= " AND limit_price <= " . $requestParms{'maxPrice'}  if ($requestParms{'maxPrice'} || $requestParms{'maxPrice'} eq 0);
                $sqlStr   .= " AND order_quantity >= " . $requestParms{'minQty'} if ($requestParms{'minQty'} || $requestParms{'minQty'} eq 0);
                $sqlStr   .= " AND order_quantity <= " . $requestParms{'maxQty'} if ($requestParms{'maxQty'} || $requestParms{'maxQty'} eq 0);


                if ((not defined $requestParms{sort}) || ($requestParms{sort} =~ /^\s*$/))
                {
                        $sqlStr .= "  ORDER BY limit_price ASC, order_quantity  ";
			$self->{SORT} = "SORT_PRICE_ASC";
                }
                else
                {

                        if ($requestParms{sort} eq "SORT_PRICE_DESC")
                        {
                                $sqlStr .= "  ORDER BY limit_price DESC, order_quantity ";
				$self->{SORT} = "SORT_PRICE_DESC";
                        }
                        elsif ($requestParms{sort} eq "SORT_PRICE_ASC")
                        {
                                $sqlStr .= "  ORDER BY limit_price ASC, order_quantity ";
				$self->{SORT} = "SORT_PRICE_ASC";
                        }
                        elsif ($requestParms{sort} eq "SORT_ORDER_ASC")
                        {
                                $sqlStr .= "  ORDER BY order_quantity ASC, limit_price ";
				$self->{SORT} = "SORT_ORDER_ASC";
                        }
                        elsif ($requestParms{sort} eq "SORT_ORDER_DESC")
                        {
                                $sqlStr .= "  ORDER BY order_quantity DESC, limit_price ";
				$self->{SORT} = "SORT_ORDER_DESC";
                        }
                        elsif ($requestParms{sort} eq "SORT_DATE_DESC")
                        {
                                $sqlStr .= "  ORDER BY original_order_datetime DESC, limit_price ";
				$self->{SORT} = "SORT_DATE_DESC";
                        }
                        elsif ($requestParms{sort} eq "SORT_DATE_ASC")
                        {
                                $sqlStr .= "  ORDER BY original_order_datetime ASC, limit_price ";
				$self->{SORT} = "SORT_DATE_ASC";
                        }

                }

                $self->{SQLSTR} =  $sqlStr;

		carp ("$self->{SQLSTR} : PARAMETERSQL");
	}
 
}

sub execIndexQuery
{
	my $self = shift();
	my $dbconf = DbConfig->new();
	my $dbh	= DBI->connect( "dbi:mysql:" . $dbconf->dbName() . ":" 
			. $dbconf->dbHost(), $dbconf->dbUser(), $dbconf->dbPass(), $::attr )
				or GenError->new(Error->new(102))->display() and die "Cannot Connect to Database $DBI::errstr\n";

	my $sth = $dbh->prepare($self->{SQLSTR}); 
	carp("$self->{SQLSTR} : EXECINDEXQUERY" );

        my $time00 = new Benchmark;
	$sth->execute();
	$self->{DATAREF} = $sth->fetchall_arrayref();
        my $time11 = new Benchmark;
        my $timedd = timediff($time11, $time00);
        my $tstr =  timestr($timedd);

        carp(" ====================");
        carp(" ======== Timer: $tstr ======");
        carp(" =====================");

	$self->{ROWCOUNT} = $sth->rows;

	$dbh->disconnect()
			or warn "Disconnection failed: $DBI::errstr\n"; 

	my @data = ();

	foreach my $row (@{$self->{DATAREF}}) {
		push @data, @$row;  
	}
	
	return(\@data,$self->{ROWCOUNT},$self->{SORT});
}

sub execQuery
{
        my $self = shift();
        my $dbconf = DbConfig->new();
        my $dbh = DBI->connect( "dbi:mysql:" . $dbconf->dbName() . ":"
	                . $dbconf->dbHost(), $dbconf->dbUser(), $dbconf->dbPass(), $::attr )
       			         or  GenError->new(Error->new(102))->display() and die "Cannot Connect to Database $DBI::errstr\n";

        my $sth = $dbh->prepare($self->{SQLSTR});

	carp("$self->{SQLSTR} : EXECQUERY" );

        $sth->execute();
        $self->{DATAREF} = $sth->fetchall_arrayref();
	$self->{ROWCOUNT2} = $sth->rows;

        $dbh->disconnect()
                or warn "Disconnection failed: $DBI::errstr\n";

        return $self->{DATAREF};
}


1;
