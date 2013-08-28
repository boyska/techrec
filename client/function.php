<?
include_once("utils.php");

/*
* API HELP
*/
function help() {
    print "<div>
            <div> TechreAPI (ver ".VER."): <b>HELP</b> <div/>
            <div> install()<div/>
            <div> new()<div/>
            <div> del()<div/>
            <div> update()<div/>
            <div> search()<div/>
        <div/>";
}
    
    
/*
* DBSQLITE CONNECT
*/
function connect( ) {
    try {
	    $db =  new SQLite3( DEFAULT_DBNAME , SQLITE3_OPEN_READWRITE | SQLITE3_OPEN_CREATE );
    } catch (Exception $e) {
       myerror("Unable to open DB ". DEFAULT_DBNAME .". (".$e->getMessage().")\n");
       return Null;
    }
    return $db; 
}


/* DBSQLITE DISCONNECT */
function disconnect( $db ){  if ($db) $db->close(); }

/*
* INSTALLAZIONE DEL NUOVO DB 
*/
function rec_install( $db ) {
    $sqlstring = "CREATE TABLE IF NOT EXISTS registrazioni (
		    id INTEGER PRIMARY KEY,
		    starttime DATE,
		    endtime DATE, 
		    stopped boolean DEFAULT 0,
		    extracted boolean DEFAULT 0,
		    title varchar(500),
		    outfile text
	    )";
		
    if ( ($res = $db->exec( $sqlstring )) == FALSE ) { 
        myerror("impossibile installare"); exit; 
    }
}


/* 
* CREO NUOVA REGISTRAZIONE 
*/
function rec_new($db, $p) {

    $title      = ( isset($p['title']) ) ? $p['title'] : DEFAULT_TITLE;
    $starttime  = ( isset($p['starttime'] ) ) ? $p['starttime'] : DEFAULT_START;
    $endtime    = ( isset($p['endtime']) ) ? $p['endtime'] : DEFAULT_END;

 	if ( $starttime == DEFAULT_START ) {
 		$starttime = date("Y/m/d H:i" );
    }

    $sqlstring = "INSERT into registrazioni (title,starttime,endtime) 
			    VALUES ('$title','$starttime','$endtime')";

    try {
	    $db->exec($sqlstring);
	    mymessage("Informazioni registrate");
    } catch (Exception $e) {
   	    myerror("Errore registrazione informazioni". $e->getMessage() .")\n");
    }
}

/* 
* CANCELLA UNA REGISTRAZIONE 
*/
function rec_del( $db, $id ) {
	$sqlstring = "DELETE from registrazioni where id='$id'";

	if ( ($result = $sq->exec($sqlstring)) == FALSE) {
		myerror("Impossibile cancellare");	
	} else {
		mymessage("Registrazione correttamente cancellata!");	
	}
}

/* 
* MODIFICA UNA REGISTRAZIONE 
*/
function rec_update( $db, $p ) {

    $id      	= $p['id'];
	$title      = $p['title'];
    $starttime  = $p['starttime'];
    $endtime = ( $p['endtime'] == DEFAULT_END) ? date("Y/m/d H:i") : $endtime = $p['endtime'] ;

	$sqlstring = "UPDATE registrazioni 
					set title = '$title', starttime = '$starttime', endtime = '$endtime', stopped=1 
					where id='$id'";
		
	if ( ($result = $db->exec($sqlstring)) == FALSE) {
		myerror("Impossibile Modificare i contenut ($sqlstring)");		
	} else {
		mymessage("Aggiornamento eseguito");	
	}
}

/* 
* ESTRAI UNA REGISTRAZIONE 
*/
function rec_extract( $db, $p ) {

    // Get values from form
    $id      	= $p['id'];
	$title      = $p['title'];
    $starttime  = $p['starttime'];
    $endtime    = $p['endtime'];
    
    $outfile 	= AUDIO_DIR."/".date("Y")."-".date("m")."/".date("d")."/".$title."-".date("U").".mp3";
	$content = "s=\"$starttime\"\ne=\"$endtime\"\noutfile=\"$outfile\"\n";
	$outfile_rel = AUDIO_DIR_R."/".date("Y")."-".date("m")."/".date("d")."/".$title."-".date("U").".mp3";
	
	#s="2013/03/31 18:37"
	#e="END"
	#outfile="mimmo.mp3"
	
	if ( data2file( FIFO_DIR . "/$title.fifo", $content ) ) {
		$sqlstring = "UPDATE registrazioni set outfile = '$outfile_rel ' , extracted = 1 where id='$id'";
		if ( ($result = $db->exec($sqlstring)) == FALSE) {
			myerror( "Impossibile segnare come fermata");		
		} 
		mymessage( "Registrazione in processamento ma non segnalata come fermata ($sqlstring)");		
	} else {
		myerror("Impossibile SALVARE la richiesta");		
	}
}

/* 
* CERCA UNA REGISTRAZIONE 
*/
function rec_get($db, $p) {

    $order = "starttime desc";

    # qui c'e' il bug perche' passo in input "starttime desc" e questo non viene rilevato

    // if ( isset($p['sort']) && in_array($p['sort'],  array("starttime","endtime","title")  ) ) {
    
    if ( isset($p['sort']) ) { 
	    $order =  $p['sort'];	
    } 
    
    $sqlstring = "SELECT * 
                FROM registrazioni 
                ORDER BY $order";

    // debug purposes            
    myerror($sqlstring);

    if ( ($result = $db->query( $sqlstring )) == FALSE) {
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
    
    print "</table>";
}
?>


