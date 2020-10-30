#!/usr/bin/perl -wT

use strict;
use lib "/home/abrooks/www/pollCenter/script_src";
use Captcha;

my $captcha_text = Captcha::genCaptcha("SSSSSS","AS734");

print $captcha_text, "\n"; 
