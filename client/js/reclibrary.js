console.log("Loading...");

function trx_startbut( code )  { return "startbutton-"+code; }
function trx_stopbut( code )   { return "stopbutton-"+code; }
function trx_downbut( code )   { return "downloadbutton-"+code; }

function trx_logarea( code )   { return "logarea-"+code; }

function rs_button( code )     { return "button"+code; }

function rs_trxarea( code )    { return "recarea-"+code; }
function rs_trxname( code )    { return "trxname-"+code; }
function rs_buttonarea( code ) { return "endtime-"+code; }
function rs_inputstart( code ) { return "startime-"+code; }
function rs_inputend( code )   { return "endtime-"; }
function rs_formid(code)       { return "form-"+code; }

function rs_id(code)           { return code; }

var txt_start       = "Inizia";
var txt_stop        = "Ferma";
var txt_download    = "Scarica";

var srvaddr         = "http://127.0.1.1:8000/";

var almostone       = false;
var noplusbotton    = true;
var maxrec          = 0 ;

var rec_name_default = "";

/** 
  * Perform Ajax async loading 
  **/
function DELETEasync_load( destdiv, uri, postdata) {
    postdata = postdata || '';
    
    console.log("[ASYNC] " + destdiv + " <- " + uri)
    console.log( postdata );
    
    $(destdiv).html("\<div class=\"imageloader\"\> \<img src=\"img/ajax-loader.gif\" /\> \</div\>");
    console.log("Tolta uri" + uri + "NOW -> http://127.0.1.1:8000/sampleJSON");
    var request = $.ajax( { url: "http://127.0.0.1:8000/create", 
                        type:"GET", 
                        //data: postdata,
                        //dataType: 'json',
                        success :  function( msg ) {     
                                $(".imageloader").remove();
                                resmsg = "["+jqXHR.status+"]";
                                alert("Ma ci sei ?");
                                $(destdiv).append( resmsg ); 
                                },
                        error: function(xhr) { 
                                var errmsg = "";
                                console.log("Errore async ajax: " + xhr.status );
                                switch( xhr.status )
                                {
                                    case 0: errmsg="[0] Network Problem."; break;
                                    case 404: errmsg="[404] Requested page not found."; break;
                                    case 500: errmsg="[500] Internal Server Error."; break;
                                    default: errmsg="[ErrCode: "+xhr.status+"] Error uncatched!"; break;
                                }
                                console.log("ErrMSG" + errmsg);
                                $(".imageloader").remove();
                                //$(destdiv).html("Err: "+ errmsg);
                                alert("Err: "+ errmsg);
                            }                     
                        } 
      ).always(function( jqXHR ) {     
            $(".imageloader").remove();
            resmsg = "ALSWAST["+jqXHR.status+"]";
            $(destdiv).append( resmsg ); 
        }
      ).complete(
         function (jqXHR, msgstatus) {
            alert("Comlpete " +jqXHR + " - " + msgstatus);         
         }
      );
      return false;
}

    
/** 
  *  New record 
  **/
