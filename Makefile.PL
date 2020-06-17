use strict;
use warnings;

use ExtUtils::MakeMaker;

WriteMakefile(
  NAME         => 'app.pl',
  VERSION      => '1.0',
  AUTHOR       => 'Silvio Barbieri <silviofbarbieri@gmail.com>',
  EXE_FILES    => ['oxmarallocation.cgi'],['oxmarconfirmallocation.cgi'],
  PREREQ_PM    => {'Mojolicious' => '2.0'},
  test         => {TESTS => 't/*.t'}
);