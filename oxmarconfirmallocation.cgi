#!/usr/bin/perl5

&parsing;  

#------------ get variables from the form - need to edit this section to get data from form appropriate to trial

#Set variables 
$participantidn=$formdata{'participantidwhat'};
$agen=$formdata{'agewhat'}; #the email of the person submitting the form
$gendern=$formdata{'genderwhat'};
$ethnicityn=$formdata{'ethnicitywhat'};
$diabeticn=$formdata{'diabeticwhat'};
$submitteremailn=$formdata{'submitteremailwhat'};
$dayn=$formdata{'daywhat'};
$monthn=$formdata{'monthwhat'};
$yearn=$formdata{'yearwhat'};
$weekdayn=$formdata{'weekdaywhat'};

#----------------- set other variables------------Need to read this section and act on it for each new trial--------------------
#initialise outcome to 0
$outcome = 0;

#$numberofclasses = the number of classes eg. gender x the number of possiblities ie gender = 2, ethnicity (white black asian chinese) would equal 3. together they woudl be 5
#here the possibilities are: male female young old notdiabetic diabetic white asian black chinese ie 10 in total
#contents participant ID [0], GenderMale[1], GenderFemale[2], AgeYoung[3], AgeOld[4], NonDiabetic[5], Diabetic [6], White[7] Black[8] Asian[9] Chinese[10] ControlGroup[11], ExperimentalGroup[12], Day[13], Month[14], Year[15], Age[16]
#need to edit MakeArrayFromInput algorithm correctly to interpret form input appropriately

$numberofclasses = 10;

#note $numberofclasses+1 = option1 field and $numberofclasses+1 = option2 field in array.These options are the outocomes of the allocation process.
#set options - the algorithm outputs two options as string outputs to the variable $allocationchosen - the values are 'option1' and 'option2'
#option1 = control arm; option2 = experimental arm
#use the hash below to provide text output by just altering the values of $firstchoice and $secondchoice

#set strings that will be used to label the outcome in the final output
$textoutcome=""; #just an empty string at first
$firstchoice="<u>Control Arm</u> of the Study";
$secondchoice="<u>Intervention Arm</u> of the Study";
#set up a hash linking each option with the appropriate label
%choicehash = ("option1", $firstchoice, "option2", $secondchoice);
# as these options are output to the variable $allocationchosen use $choicehash{'$allocationchosen'} to get the actual option required

#set the age threshold for deciding young and old
$agethreshold =65;

# define minimisation only or randomisation
# set $randomisationelement to 1 for no randomisation or to 0.8 for 80% randomisation etc. No changes are needed elsewhere to implement this
$randomisationelement = 1 ;

#set the email address or addresses to send details to for administrator 
$administratoremail="name.name\@domain.ac.uk";
$researcheremail="name.name\@domain.ac.uk";


#Setfilepaths for text files, firstly for the main file, secondly for an archive file
$filepathforallocation ="allocationstemp1.txt";
$filepathforallocationarchive ="archiveallocationstemp1.txt";


#---Main program


	#-------------read up the file data on participants already in the study  and make an array for each arm of the study--------
	#first read files and make each line into an array then process this into two arrays one for the control arm $controlarray and one for the experimental arm $exptarray
	
	&ConvertFileLineToArray ($filepathforallocation) ;

	#------make an array from the data input by user ----------
	
	&MakeArrayFromInputData ;
	
	#----do the minimisation and make the allocation - get this from teh algorithm as either option1=control=[7] option2= experimental = [8]

	$allocationchosen = &DoMinimisationAndAllocation ;

	#-------randomise this participant-----------could be used for simple randomisation
	#$randomoutcome=&RandomiseThisParticipant (0.5);
	#$allocationoutcome=$randomoutcome;

	&ReviseParticipantArrayWithResult($allocationchosen);
	&MakeArrayOneLine ;
	
	#Decode the final outcome for use on the html page for the outcome - uses the hash with the values in. 
	$textoutcome=$choicehash{$allocationchosen};

	#call subroutine with text to put on line and filepath
	$newparticipantline = $newline;
	&FileWrite($newparticipantline, $filepathforallocation);
	&FileWrite($newparticipantline, $filepathforallocationarchive );

	#---------below here creates the feedback html page if booking is successful----------
	#$datelist=&CalculateDiaryDates ($daydate, $month, $year, $numberofdays);
	&MakeHtmlPageSucces;
	
	#---send emails
	#first calculate the time now
	$currenttime=&WhatTimeNow;
	#first construct the strings for the emails
	&SendEmails; 
	#send email to the researcher submitting the form------------
	mail($submitteremailn, $emailsubject, $replytowriter);
	#send email to the study nurse the form------------
	mail($researcheremail, $emailsubject, $replytostudynurse);
	#send email to the administrator------------
	mail ($administratoremail, $emailsubject, $mailcontentforadministrator);


