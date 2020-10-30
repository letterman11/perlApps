#!/usr/bin/perl -wT

use strict;
use lib "/home/angus/dcoda_net/private/chatterBox/script_src";
#use DbConfig;
use DbGlob;
use Util;
use CGI qw (:standard -debug);
use CGI::Cookie;
use CGI::Carp;
#use CGI::Carp qw(fatalsToBrowser);

$CGI::POST_MAX=1024 * 10;  # max 10K posts
$CGI::DISABLE_UPLOADS = 1;  # no uploads

my $query = new CGI;
my $initSessionObject = Util::validateSession();


if (ref $initSessionObject eq 'SessionObject')
{
        #TO DO: Restructure handling of db login failure

       # my $dbc = DbConfig->new()
        my $dbg = DbGlob->new()
                        or die "Cannot Create DB Handle \n";

       # my $dbh = $dbc->connect()
        my $dbh = $dbg->connect()
                        or die "Cannot Connect to Database $DBI::errstr\n";

	#	$dbh->trace(1, 'chat_dbi_ping.log');

        my $sqlstr = ();
        my $sqlstr2 = ();
	my $sqlstr3 = ();
        my $sth = ();
        my $room_array = ();
        my $row_count = ();
        my $msg_user_array = ();
	my $msg_queue_array = ();

	my $userID = $query->param('userID');
	my $roomID = $query->param('roomID');
	
	if($query->param('req') eq 'ajaxPing')
	{
		my @user_cr_row = ();

		$sqlstr = "select * from user_cr where user_id = '$userID'";
		$sqlstr2 = "select user_id from user_cr where room_id = '$roomID'";		

		eval {		
			#one exec sequence
			@user_cr_row = $dbh->selectrow_array($sqlstr);
			#second exec sequence
			$sth = $dbh->prepare($sqlstr2);
						
			$sth->execute();
		
			$msg_user_array = $sth->fetchall_arrayref;	

			$sth->finish();
		
		};	
		
		carp("ping server - DB ERROR " . $@) if ($@);

		if($@) 
		{
			print $query->header(-status=>'1001 Application Error: Failed on combo select user_cr'
						);	
		}
		else
		{
			$sqlstr2 = "select * from chat_room_queue "
				 . " where msg_user_id = '$userID' "
				 . " and insert_ts >= '$user_cr_row[2]' "
				 . " order by cr_queue_id desc limit 2 ";

			eval {		
	
				my $sth = $dbh->prepare($sqlstr2);
	
				$sth->execute();
	
				$msg_queue_array = $sth->fetchall_arrayref;	
	
				$sth->finish();
	
			};	

			carp("ping server - DB ERROR " . $@) if ($@);
				
			if($@) 
			{
				print $query->header(-status=>'1002 Application Error: Failed ChatRoom Select'
							);	
			}	
			elsif(scalar(@{$msg_queue_array}) > 0)
			{
				$sqlstr3 = "delete from chat_room_queue "
					 . "where cr_queue_id = " . @{$msg_queue_array}[0]->[0]; 
				
				for(my $i=1; $i < scalar(@{$msg_queue_array}); $i++)
				{
					$sqlstr3 .= " or cr_queue_id = " . @{$msg_queue_array}[$i]->[0]; 

				}				

				carp("DELETE CHAT TBL " . $sqlstr3);	

				eval {		
					my $sth = $dbh->prepare($sqlstr3);
		
					$sth->execute();
		
					$sth->finish();
		
				};	
				
				carp("ping server - DB ERROR " . $@) if ($@);
				if($@)
				{
					print $query->header(-status=>'1003 Application Error: Failed ChatRoom Delete'
							);	
				}
				else
				{
					#all done return JSON_CO to client
					my $json_co = ();
					my ($user_id,$msg_user_id,$room_id,$msg_text,$time_stamp,$msg_q_id) = (1,5,2,4,3,0);
					my $i = 0;
					$json_co =  qq/  { \n "messages" : [ \n
						   { 
						 		"user_id" :  "@{$msg_queue_array}[$i]->[$user_id]", \n
						 		"room_id" :  "@{$msg_queue_array}[$i]->[$room_id]", \n
						 		"msg_text" : "@{$msg_queue_array}[$i]->[$msg_text]", \n
						 		"msg_q_id" : "@{$msg_queue_array}[$i]->[$msg_q_id]", \n
						 		"time_stamp" : "@{$msg_queue_array}[$i]->[$time_stamp]" \n
						  } / ;
						
					for(++$i; $i < scalar(@{$msg_queue_array}); $i++) 
					{

					$json_co .=  qq/ 
						    , \n { 
						 		"user_id" :  "@{$msg_queue_array}[$i]->[$user_id]", \n
						 		"room_id" :  "@{$msg_queue_array}[$i]->[$room_id]", \n
						 		"msg_text" : "@{$msg_queue_array}[$i]->[$msg_text]", \n
						 		"msg_q_id" : "@{$msg_queue_array}[$i]->[$msg_q_id]", \n
						 		"time_stamp" : "@{$msg_queue_array}[$i]->[$time_stamp]" \n
						  }  \n / ;
						
					}
					
					$json_co .= " ] ";

					my $js_msg_user_array = ();
					
						if (scalar(@{$msg_user_array}) > 1) 
						{

							$js_msg_user_array .= "\"" . @{$msg_user_array}[$i]->[0] . "\""; 

                                                        my $i = 0;
                                                        $js_msg_user_array =  qq/  "msg_user_ids" : [ "@{$msg_user_array}[$i]->[0]"  /;

				
							for(++$i; $i < scalar(@{$msg_user_array}); $i++) 
							{
								$js_msg_user_array .=  ", \"" . @{$msg_user_array}[$i]->[0] ."\"";
							}
		
							 $js_msg_user_array .= " ] ";
						}
					
					$json_co .= ", \n $js_msg_user_array " if ($js_msg_user_array);
					$json_co .= " \n} ";

					carp("JSON_CO object: " . $json_co);

					print $query->header(-status=>'200 OK',
								-Content_Type=>'text/javascript'
								);
					print $json_co;
				}
			}
			elsif(scalar(@{$msg_user_array}) > 1)
			{

				my $json_co = ();

				my $js_msg_user_array = ();
				
				$json_co = "  { ";
									
				$js_msg_user_array = " \"msg_user_ids\" : [ ";
				my $i = 0;

				$js_msg_user_array .= "\"" . @{$msg_user_array}[$i]->[0] . "\""; 
	
				for(++$i; $i < scalar(@{$msg_user_array}); $i++) 
				{
					$js_msg_user_array .=  ", \"" . @{$msg_user_array}[$i]->[0] ."\"";
				}
	
				$js_msg_user_array .= " ] ";
				
				$json_co .= "\n $js_msg_user_array " if ($js_msg_user_array);
				$json_co .= " \n} ";

				carp("JSON_CO object: " . $json_co);
				carp("process ID: " . $$);

				print $query->header(-status=>'200 OK',
							-Content_Type=>'text/javascript'
							);
				print $json_co;

			}
			else
			{
				print $query->header(-status=>'200 OK'
						);
			}

		}
	}

}

exit;
