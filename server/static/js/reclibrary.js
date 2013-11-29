console.log("Loading...");

function trx_startbut( code )  { return "startbutton-"+code; }
function trx_stopbut( code )   { return "stopbutton-"+code; }
function trx_downbut( code )   { return "downloadbutton-"+code; }
function trx_endbut( code )      { return "endbutton-"+code; }

function trx_logarea( code )   { return "logarea-"+code; }

function rs_button( code )     { return "button"+code; }

function rs_trxarea( code )    { return "recarea-"+code; }
function rs_trxname( code )    { return "name"; }
function rs_buttonarea( code ) { return "butarea-"+code; }
function rs_inputstart( code ) { return "starttime"; }
function rs_inputend( code )   { return "endtime"; }
function rs_formid(code)       { return "form-"+code; }
function rs_dellink(code)       { return "dellink-"+code;}
function rs_id(code)           { return code; }

var txt_start       = "Inizia";
var txt_stop        = "Ferma";
var txt_download    = "Scarica";

var srvaddr         = "/";

var almostone       = false;
var noplusbotton    = true;

var rec_name_default = "";

/*
TODO: cambiare logica
Quando premo il primo tasto, faccio la crazione,
per ogni altro pulsante, faccio solo e sempre UPDATE
*/
/**
  * Perform Ajax async loading
  **/

function newformstr ( recid , butflag=false )
{
    var formid = rs_formid( recid );
    var str = "<form id=\""+formid+"\" name=\""+formid+"\" action=\"#\">";

    if (butflag) {
        str = str + "<input type=\"button\" name=\""+trx_startbut(recid)+"\" id=\""+trx_startbut(recid)+"\" ";
        str = str + " class=\"recbutton\" value=\"Inizia\" />";
        str = str + "<input type=\"button\" name=\""+trx_stopbut(recid)+"\" id=\""+trx_stopbut(recid)+"\" ";
        str = str + " class=\"recbutton\" value=\"Stop\" />";
        str = str + "<input type=\"submit\" name=\""+trx_downbut(recid)+"\" id=\""+trx_downbut(recid)+"\" ";
        str = str + " class=\"recbutton\" value=\"Salva\" />";
        str = str + "<input type=\"submit\" name=\""+trx_endbut(recid)+"\" id=\""+trx_endbut(recid)+"\" ";
        str = str + " class=\"recbutton\" value=\"Download\" />";
    }

    str = str + "<input type=\"hidden\" id=\"recid\" name=\"recid\" value=\""+recid+"\" />";
    str = str + "<input type=\"text\" id=\""+rs_trxname(recid)+"\" name=\""+rs_trxname(recid)+"\" />";
    str = str + "<input type=\"text\" id=\""+rs_inputstart(recid)+"\" name=\""+rs_inputstart(recid)+"\" />";
    str = str + "<input type=\"text\" id=\""+rs_inputend(recid)+"\" name=\""+rs_inputend(recid)+"\" />";

    if (! butflag) {
        str = str + "<input type=\"button\" name=\""+trx_downbut(recid)+"\" id=\""+trx_downbut(recid)+"\" ";
        str = str + " class=\"downloadbutton\" value=\"scarica\" />";
    }
    /*
    str = str + "<input type=\"text\" id=\"name\" name=\"name\" />";
    str = str + "<input type=\"text\" id=\"starttime\" name=\"starttime\" />";
    str = str + "<input type=\"text\" id=\"endtime\" name=\"endtime\" /> ";
    */
    str = str + "</form>";

    return str;
}

/**
*  GetActive Recs
**/

function rec_active( recid ) {
    dataString = "";
    var request = RecAjax("search", dataString);

    request.done( function(data) {
        $.each(data, function(key, val) {
            console.log("Key " + key + " > VAL " + val );
            $("#"+trx_logarea( recid )).append( "Key " + key + " > VAL " + val + "<br>"  );
        });

        console.log("Req OK: "+ data);
        // console.log("request"+ req);
        ChangeState(recid, trx_downbut(recid) , trx_endbut(recid));
    });
}