#----subroutines are below here-----------

#--------------------------Convert line from text to an array-------------------

sub ConvertFileLineToArray {
#sent the filepath as an argument
#currently uses [$numberofclasses+1] as control arm and [$numberofclasses+2] as index for expt arm
#outputs two arrays but not as return values  - it just modifies them as $controlarray and $exptarray with same indices as input data ie 
#contents participant ID [0], GenderMale[1], GenderFemale[2], AgeYoung[3], AgeOld[4], NonDiabetic[5], Diabetic [6], White[7] Black[8] Asian[9] Chinese[10] ControlGroup[11], ExperimentalGroup[12], Day[13], Month[14], Year[15], Age[16]
# set everything in the arrays to zero initially

$filetoopen=$_[0];
open(THISFILE, "<out/$filetoopen") ||&Erromessage("Allocations file unavailable at $filetoopen");
@filearray = <THISFILE>;
close(THISFILE);
$lengthoffilearray=@filearray;

#set values of each element of controlarray and exptarray to zero to start. 
# The number of elements is that of the number of features or 'classes' of the participants
#nb in next line setting out the for loop, it is possible to use $p<9, but the use of $numberofclasses-1 
#allows changes in this number and so in the length of the array to be set elsewhere
for ($p=0; $p<$numberofclasses-1; $p++) {
$controlarray[$p]=0;
$exptarray[$p]=0;
}#end for

#next two lines are just used to output this information to the administrator email.The values are incremented in the loops below. 
$option1total = 0;
$option2total = 0;

$i=0;
while ($i<$lengthoffilearray) {
	@formatext=split(/zz/,$filearray[$i]);

		if (($formatext[$numberofclasses+1]==1)&&($formatext[$numberofclasses+2]==0)) {

			for ($j=1; $j<($numberofclasses+3); $j++) {
				$controlarray[$j]=$controlarray[$j]+$formatext[$j];
			}#end for
			$option1total++;
		} # endif
		elsif (($formatext[$numberofclasses+2]==1)&&($formatext[$numberofclasses+1]==0)) {

			for ($k=1; $k< ($numberofclasses+3); $k++) {
				$exptarray[$k]=$exptarray[$k]+$formatext[$k];
			}#end for
			$option2total++;
		} # end elsif
		else {
		} #end else does nothing but could deliver an alert

	$i++;
	} # end while


} #end subroutine

#---determine time-----------
sub WhatTimeNow {
$now=gmtime;
($sec, $min, $hour, $mday, $mon, $yeartime, $wday, $yday, $isdst) = gmtime(time);

$formatedminutes= sprintf("%02d", $min);
$formatedhours= sprintf("%02d", $hour);
$timenow=$formatedhours.":".$formatedminutes;
return $timenow;

} #end subroutine

