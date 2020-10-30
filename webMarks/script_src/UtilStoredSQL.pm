package UtilStoredSQL;

use strict;
use Error;
use SessionObject;
use CGI::Cookie;
use Storable;
use Data::Dumper;

#my $tmp_dir = "/services/webpages/d/c/dcoda.net/tmp";
my $tmp_dir = "/tmp";

BEGIN
{
     require         Exporter;

     use vars        qw(@ISA @EXPORT @EXPORT_OK);
     @ISA            = qw(Exporter);
     @EXPORT         = qw(&headerHttp &headerHtml &footerHtml &validateSession &formValidation &storeSession &storeSQL &getStoredSQL &genSessionID &genID &isset);
}

sub headerHttp
{
	return "Content-type:text/html\n\n";
}


sub headerHtml
{
	my $buffer_out;
	$buffer_out = headerHttp();
	$buffer_out .= "<html>\n"
   	       .  " <head>\n"
    	       .  "<title> StockApp</title>\n"
 	       .  "<LINK href='$::URL_PATHS->{MAINSTYLE_CSS}' rel='stylesheet' type='text/css'>\n"
	       .  "<script type='text/javascript' src='$::URL_PATHS->{COMMON_JS}'> </script>\n"
	       .  "</head>\n"
	       .  "<body>\n";
	return $buffer_out;

}


sub footerHtml
{
	my $buffer_out;
	$buffer_out = "</body>\n"
		. "</html>\n";
	return $buffer_out;
}


sub dumpEnvHtml
{
	my %anyHash		= %ENV;
	my ($key,$value)	= ""; 
	print "\n<table>";
	while (($key,$value) = each %anyHash) {
		print "\n<tr><td bgcolor=\"lightblue\"> $key </td> <td bgcolor=\"cyan\">$value</td></tr>";
	} 
	print "\n</table>"; 
}

sub parseParms
{
	my $rawInputParms	= $ENV{QUERY_STRING};
	my %inputHash	= ();

	my @rawInputParms = split /&/, $rawInputParms;
	foreach my $rawStr (@rawInputParms) {
		my ($key,$value) = split /=/, $rawStr;
		$inputHash{$key} = $value;
	}
	return \%inputHash;

}

sub printInputEnv 
{
	my ($key,$value)	= ""; 
	while (($key,$value) = each my %inputHash) {
		print "$key=$value\n";
	} 
  
}

sub genSessionID
{
	my @id_list = qw(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 0 1 2 3 4 5 6 7 8 9);
	my $id;
	for(my $i = 0; $i < 16; $i++) {
		 $id .= $id_list[int(rand 35)] ;
	}
	return $id;
}


sub genQueryID
{
        my @id_list = qw(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 0 1 2 3 4 5 6 7 8 9);
        my $id;
        for(my $i = 0; $i < 5; $i++) {
                 $id .= $id_list[int(rand 35)] ;
        }
        return $id;
}



sub storeSession
{
	my $sessionInstance = shift;
	my $sessionID = shift;
	my $userID = shift;
	my $userName = shift;

	my $sessionObject = SessionObject->new($sessionInstance,
                                         $sessionID,
                                         $userID,
                                         $userName);

	#store $sessionObject, "/tmp/$sessionID" || die $!;
	store $sessionObject, "$tmp_dir/$sessionID" || die $!;

}

sub getSessionInstance
{
	my $sInstancePre = 'ses';
	my @numInstances = @{$::SESSION_CONFIG->{INSTANCES}};
	return $sInstancePre . int(rand(scalar(@numInstances)));

}

sub storeSessionObject
{
        my $sessionObject = shift;
        my $sessionFile = $sessionObject->{wmSESSIONID};

	#store $sessionObject, "/tmp/$sessionFile" || die $!;
	store $sessionObject, "$tmp_dir/$sessionFile" || die $!;

}

sub validateSession
{
        my ($sessionID,$userID)  = ();

        my %cookies = fetch CGI::Cookie;
        return Error->new(104) unless (defined $cookies{'wmSessionID'} && defined $cookies{'wmUserID'});

        $sessionID = $cookies{'wmSessionID'}->value;
        $userID = $cookies{'wmUserID'}->value;

	#return Error->new(104) 	if not -e "/tmp/$sessionID";
	return Error->new(104) 	if not -e "$tmp_dir/$sessionID";

	#my $sessionObject = retrieve("/tmp/$sessionID") || return Error->new(103);
	my $sessionObject = retrieve("$tmp_dir/$sessionID") || return Error->new(103);

        return $sessionObject;

}