function rec_new( ) {
    var recid = "rec-"+maxrec;
    maxrec += 1;  // increment number of active record
    
    console.log("[rec_new] New Rec " + recid);

    $("#buttonscontainer").append( "<div id=\""+rs_trxarea(recid)+"\" class=\"recarea\"> </div>" );
    console.log("[rec_new] add div TRXArea "+ rs_trxarea(recid) );
    
    $("#"+rs_trxarea(recid)).append( "<div id=\""+rs_buttonarea(recid)+"\" class=\"buttonarea\"> </div>" );
    console.log("[rec_new] add div ButtonArea "+ rs_buttonarea(recid) );
    
    var formid = rs_formid( recid );

    var str = "<form id=\""+formid+"\" name=\""+formid+"\" action=\"#\">";

    str = str + "<input type=\"button\" name=\""+trx_startbut(recid)+"\" id=\""+trx_startbut(recid)+"\" ";
    str = str + " class=\"recbutton\" value=\"Inizia\" />";

    str = str + "<input type=\"button\" name=\""+trx_stopbut(recid)+"\" id=\""+trx_stopbut(recid)+"\" ";
    str = str + " class=\"recbutton\" value=\"Stop\" />";
    // ADD SUBITO TEXTBUTTON
    str = str + "<input type=\"submit\" name=\""+trx_downbut(recid)+"\" id=\""+trx_downbut(recid)+"\" ";
    str = str + " class=\"recbutton\" value=\"Scarica\" />";

    str = str + "</form>";

    
    $("#"+rs_buttonarea(recid)).append( str );
    
    $("#"+trx_stopbut(recid)).hide();
    $("#"+trx_downbut(recid)).hide();
    
    console.log("[rec_new] Hide Start Button");
    //$("#"+trx_startbut(recid)).css("display","none");
    
    
    console.log("[rec_new] add form "+ formid );
    
    
    $("#"+rs_buttonarea(recid)).append( "\<div class=\"dellink\" \> <a href=\"#\"> cancella</a> \</div\>" );

    // INSERT AND POPULATE BUTTON AREA
    $("#"+rs_trxarea(recid)).append( "<div id=\""+trx_logarea(recid)+"\" class=\"logarea\">Nuova trasmissione </div>" );
    
    $("#"+trx_startbut(recid)).click(function(){
        ChangeState(recid, trx_startbut(recid) , trx_stopbut(recid));
    });

    $("#"+trx_stopbut(recid)).click(function(){
        ChangeState(recid, trx_stopbut(recid) , trx_downbut(recid));
    });
    
    // $("#"+trx_downbut(recid)).submit(function(e){
    $("#"+formid).submit(function(event){
      
        event.preventDefault();
        dataString = $(this).serialize();
        alert("Mando:" + dataString);
        var request = $.ajax({
          type: "POST",
		  cache: false,
          url: "http://127.0.0.1:8000/create",
          data: dataString,
          dataType: "json"
          });
        
        request.done( function(data) { 	
						 $.each(data, function(key, val) {
								console.log("Key " + key + " > VAL " + val );
								$("#"+trx_logarea( recid )).append( "Key " + key + " > VAL " + val + "<br>"  );
						});

						console.log("Req OK: "+ data); 
						console.log("req"+ request);
					} );

		request.fail(function (jqXHR, textStatus, errorThrown){

	       console.error("The following error occured: "+
		      jqXHR.status, +"-"+ textStatus + "-" + errorThrown
    	   );
        });

    });
    
    console.log("Form readyReady");
}

function ChangeState(eid, from, to) {
  
  console.log("ChangeState: " + from + " --> " + to );
  
  $("#"+from).css("display", "none");
  $("#"+to).css("display", "inline");

  // take the date
  var myDate = new Date()
  var displayDate = (myDate.getMonth()+1) + '/' + (myDate.getDate()) + '/' + myDate.getFullYear();
  displayDate = displayDate +' '+ myDate.getHours()+':'+myDate.getMinutes()+':'+myDate.getSeconds();
  
  var formid = rs_formid( eid );
  var logdiv = trx_logarea( eid );
  
  if ( from == trx_startbut(eid) ) {
    var str = "<input type=\"text\" id=\""+rs_inputstart(eid)+"\" name=\""+rs_inputstart(eid)+"\" value=\""+displayDate+"\" />";
    $("#"+formid).append( str );
    $("#"+logdiv).append("<br/>Inizio: "+ displayDate);
  }
  
  if ( from == trx_stopbut(eid) ) {
    var str = "\<input type=\"text\" id=\""+rs_inputend(eid)+"\" name=\""+rs_inputend(eid)+"\" value=\""+displayDate+"\" /\>";
    $("#"+formid).append( str );
    $("#"+logdiv).append("<br/>Fine: "+ displayDate);
  }

} // End function ChangeState