#-----------------------minimsation ------------------
sub DoMinimisationAndAllocation {

# first total up the scores for each of the relevant parameters that are correct for the new participant
# weighting could be applied for different allocation elements by transformation of the values for those elements
$controlarmscore = 0;
$experimentalarmscore = 0;
$allocationchosen = "";

	for ($r=1; $r<($numberofclasses+3); $r++) {
		
		if ($localarray[$r]==1) {

			$controlarmscore = $controlarmscore + $controlarray[$r];
			$experimentalarmscore = $experimentalarmscore + $exptarray[$r];

		} # endif
		elsif ($localarray[$r]==0) {
			#do nothing
			#$controlarmscore = $controlarmscore + $controlarray[$r];
			#$experimentalarmscore = $experimentalarmscore + $exptarray[$r];

		} # endelsif
		else {
		} #end else

	}#end for

# second make the control vs expt comparison with respect to the variables displayed by the new participant

		if ($experimentalarmscore> $controlarmscore ){
			#allocate to control arm
			#$allocationchosen = "option1";
	#--if a randomisation component is required then it is applied here eg.	
			$allocationchosen =&RandomiseThisParticipant ($randomisationelement); 
		} # endif
		elsif ($controlarmscore > $experimentalarmscore) {
			#allocate to experimental arm
			#$allocationchosen = "option2";
			$allocationchosen =&RandomiseThisParticipant (1-$randomisationelement);
		} # endelsif
		elsif ($controlarmscore == $experimentalarmscore) {
			#need to randomise with probabily 0.5
			$allocationchosen =&RandomiseThisParticipant (0.5);
	
		} # endelsif
		else {#do nothing
		} #end else



return $allocationchosen;


} #end subroutine DoMinimisationAndAllocation 



#------------------------make one line for writing to file--------------

sub MakeArrayOneLine {
#make one line for writing to file
#$thisarray=$_[0];
$newline ="";
$lengthoflocalarray=@localarray;
$i=0;

while ($i<$lengthoflocalarray) {

	$newline=$newline.$localarray[$i]." zz ";
	$i++;
	}#end while

} #end subroutine

#--------------alter participant array with result of allocation--------

sub ReviseParticipantArrayWithResult {

$choiceofoutcome=$_[0];

if ($choiceofoutcome eq "option1") {
	$localarray[$numberofclasses+1]=1;
	$localarray[$numberofclasses+2]=0;
	}#endif
	else	{
	$localarray[$numberofclasses+2]=1;
	$localarray[$numberofclasses+1]=0;
	}#endelse


} #end subroutine

#--------------will do randomisation to the extent that it is required-------------

sub RandomiseThisParticipant  {
#takes two options and input provides the probability of option1 where 1 is 100% probability of option 1
#subroutine is supplied with the extent of randomisation required

$probabilityofoption1n=$_[0];

$randomiseresult = int(rand 10000);

$threshold = $probabilityofoption1n*10000;

if ($randomiseresult < $threshold) {
	$selection ="option1"
	}#endif
	else {
	$selection ="option2";
	}#endelse


return $selection ;

} #end subroutine



#--------------------make an array of the data from the form--------------
sub MakeArrayFromInputData {
# uses the form input to make an array of the data of the form 
#elements 0 1 2 3 4 5 6 7 8 9 10 11 12 13 
#contents participant ID [0], GenderMale[1], GenderFemale[2], AgeYoung[3], AgeOld[4], NonDiabetic[5], Diabetic [6], ControlGroup[7], ExperimentalGroup[8], Day[9], Month[10], Year[11], Age[120
# set everything in the array to zero
foreach $item(@localarray) {
	$item=0;
	} #end foreach

#now set values from the input values

$localarray[0]=$participantidn;

if ($gendern eq "male") {
	$localarray[1]=1;
	$localarray[2]=0;
	}#endif
	else {
	$localarray[2]=1;
	$localarray[1]=0;
	}#endelse

if ($agen < $agethreshold) {
	$localarray[3]=1;
	$localarray[4]=0;
	} #endif
	else	{
	$localarray[4]=1;
	$localarray[3]=0;
	}#endelse

if ($diabeticn eq "nondiabetic") {
	$localarray[5]=1;
	$localarray[6]=0;
	} #endif
	else	{
	$localarray[6]=1;
	$localarray[5]=0;
	}#endelse

if ($ethnicityn eq "white") {
	$localarray[7]=1;
	$localarray[8]=0;
	$localarray[9]=0;
	$localarray[10]=0;

	} #endif
	elsif ($ethnicityn eq "black")	{
	$localarray[7]=0;
	$localarray[8]=1;
	$localarray[9]=0;
	$localarray[10]=0;

	}#endelsif

	elsif ($ethnicityn eq "asian")	{
	$localarray[7]=0;
	$localarray[8]=0;
	$localarray[9]=1;
	$localarray[10]=0;

	}#endelsif

elsif ($ethnicityn eq "chinese")	{
	$localarray[7]=0;
	$localarray[8]=0;
	$localarray[9]=0;
	$localarray[10]=1;

	}#endelsif



$localarray[11] = 0;
$localarray[12] = 0;
$localarray[13] = $dayn;
$localarray[14] = $monthn;
$localarray[15] = $yearn;
$localarray[16] = $agen;


} #end subroutine

