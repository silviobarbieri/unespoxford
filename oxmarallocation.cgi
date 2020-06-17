#!/usr/bin/env perl

#call subroutine to parse the form contents
&parsing;  

# extract information from the form using the value labels in the form
$daydate=$formdata{'whatday'};
$month=$formdata{'whatmonth'};
$year=$formdata{'whatyear'};
$participantid=$formdata{'whatparticipantid'};
$submitteremail=$formdata{'whatsubmitteremail'};
$age=$formdata{'whatage'};
$gender=$formdata{'whatgender'};
$ethnicity=$formdata{'whatethnicity'};
$diabetic=$formdata{'whatdiabetic'};



#set the email address to send details to for administrator to confirm to applicatnt
$administratoremail="name.name\@domain.ac.uk";

#Setfilepaths for text files, firstly for the main file, secondly for an archive file
$filepathforallocations ="allocationstemp1.txt";
$filepathforallocationsarchive ="archiveallocationstemp1.txt";


#-----------------below here does some date manipulation on the date submitted if required ---------------


#-----sort out todays date----

$now=gmtime;
($sec, $min, $hour, $mday, $mon, $yeartime, $wday, $yday, $isdst) = gmtime(time);
$yeartime=$yeartime+1900;


@monthlist =qw(January February March April May June July August September October November December);
$monthname =$monthlist[$mon];
#$mon starts at 0 so add 1 to it to get the actual month for numerical representation
$mon=$mon+1;

#$wday starts on Sunday with zero
@weekdaynames =qw(Sun Mon Tue Wed Thu Fri Sat);
$weekday = $weekdaynames[$wday];



#---produce an html page as output for user to confirm that the information they submitted is correct


	&MakeHtmlPageSucces;
	
	


#-------------the subroutines are below this line--------------------------

sub MakeHtmlPageSucces {
#--------- creates the html page ----------


#create title and header
$pagetitle= "Feedback Summary"; 
$header= "Feedback Summary";

&Header($header);
print<<"bodytext";
<body bgcolor="#FFFFFF">
<p align="center"><b><font face="Verdana, Arial, Helvetica, sans-serif" size="+4" color="#0000FF">Allocation Pending</font></b></p>

<p align="left"><b><font face="Arial, Helvetica, sans-serif" size="+2" color="#004080">Allocation Request Summary</font> </b></p>

<P>Thank you for your request to allocate to the study.</p>
<p>
<p>
<p>This is a summary of your request. Please check the details for any errors. Use the back arrow of your browser to re-edit your allocation and resubmit it if there are errors.</p>

<p>*** Please note that this allocation is <b>NOT </b>complete until you click on the 'Confirm Allocation Now' button below.*** </p>

<p><b>The date today is </b> $mday / $mon / $yeartime or $weekday $mday $monthname  $yeartime</p>

<p><b>The data you submitted for allocation are :</b> </p>
<p><b>Participant ID:</b> $participantid</p>
<p><b>Age:</b> $age</p>
<p><b>Gender:</b> $gender</p>
<p><b>Ethnicity group:</b> $ethnicity</p>
<p><b>Diabetic status:</b> $diabetic</p>

<p><b>Your email address:</b> $submitteremail</p>

<p>You will receive email verification of the allocation if it is accepted. </p>

<p>If you do not, then please contact the chief investigator as you may have submitted an incorrect email address. </p>  


<FORM
ACTION="https://unespoxford.herokuapp.com/oxmarconfirmallocation.psgi"
METHOD=POST>

<INPUT TYPE=hidden NAME=participantidwhat VALUE=$participantid>
<INPUT TYPE=hidden NAME=agewhat VALUE=$age>
<INPUT TYPE=hidden NAME=genderwhat VALUE="$gender">
<INPUT TYPE=hidden NAME=ethnicitywhat VALUE="$ethnicity">
<INPUT TYPE=hidden NAME=submitteremailwhat VALUE="$submitteremail">
<INPUT TYPE=hidden NAME=diabeticwhat VALUE="$diabetic">
<INPUT TYPE=hidden NAME=daywhat VALUE=$mday>
<INPUT TYPE=hidden NAME=monthwhat VALUE=$mon>
<INPUT TYPE=hidden NAME=yearwhat VALUE=$yeartime>
<INPUT TYPE=hidden NAME=weekdaywhat VALUE=$weekday>



<p><INPUT TYPE="submit" VALUE="Confirm Allocation Now">
</FORM>




bodytext
&Footer;


}





#---------------------------------


sub parsing

{
if ($ENV{'REQUEST_METHOD'} eq 'GET') {
        @pairs = split(/&/, $ENV{'QUERY_STRING'});
} elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
        read (STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
        @pairs = split(/&/, $buffer);
} else {
        print "Content-type: text/html\n\n";
        print "<P>Use Post or Get";
}

foreach $pair (@pairs) {
        ($key, $value) = split (/=/, $pair);
        $key =~ tr/+/ /;
        $key =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
        $value =~ tr/+/ /;
        $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

        $value =~s/<!--(.|\n)*-->//g;

        if ($formdata{$key}) {
                $formdata{$key} .= ", $value";
        } else {
                $formdata{$key} = $value;
        }
}

}


#---------------------------------

sub Header {
#writes a header for the html page
  print "Content-type: text/html\n\n";
  print "<HTML><HEAD><TITLE>";
  print "$_[0]";
  print "</TITLE></HEAD><body bgcolor=#FFFFFF>\n";

}



#---------------------------------

sub Footer {
#writes a footer for the html page

print<<"signature";
<hr>
<ADDRESS>

C.A.O'Callaghan : revised 2013
</ADDRESS>
signature

print "\n</BODY></HTML>";
}