/**
  *  New record
  **/
function rec_new( )
{

    var myDate = new Date()
    console.log("New ID "+ myDate.getTime());
    var recid = "rec-"+ myDate.getTime();

    console.log("[rec_new] New Rec " + recid);

    $("#buttonscontainer").append( "<div id=\""+rs_trxarea(recid)+"\" class=\"recarea\"> </div>" );
    $("#"+rs_trxarea(recid)).append( "<div id=\""+rs_buttonarea(recid)+"\" class=\"buttonarea\"> </div>" );
    console.log("[rec_new"+recid+"] add div (TRXArea, ButtonArea) ok " );

    var formid = rs_formid( recid );

    var str = newformstr(recid, butflag=true);
    $("#"+rs_buttonarea(recid)).append( str );

    $("#"+trx_stopbut(recid)).hide();
    $("#"+trx_downbut(recid)).hide();
    $("#"+trx_endbut(recid)).hide();

    console.log("[rec_new "+recid+"] Form OK");

    $("#"+rs_buttonarea(recid)).append( "<div class=\"dellinkarea\" > <a href=\"#\" id="+rs_dellink(recid)+"> cancella</a> </div>" );

    // INSERT AND POPULATE BUTTON AREA
    $("#"+rs_trxarea(recid)).append( "<div id=\""+trx_logarea(recid)+"\" class=\"logarea\"> Nuova trasmissione </div>" );

    // Bind the Delete Links
    $("#"+rs_dellink(recid)).click(function(){
        console.log("Remove " + rs_trxarea(recid) + "[ID"+recid+"]");
         // $("#"+rs_trxarea(recid)).remove();
        recDelete (recid,rs_trxarea(recid));
    });

    // FORM SUBMIT: THE REC IS STOPPEND AND MUST BE PROCESSED
    $("#"+formid).submit(function(event){
        // Immediately, mark the end time (stop action)
        ChangeState(recid, trx_downbut(recid) , trx_endbut(recid));

        // Force a Name
        while (true) {
            if ( $("#"+rs_trxname(recid)).val() == "" )
            {
                var tmpname = prompt("Nessun nome di trasmissione!!!");
                $("#"+rs_trxname(recid)).val(tmpname);
                $("#"+trx_logarea(recid)).append("Titolo: <b>"+ tmpname +"</b> <br/>");
            }
            else { break; }
        }

        event.preventDefault();

        // Update data (send to server) in order to save some information
        recUpdate(recid);

        recStart(recid);

    }); // End of form SUBMIT

    // Bind the STOP button
    $("#"+trx_stopbut(recid)).click( function(event){

        event.preventDefault();
        ChangeState(recid, trx_stopbut(recid) , trx_downbut(recid));
        recUpdate(recid);

    }); // End of STOP button

    // Bind the START button
    $("#"+trx_startbut(recid)).click( function(event){

        // Immediately, mark the start time (start action) and send it to Server
        ChangeState(recid, trx_startbut(recid) , trx_stopbut(recid));
        event.preventDefault();
        recNew( recid );

    }); // End of START button

    console.log("New form has been built.");
}

/* Delete Record */
function recDelete ( recid, targetarea ) {
    var formid = rs_formid( recid );
    var dataString = "recid="+recid

    console.log("Del rec: "+dataString);
    var req_del = RecAjax("delete", dataString);

    req_del.done (function(data) {
        $.each(data, function(del_key, del_val) {
            console.log("K:V " + del_key +":"+del_val );

            if (del_key == "message") {
                $("#"+targetarea).fadeOut( 200, function() { $(this).remove(); });
                console.log("delete area "+rs_trxarea(key));

            }

            if (del_key == "error") {
                alert("Impossibile cancellare elemento:\n" + del_val );
            }

        });
    });
}