#--------------set up the emails to send out------------------

sub SendEmails {

#note this subroutine does require data input from the form. 
# strip formatting out of statement of allocation
# the next two lines remove html formatting from the text describing the outcome <u> and </u>
$localtextoutcome=$textoutcome;
$localtextoutcome=~ s/<?\/?u>//g;

#calculate the total number of participants allocated,including this new person by adding 1 to the length 
#of the array that was read in from the file of previous allocations
$totalnumberofparticipantsnow=$lengthoffilearray + 1;

$emailsubject ="Allocation on $dayn $monthn $yearn";
$replytowriter="Dear Researcher 

Thank you for submitting your study allocation request on 
$weekdayn $dayn/$monthn/$yearn at $currenttime.
Note this is GMT - add one hour if the hour has gone forward for British Summer Time (BST)
If the time in this email is 20:55 that will be 21:55 during BST.\n

The submitted data are below:

Participant ID: $participantidn
Age: $agen
Gender: $gendern
Ethnicity category: $ethnicityn
Diabetic status: $diabeticn

Your request has been accepted and this participant has been allocated to the $localtextoutcome.

If there is a problem or error please email $administratoremail immediately. Do not reply to this email as the email address will not reach anyone. 

This participant is the  $totalnumberofparticipantsnow th/st/rd participant to be allocated.
The total number of participants previously allocated to the control arm is $option1total.
The total number of participants previously allocated to the interventional arm is $option2total.

Best wishes,

The Allocation Script";


$replytostudynurse="Dear Study Nurse, 

This email is to inform you that a study allocation request was made on 
$weekdayn $dayn/$monthn/$yearn at $currenttime.
Note - this is GMT - add one hour if the hour has gone forward for British Summer Time (BST)
If the time in this email is 20:55 that will be 21:55 during BST.\n

The submitted data are below:

Participant ID: $participantidn
Age: $agen
Gender: $gendern
Ethnicity category: $ethnicityn
Diabetic status: $diabeticn

The request was accepted and this participant has been allocated to the $localtextoutcome.

If there is a problem or error please email $administratoremail immediately. Do not reply to this email as the email address will not reach anyone.

For your information, this participant is the  $totalnumberofparticipantsnow th/st/rd participant to be allocated.
The total number of participants previously allocated to the control arm is $option1total.
The total number of participants previously allocated to the interventional arm is $option2total. 

Best wishes,

The Allocation Script";

$subjectlineforadmin="Allocation submission";
$textforadmin="Dear Admin, thank you. ";

$mailcontentforadministrator="Dear Administrator,

An allocation was requested on
$weekdayn $dayn/$monthn/$yearn at $currenttime.
Note - this time is GMT - add one hour if the hour has gone forward for British Summer Time (BST)
ie if the time in this email is 20:55 that will be 21:55 during BST \n

The submitted data are below:

Participant ID: $participantidn
Age: $agen
Gender: $gendern
Ethnicity category: $ethnicityn
Diabetic status: $diabeticn


This participant has been allocated to the $localtextoutcome.

The data line for this participant is below. 
$newparticipantline

This participant is the  $totalnumberofparticipantsnow th/st/rd participant to be allocated.
The total number of participants previously allocated to the control arm is $option1total.
The total number of participants previously allocated to the interventional arm is $option2total.

The preceding dataset is 
@filearray 

Best wishes, 

The Allocation Script";


}

#end of subroutine


#-------------------

