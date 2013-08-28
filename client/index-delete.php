<?
// phpinfo();
// exit;
include_once("utils.php");
?>

<html>

<head>
<!--[if lt IE 9]>
    <script src="jquery-1.9.1.min.js"></script>
<![endif]-->

<!-- <meta http-equiv="refresh" content="30;url=https://techrec.ondarossa.info/index.php"> --> 

<link rel="stylesheet" type="text/css" href="style.css">
</head>

<body>

<div class="message">
Le registrazioni antecendeti a dom 14 apr 2013, 23.00.00 non sono
disponibili.
</div>

<!-- PAGE CONTAINER -->
<div class="pagecontainer">

    <div class="newrec">
        <form action="index.php" method=POST>
            <input type="hidden" name="op" value="new">
            <input type="hidden" id="starttime" name="starttime" value="<? echo DEFAULT_START?>" />
    	      <input type="hidden" id="endtime" name="endtime" value="<? echo DEFAULT_END?>" />
    	      <div class="fieldtitle">
    	      	<p>titolo della registrazione</p>
    	        <input type="text" id="title" name="title" value="<? echo DEFAULT_TITLE?>" />            
            </div>
            <input type="submit" value="start now!" class="startbutton" />
        </form>
    </div>

<?php

/*  DB SQLITE CONNECTION  */

try {
	$sq =  new SQLite3( DEFAULT_DBNAME , SQLITE3_OPEN_READWRITE | SQLITE3_OPEN_CREATE );
	// $sq->open( DEFAULT_DBNAME , SQLITE3_OPEN_READWRITE);
} catch (Exception $e) {
   myerror("Unable to open DB ". DEFAULT_DBNAME .". (".$e->getMessage().")\n");
   exit;
}

# http://www.sqlite.org/datatype3.html

/* INSTALALZIONE DEL NUOVO DB */
$sqlstring = "CREATE TABLE IF NOT EXISTS registrazioni (
		id INTEGER PRIMARY KEY,
		starttime DATE,
		endtime DATE, 
		stopped boolean DEFAULT 0,
		extracted boolean DEFAULT 0,
		title varchar(500),
		outfile text
		)";
		
if ( ($res = $sq->exec( $sqlstring )) == FALSE ) {
		myerror("impossibile installare");
		exit;
}

$title      = ( isset($_POST['title']) ) ? $_POST['title'] : DEFAULT_TITLE;
$starttime  = ( isset($_POST['starttime']) ) ? $_POST['starttime'] : DEFAULT_START;
$endtime    = ( isset($_POST['endtime']) ) ? $_POST['endtime'] : DEFAULT_END;

/* 
* CREO NUOVA REGISTRAZIONE 
*/

if ( isset($_POST['op']) && $_POST['op'] === "new" ) {

   //print "NewFile...".FIFO_DIR."/$title<br/>";

   # esempio:
   # s="2012/02/14 10:20" 
	# e="2012/02/14 11:15" 
	# outfile="cross-55.mp3"
	
 	if ( $starttime == DEFAULT_START ) {
 		$starttime = date("Y/m/d H:i" );
	}

	$sqlstring = "INSERT into registrazioni (title,starttime,endtime) 
				VALUES ('$title','$starttime','$endtime')";
	
	try {
		$sq->exec($sqlstring);
		mymessage("Informazioni registrate");
	} catch (Exception $e) {
   	    myerror("Errore registrazione informazioni". $e->getMessage() .")\n");
	}
}

/* 
* FERMO UNA NUOVA REGISTRAZIONE 
*/
/*
if ( isset($_GET['op']) && isset($_GET['stop']) &&  $_GET['stop'] == "stop" ) {
	
    print "QUIIIII" ;
	$id      = $_GET['id'];
	// end time = NOW!

    if ( $_GET['endtime'] == DEFAULT_END) {
    	$endtime = date("Y/m/d H:i");
    } else {
    	$endtime = $_GET['endtime'] ;
    }
	
	$sqlstring = "UPDATE registrazioni 
					set endtime='$endtime', stopped=1
					where id='$id'";
	

	if ( $sq->exec($sqlstring) == FALSE ) {
		myerror("Impossibile Terminare la registrazione ($sqlstring)");	
	} else {
		mymessage("Registrazione fermata!");	
	}
}
*/