sub storeSQL
{
       my $storedSQL = shift;
       my $sessionObject = validateSession();
       $sessionObject->{DATA} = $storedSQL;
       storeSessionObject($sessionObject); 
}

sub getStoredSQL
{
       my $sessionObject = validateSession();
       my $storedSQL = $sessionObject->{DATA};
       return $storedSQL;
}


sub formValidation
{
	my $query = shift;
	my %sqlInsert = ();
	my $passLen = 6;
	my $userLen = 6;

	$sqlInsert{firstName} =	isset($query->param('firstName')) ? $query->param('firstName') : '';
	$sqlInsert{lastName} =	isset($query->param('lastName')) ? $query->param('lastName') : '';
	$sqlInsert{address1} =	isset($query->param('address1')) ? $query->param('address1') : '';
	$sqlInsert{address2} =	isset($query->param('address2')) ? $query->param('address2') : '';
	$sqlInsert{city} =	isset($query->param('city')) ? $query->param('city') : '';
	$sqlInsert{state} =	isset($query->param('state')) ? $query->param('state') : '';
	$sqlInsert{zipcode} =	isset($query->param('zipcode')) ? $query->param('zipcode') : '';
	$sqlInsert{phone} =	isset($query->param('phone')) ? $query->param('phone') : '';
	$sqlInsert{email} =	isset($query->param('email_address')) ? $query->param('email_address') : '';
	$sqlInsert{userName} =	isset($query->param('user_name')) ? $query->param('user_name') : '';
	$sqlInsert{password} =	isset($query->param('new_user_pass1')) ? $query->param('new_user_pass2') : '';


	return Error->new(106) if($sqlInsert{userName} eq 'NULL' || length($sqlInsert{userName}) < $userLen); 

	return Error->new(111) if($sqlInsert{password} eq 'NULL' || length($sqlInsert{password}) < $passLen); 

	return Error->new(113) if($query->param('new_user_pass1') ne $query->param('new_user_pass2')); 

	return Error->new(119) if($sqlInsert{email} !~ /\w+[\w.]+?\w+@\w+[\w.]+?\.\w+\s*$/);



	return \%sqlInsert;
}

sub profileFormValidation
{

	my $query = shift;
	my %sqlUpdate = ();
	my $passLen = 6;
	my $userLen = 6;

	$sqlUpdate{new_password} =  isset($query->param('new_password')) ? $query->param('new_password') : '';
	$sqlUpdate{confirm_password} =  isset($query->param('confirm_password')) ? $query->param('confirm_password') : '';
	$sqlUpdate{userName} =	isset($query->param('userName')) ? $query->param('userName') : '';

	return Error->new(110) if($sqlUpdate{userName} eq '' || length($sqlUpdate{userName}) < $userLen); 

	if (length($sqlUpdate{new_password}) >= $passLen &&  length($sqlUpdate{confirm_password})  >= $passLen) {
 
		return Error->new(112) if $sqlUpdate{new_password} ne $sqlUpdate{confirm_password};
		return \%sqlUpdate;

	} else {

		return Error->new(112) if (length($sqlUpdate{new_password}) > 0 || length($sqlUpdate{confirm_password}) > 0);

		$sqlUpdate{firstName} = isset($query->param('firstName')) ? $query->param('firstName') : '';
		$sqlUpdate{lastName} =  isset($query->param('lastName')) ? $query->param('lastName') : '';
        	$sqlUpdate{address1} =  isset($query->param('address1')) ? $query->param('address1') : '';
        	$sqlUpdate{address2} =  isset($query->param('address2')) ? $query->param('address2') : '';
        	$sqlUpdate{city} =      isset($query->param('city')) ? $query->param('city') : '';
        	$sqlUpdate{state} =     isset($query->param('state')) ? $query->param('state') : '';
        	$sqlUpdate{zipcode} =   isset($query->param('zipcode')) ? $query->param('zipcode') : '';
        	$sqlUpdate{phone} =     isset($query->param('phone')) ? $query->param('phone') : '';

		return \%sqlUpdate;
		
	}

}


sub slurp_file
{
	my $file_name = shift;
	my $out_page = ();

        open(FH, "<$file_name") or
                warn "Cannot open $file_name\n";
        my $terminator = $/;
        undef $/;
        $out_page = <FH>; #slurp file all at once via above line.
        $/ = $terminator;
        close(FH);
	return $out_page;
}

sub isset
{
  return ((defined $_[0]) && ($_[0] !~ /^\s*$/));
}


1;