sub MakeHtmlPageSucces {
#---------make html page to output-------------------------

#now convert perl new line into html new lines
$contents=~ s/\n/\<br>/g;


#create title and header
$pagetitle= "Allocation Summary"; 
$header= "Allocation Summary";

&Header($header);
print<<"bodytext";
<body bgcolor="#FFFFFF">
<p align="center"><b><font face="Verdana, Arial, Helvetica, sans-serif" size="+4" color="#0000FF">Allocation Successful</font></b></p>

<p align="left"><b><font face="Arial, Helvetica, sans-serif" size="+2" color="#004080">Allocation Summary</font> </b></p>

<P>Thank you for your request to allocate a participant to this study</p>
<p>
<p>
<p>This is a summary of your request. Please check the details for any errors. 
<p>If there are any errors, please email the chief investigator now. 

<p><b>The data you submitted for allocation are :</b> </p>
<p><b>Participant ID:</b> $participantidn</p>
<p><b>Age:</b> $agen</p>
<p><b>Gender:</b> $gendern</p>
<p><b>Ethnicity category:</b> $ethnicityn</p>
<p><b>Diabetic status:</b> $diabeticn</p>

<p><b>Your email address:</b> $submitteremailn</p>



<p>The result of the allocation process is on the next line. </p>


<p align="left"><b><font face="Arial, Helvetica, sans-serif" size="+2" color="#004080">This participant is allocated to the $textoutcome</font> </b></p>


<p>You will receive email verification of this allocation. </p>
<p>If you do not, then please contact the chief investigator as you may have submitted an incorrect email address. </p>  


bodytext
&Footer;


}






#-------------the subroutines below here do not alter variables in teh mian programme and are really independent functions
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
#unhash this section to print out the names and values
#print "Content-type: text/html\n\n";
#foreach $key (sort keys(%formdata)) {
#       print "<P>The field named <B>$key</B> contained
#<B>$formdata{$key}</B>";
#}
}

sub GetMonthLength {

$monthinquestion=$_[0];
$yearinquestion=$_[1];


#determine the length of the month includes leap years

if ($monthinquestion == 2){
$monthinquestionlength=28;
if (($yearinquestion==2012)||($yearinquestion==2012)||($yearinquestion==2016)||($yearinquestion==2020)||($yearinquestion==2024)||($yearinquestion==2028)||($yearinquestion==2032)||($yearinquestion==2036)){
$monthinquestionlength=29;
}
}
elsif (($monthinquestion == 4)||($monthinquestion == 6)||($monthinquestion == 9)||($monthinquestion ==11))
{
$monthinquestionlength=30;
}
else {
$monthinquestionlength=31;
}

return $monthinquestionlength;

}

sub GetDayofYear {

$dayinquestion=$_[0];
$monthinquestion=$_[1];
$yearinquestion=$_[2];

@monthstartdays =(0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334);
$yeardayinquestion=$monthstartdays[$monthinquestion]+$dayinquestion;

$compositeyeardayinquestion=$yeardayinquestion+($yearinquestion*365);


#return ($yeardayinquestion);
return ($yeardayinquestion, $compositeyeardayinquestion);

}


#--------------------------------write files------------------

sub FileWrite {

$textlinetowrite=$_[0];
$filename=$_[1];

open(LIST, ">>$filename") ||&Erromessage("LIST file unavailable at $filename");
flock(LIST, 2);
print LIST "$textlinetowrite\n";
#print LIST "$textlinetowrite";
flock(LIST, 8);
close(LIST);
}

#-------------make header for html page-----------------
sub Header {

  print "Content-type: text/html\n\n";
  print "<HTML><HEAD><TITLE>";
  print "$_[0]";
  print "</TITLE></HEAD><body bgcolor=#FFFFFF>\n";

}

#-------------make error message-----------------
sub Errormessage {
print "Content-type: text/html\n\n";
print "An error has occurred.
<P>$_[0] \n";
print "Please inform webmaster at learndoctor.com";
exit;
}


#-------------make footer for html page-----------------
sub Footer {


print<<"signature";
<hr>
<ADDRESS>

C.A.O'Callaghan : revised 2013
</ADDRESS>
signature

print "\n</BODY></HTML>";
}