/* 
* CANCELLA UNA REGISTRAZIONE 
*/
if ( isset($_GET['op']) && isset($_GET['delete']) &&  $_GET['delete'] == "cancella" ) {

	$id      	= $_GET['id'];
	
	$sqlstring = "DELETE from registrazioni where id='$id'";

	if ( ($result = $sq->exec($sqlstring)) == FALSE) {
		myerror("Impossibile cancellare");	
	} else {
		mymessage("Registrazione correttamente cancellata!");	
	}
}

/* 
* MODIFICA / FERMA UNA REGISTRAZIONE 
*/
/* print "OP". $_GET['op']."<br/>";
print "UPDATE". $_GET['update']."<br/>";
print "STOP". $_GET['stop']."<br/>";
*/
if (isset($_GET['op']) && ( $_GET['op'] == "update" )) 
    {

    // Anyway, update!

    // Get values from form
    $id      	= $_GET['id'];
	$title      = $_GET['title'];
    $starttime  = $_GET['starttime'];
    $endtime = ( $_GET['endtime'] == DEFAULT_END) ? date("Y/m/d H:i") : $endtime = $_GET['endtime'] ;

	$sqlstring = "UPDATE registrazioni 
					set title = '$title', starttime = '$starttime', endtime = '$endtime', stopped=1 
					where id='$id'";
		
	if ( ($result = $sq->exec($sqlstring)) == FALSE) {
		myerror("Impossibile Modificare i contenut ($sqlstring)");		
	} else {
		mymessage("Aggiornamento eseguito");	
	}
}

/* 
* ESTRAI UNA REGISTRAZIONE 
*/
if ( isset($_GET['op']) && isset($_GET['extract']) &&  $_GET['extract'] == "estrai" ) {

    // Anyway, update!

    // Get values from form
    $id      	= $_GET['id'];
	$title      = $_GET['title'];
    $starttime  = $_GET['starttime'];
    $endtime    = $_GET['endtime'];
    $outfile 	= AUDIO_DIR."/".date("Y")."-".date("m")."/".date("d")."/".$title."-".date("U").".mp3";
	$content = "s=\"$starttime\"\ne=\"$endtime\"\noutfile=\"$outfile\"\n";
	$outfile_rel = AUDIO_DIR_R."/".date("Y")."-".date("m")."/".date("d")."/".$title."-".date("U").".mp3";
	
	#s="2013/03/31 18:37"
	#e="END"
	#outfile="mimmo.mp3"
	
	if ( data2file( FIFO_DIR . "/$title.fifo", $content ) ) {
		$sqlstring = "UPDATE registrazioni set outfile = '$outfile_rel ' , extracted = 1 where id='$id'";
		if ( ($result = $sq->exec($sqlstring)) == FALSE) {
			myerror( "Impossibile segnare come fermata");		
		} 
		mymessage( "Registrazione in processamento ma non segnalata come fermata ($sqlstring)");		
		
	} else {
		myerror("Impossibile SALVARE la richiesta");		
	}
	
	
}
?>

<!--




	Visualizzazione dati passati!
	TODO: FORM per filtrare le richieste
	



-->

<div class="resultcontainer">

<?php
	
	
	$order = "starttime desc";

    # qui c'e' il bug perche' passo in input "starttime desc" e questo non viene rilevato
    
	// if ( isset($_GET['sort']) && in_array($_GET['sort'],  array("starttime","endtime","title")  ) ) {
	if ( isset($_GET['sort']) ) { 
		$order =  $_GET['sort'];	
	} 
	$sqlstring = "SELECT * FROM registrazioni ORDER BY $order";
	myerror($sqlstring);
	
	if ( ($result = $sq->query( $sqlstring )) == FALSE) {
		myerror("Impossibile prelevare dati");	
	}

	print "
		
		<table width=\"100%\">
		<tr> 
			<td> <p> <a href=\"index.php?sort=title\">Titolo</a> (<a href=\"index.php?sort=title desc\">desc</a>)</p> </td>
			<td> <p> <a href=\"index.php?sort=starttime\">Inizio</a> (<a href=\"index.php?sort=starttime desc\">desc</a>)</p> </td>
			<td> <p> <a href=\"index.php?sort=endtime\">Fine</a> (<a href=\"index.php?sort=endtime desc\">desc</a>)</p> </td>
			<td> Stop/Aggiorna </td>
			<!-- <td> Aggiorna </td> -->
			<td> Estrai </td> 
			<td> Download </td>
			<td> Cancella </td>
		</tr>";

	while ($data = $result->fetchArray() )
	{   

	    // se e' stata stoppata (aggiornata almeno una volta) => Pulsate STOP/Aggiorna
        $stoplabel = ( $data['stopped'] == 1) ? "aggiorna" : "stop";
        $updatedisabled = ( $data['extracted'] == 1) ?  "disabled" : "";
        
        $extractiondisabled = ( $data['stopped'] == 1 && $data['extracted'] == 0 ) ? "":  "disabled" ;

		print "
			<tr class=\"rec$updatedisabled\"><form action=\"index.php\" method=\"GET\"> 
			<td><input type=\"text\" id=\"title\" name=\"title\" value=\"". $data['title'] ."\" $updatedisabled /></td>
			<td><input type=\"text\" id=\"starttime\" name=\"starttime\" value=\"". $data['starttime'] ."\" $updatedisabled /> </td>
			<td><input type=\"text\" id=\"endtime\" name=\"endtime\" value=\"". $data['endtime'] ."\" $updatedisabled /> </td>
			<td><input type=\"hidden\" name=\"op\" value=\"update\">
					<input type=\"hidden\" name=\"id\" value=\"". $data['id'] ."\">";
        
        print "<input type=\"submit\" name=\"stop\" value=\"$stoplabel\" $updatedisabled > </td>";

		// print "<td><input type=\"submit\" name=\"update\" value=\"aggiorna\" $aggiornadisabled> </td>";

		print "<td><input type=\"submit\" name=\"extract\" value=\"estrai\" $extractiondisabled> </td>";	

		if ( $data['extracted'] == 1) {
			$f = trim( str_replace( getcwd(), "", $data['outfile']) ); 
			// print "F" . $f;
            // print "OUT" . $data['outfile'];
            // print "OUT" .realpath( $data['outfile'] );
            // print "COMPLETE" . getcwd()."/".$data['outfile'] . " --- " . is_readable( $data['outfile'] ) ; 

            // if ( ($f = fopen($data['outfile'] ,'r')) !== FALSE )  {
			// if (  is_readable( getcwd()."/".$data['outfile'] ) ) {
			//if (  is_readable( $data['outfile'] ) ) {
			$finfo = pathinfo($f);
			$logfile = urlencode( $f ).".log";
			$logfile = trim($f).".log";
			
			$logcontent =  file_get_contents( $logfile , FILE_USE_INCLUDE_PATH);
			// print $logcontent;
			print "<td>";
			// print "<br>File: $f";
			// print "<br>LogFile: $logfile";
			// print "<br>logcontent: $logcontent";
			
	        if ( file_exists($f) ) {
    	        print "<a href=\"".$f."\" title=\"log: \n$logcontent\"> scarica </a>";
            } else {
			    print "<a href=\"#\" title=\"log: \n$logcontent\">..processando..</a> <br/> $f <br/> $logfile";
			}
			print "</td>";
			
		} else {
				print "<td>(estrai prima di scaricare)</td>";
        }

        print "<td><input type=\"submit\" name=\"delete\" value=\"cancella\"> </form> </td>";
		
		print "</tr>";
	}
	print "
		</table>";

	$sq->close();

?>
</div>

<div style="clear:both;"></div>

</div>

<div id="footer">
techbl*c
</div>

</body>
</html>