/* New Record */
function recNew ( recid ) {
    var formid = rs_formid( recid );
    var dataString = $("#"+formid).serialize();

    console.log("New rec: "+dataString);

    var request = RecAjax("create", dataString);

    request.done( function(data) {
        $.each(data, function(key, val) {
            console.log("Received (K:V) ("+key+":"+val+")") ;
            if (key == "msg") {
                $("#"+trx_logarea(recid)).html("Nuova Registrazione </br> (recid:"+recid+") </br>");
                $("#"+trx_logarea(recid)).append("Inizio: "+ $("#"+rs_inputstart(recid)).val() +"<br/>");
            }
            if (key == "error") {
                $("#"+trx_logarea( recid )).html("Errore: impossibile creare una nuova registrazione"+val+" </ br>");
            }

        });
    } );
    return request;
}

/* Update Record */
function recUpdate( recid  ) {
    var formid = rs_formid( recid );
    var dataString = $("#"+formid).serialize();
    console.log("Sending Ajax Update request: "+ dataString);

    //event.preventDefault();
    var request = RecAjax("update", dataString );
    request.done( function(data) {
        $.each(data, function(key, val) {
            console.log("recUpdate receive (k:v) ("+key+":"+val+")" );

            if (key == "message") {
                var str = "";
                str += "<b>RecID</b> "+ recid + "</br>"
                str += "<b>nome</b> "+ $("#"+rs_trxname(recid)).val() + "</br>"
                str += "<b>Inizio</b> "+ $("#"+rs_inputstart(recid)).val() + "</br>"
                str += "<b>Fine</b> "+ $("#"+rs_inputend(recid)).val() + "</br>"

                $("#"+trx_logarea(recid)).html( str );
                // if all elements have been recorded
                if ($("#"+rs_trxname(recid)).val() != "") {
                    $("#"+trx_logarea(recid)).append( "<b>In Elaborazione</b>" );
                }
            }

            if (key == "error") {
                $("#"+trx_logarea( recid )).append( "Error:" + val +"<br>"  );
            }
        }); // end of each
    }); // end of request.done
}

/*
 *
 *  AJAX REQUEST
 *
 */
function RecAjax(apipath, dataString ) {
    var srv = srvaddr + "api/" + apipath ;
    var request = $.ajax({
        type: "POST",
        cache: false,
        url: srv,
        data: dataString,
        dataType: "json"
    });

    request.fail(function (jqXHR, textStatus, errorThrown){
        console.error("The following error occured: "+ jqXHR.status +"-"+ textStatus + "-" + errorThrown );
        if (jqXHR.status == 0 && jqXHR.readyState === 4)
        {
            alert("Errore di connessione, impossibile inviare i dati al server "+ srv);
        } else {
            alert("Error: "+jqXHR.status +"\nTextStatus: "+ textStatus + "\n Ready State "+jqXHR.readyState+"\n" + errorThrown );
        }
    });

    return request;
}

/*
 *  GetNow (data parser)
 */
function getnow()
{
    var myDate = new Date()
    var displayDate = myDate.getFullYear() + '/' + (myDate.getMonth()+1) + '/' + myDate.getDate();
    displayDate = displayDate +' '+ myDate.getHours()+':'+myDate.getMinutes()+':'+myDate.getSeconds();
    return displayDate;
}

/*
FUNCTION: CHANGE STATE (gui)
*/
function ChangeState(recid, from, to) {

  console.log("ChangeState: " + from + " --> " + to );

  $("#"+from).css("display", "none");
  $("#"+to).css("display", "inline");

  // take the date
  var displayDate = getnow();

  if ( from == trx_startbut(recid) ) {
    $("#"+rs_inputstart(recid)).val( displayDate );

    console.log("ChangeState: set "+rs_inputstart(recid)+ " to "+ displayDate )
  }

  if ( from == trx_stopbut(recid) ) {
    $("#"+rs_inputend(recid)).val( displayDate );
    console.log("ChangeState: set '"+rs_inputend(recid)+ "' to "+ displayDate )
  }

  if ( from == trx_downbut(recid) ) {
    $("input[type=submit]").attr("disabled", "disabled");
    console.log("ChangeState: set '"+rs_inputend(recid)+ "' to "+ displayDate );
  }
} // End function ChangeState

// vim: set ts=4 sw=4 et:
