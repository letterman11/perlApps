package GenStockList;


use strict;
use CGI;
use CGI::Carp;


sub new
{
	my $class = shift;
	my $self = {};
	$self->{STOCKLIST} = shift;

	bless ($self,$class);
	return $self;

}

sub display
{

	my $self = shift;
	my $out_buffer;
	my $rowcount = 0;
	my $rowlen = 5;
	my $flag = 0;
	my @stocklist_array = @{$self->{STOCKLIST}};

	my $stock_name = ();
	my $old_stock_name = ();
	my $div_id = ();
	my ($true,$false) = (1,0);


	my $flag_newdiv= $false;

        @stocklist_array = sort(@stocklist_array);	

	carp("@stocklist_array " . scalar(@stocklist_array));

	$out_buffer = "<html><head><title> stocklist </title> "
		    . "<script language=\"Javascript\" src=\"$::URL_PATHS->{VALIDATION_JS}\" type=\"text/javascript\"> </script> "
		    . "<LINK href='$::URL_PATHS->{MAINSTYLE_CSS}' rel='stylesheet' type='text/css'> "
		    . "	</head>\n "
		    . "<body> ";

	for(my $i=0; $i< scalar(@stocklist_array); $i++) 
	{
		$stock_name = $stocklist_array[$i];
		if(substr($stock_name,0,1) ne substr($old_stock_name,0,1)) 
		{
			$out_buffer .= "</table></div>\n" if $flag++;

			$rowcount = 0;
			$div_id = "stock_pre" . substr($stock_name,0,1);	
			$out_buffer .= "<div id=\"$div_id\" class=\"stocklist_div\">\n"
				    . "<table class=\"results2\"  cellspacing=\"1\" cellpadding=\"1\"> "
				    . "<tr class=\"tbl_hd_stock_sym\"><th width=\"100%\" colspan=\"100%\"><a class=\"tbl_hd_stock_sym_link\" href=\"javascript:void 0\" onclick=\"giveTop($div_id)\"> " 
				    . substr($stock_name,0,1) . "</a>" . "</th></tr>\n" 
				    . "<tr class=\"tbl_stock_sym\">";
				   
			$out_buffer .= "<td> <a href=\"javascript: void 0\" onclick=\"setStockField('$stocklist_array[$i]',$div_id)\" > $stocklist_array[$i] </a> </td>";

		} else { 

			$out_buffer .= "<tr class=\"tbl_stock_sym\">" if $rowcount == 0;
			$out_buffer .= "<td> <a href=\"javascript: void 0\" onclick=\"setStockField('$stocklist_array[$i]',$div_id)\" > $stocklist_array[$i] </a> </td>";

		}

		$rowcount++;
		if ($rowcount eq $rowlen) 
		{ 
			$out_buffer .= "</tr>\n";
			$rowcount = 0;
		}


		$old_stock_name = $stocklist_array[$i];
	}	
	
	$out_buffer .= "</body></html>\n";
	print $out_buffer;

}






1;
