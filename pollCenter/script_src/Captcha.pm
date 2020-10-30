package Captcha;

use strict;
use Image::Magick;
use File::Copy;

#use Posix qw/ceil/;

sub genCaptcha
{

   #my $imgWidth=ceil(574/36);
   my $imgWidth=16;
   my $imgHeight=26;
   my @captchaIndexTable = ();
   my $sessionDir = shift;
   my $captchaFileName = shift;
   my $baseImage = shift;


   if (not defined $baseImage) 
   {
      $baseImage = "alphanummonofont.png";
      #$baseImage = "alpha.png";
   }
  

   my $image = Image::Magick->new;
   $image->Read($baseImage,$baseImage,$baseImage,$baseImage,$baseImage,$baseImage);

   open(IMG2, ">/home/abrooks/www/pollCenter/gen_rsrc/$sessionDir/$captchaFileName.png");

   my @array = qw(a b c d e f g h i j k l m n o p q r s t u v w x y z 1 2 3 4 5 6 7 8 9 0);

   for (my $i=0; $image->[$i]; $i++)
   {
       my $alphaOffSet = int(rand(36));
       push @captchaIndexTable, $alphaOffSet;
       my $imgOffSet = $alphaOffSet * $imgWidth;	
       $image->[$i]->Crop(geometry=>$imgWidth . "x" . $imgHeight . "+$imgOffSet+0");
       $image->[$i]->Implode(amount=>.64, interpolate=>'bicubic');
   }

   my $captchaFileOut = $image->Append(stack=>"false");
   $captchaFileOut->Write(file=>\*IMG2, filename=>"$captchaFileName.png");

   return join ("", map { $array[$_] } @captchaIndexTable); 

}


1;
