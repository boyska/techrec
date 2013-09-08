<?php

# DEFAULT VALUES FOR FORMS
define("DEFAULT_TITLE", "Undefined");
define("DEFAULT_DESC", "");
define("DEFAULT_START", "");
define("DEFAULT_END", "");
define("VER", "0.1");

# SQLITE DB PARAMETER
define("DEFAULT_DBNAME", "registrazioni.sqlite");

# VARIABLES 2 DAEMON
define("FIFO_DIR", "/tmp/rorrec/");
define("AUDIO_DIR", getcwd()."/files/");
define("AUDIO_DIR_R", "./files/");
define("GUI_WEB_URI", "");

function mymessage($s) { myprint("message", $s); }

function myerror($s) { myprint("error", $s); }

function myprint($type, $s) {
    print "<div class=\"info $type\"> ". 
        $s
        ."</div>";
}


function data2file($filename, $content)
{
	if (! is_writable( dirname($filename) )) {
		print "Non scrivibile (".dirname($filename).")<br>";
		return FALSE;
	}

	if (!$handle = fopen($filename, 'w')) {
		print "Cannot open file ($filename)<br>";
		return FALSE;
	}
	
	if (fwrite($handle, $content) === FALSE) {
	  	print "Cannot write to file ($filename)<br>";
		return FALSE;
	}	

	fclose($handle);
	return TRUE;	
}

function array2yamlfile( $r, $fname ) {
    //TODO: Gestione errori
    $sYAMLdata = yaml_emit ( $r );
    echo "write to ".$fname;
    $fp = fopen ( $fname, 'w' );
    fwrite ( $fp, $sYAMLdata );
    fclose ( $fp );
}

?>
