#!/usr/bin/perl -wT

use strict;
use lib "/home/ubuntu/dcoda_net/pollCenter/script_src";
use Captcha;

my $captcha_text = Captcha::genCaptcha("SSSSSS","AS734");

print $captcha_text, "\n"; 
