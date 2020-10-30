package GenReport;


use strict;

sub stockHeaderHtml
{
#	return "<tr class='tbl_hd'><th> TA NUMBER </th><th> FIRM SYMBOL </th><th> LIMIT PRICE </th><th> ORDER QUANTITY </th> <th> ORDER DATE </th> </tr>\n";

	return "<tr class='tbl_hd'><th> TA NUMBER </th><th> FIRM SYMBOL </th> " 
		. " <th> <a href='javascript:tblSort(\"PRICE\")'>  LIMIT PRICE </a> </th> <th> <a href='javascript:tblSort(\"ORDER\")'> ORDER QUANTITY </a> </th> "
		. " <th>  <a href='javascript:tblSort(\"DATE\")'> ORDER DATE  </a> </th> </tr>\n ";

}


sub new
{
	my $class = shift();
	my $self = {};
	my $mModel = shift;
	$self->{DATA} = $mModel->{DATAREF}; 
	$self->{ROWCOUNT} = $mModel->{ROWCOUNT};
	$self->{ROWSPERPAGE} = $mModel->{PARMS}->{rowsPerPage} || 30;	
	bless ($self,$class);
	return $self;	
}

sub display
{
	my $self = shift(); 
        my $page = shift();
	my $buffer_out = ();
   
	$buffer_out  = StockUtil::headerHtml();
	$buffer_out .= "<table class='results' width=100% cellspacing='1' cellpadding='1' border='0' align='left' >\n";
	$buffer_out .= stockHeaderHtml();
	my  ($i,$alt) = 0;
	foreach my $row (@{$self->{DATA}}) {
		my ($ta_number, $firm_symbol, $limit_price, $order_quantity, $order_datetime) = @$row;
		$alt =  (++$i % 2 ? 1 : 2);
		$buffer_out .= "<tr class='tbl_num$alt'><td class='tbl_txt' width='15%'> $ta_number </td> "  
	 	            .  "<td class='tbl_txt' width='10%'> $firm_symbol</td><td width='15%'> $limit_price </td><td width='15%'> $order_quantity</td> "
			    .  "<td width='30%'> $order_datetime </td></tr>\n";

	} 
	$buffer_out .= "<tr class='results'><td colspan='100%'>";
	$buffer_out .= $self->genNavigation($page);
	$buffer_out .= "\n </td></tr>\n";
	$buffer_out .= "\n</table>\n";
	$buffer_out .= "<!-- " . $self->{ROWCOUNT} . " -->"; 

	$buffer_out .= StockUtil::footerHtml();
	print $buffer_out;
}


sub genNavigation
{
	my $self = shift;
	my $currPage = shift || 0; 
	my $buffer_out = (); 
	my $pgCnt = 1;
	my $currCnt  = 0;
	my $totRows = $self->{ROWCOUNT};
	my $rowsPerPage = $self->{ROWSPERPAGE};


	if($totRows > $rowsPerPage) {
		$buffer_out .= "Pages: ";
		do {
			if ( $currPage eq $pgCnt ) 
			{			
				$buffer_out .= " <span id='curr_page'>  $pgCnt </span>";
			}
			else
			{
				$buffer_out .= " <A HREF=/stockApp/cgi-bin/stockReportDetail.cgi?page=" . $pgCnt .  "&rowsPerPage=" . $rowsPerPage . ">" .  $pgCnt . "</A> ";
			}
			$currCnt += $rowsPerPage;
			$pgCnt++;
		}while($currCnt < $totRows);
	}
	return $buffer_out;

}


1;
