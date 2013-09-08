<!DOCTYPE html>
<html>

<?php
include "utils.php";
?>

<head>

<title> TechREC :: macchina del tempo</title>
<script src="jquery-1.9.1.min.js"></script>
<link rel="stylesheet" type="text/css" href="style.css">

<script>
    // fetch record
    function fetch_rec( outid ) {
        
        var serializedData = $("#searchform").serialize();
        
        var request = $.ajax({
            url: "/techrecapi.php?op=getrec",
            type: "post",
            data: serializedData
        });
        
        // callback handler that will be called on success
        request.done(function (response, textStatus, jqXHR){
            // log a message to the console
            console.log("Hooray, it worked!");
            $("#"+outid).innerHTML = response;
        });

        // callback handler that will be called on failure
        request.fail(function (jqXHR, textStatus, errorThrown){
            // log the error to the console
            console.error(
                "The following error occured: "+
                textStatus, errorThrown
            );
            alert("Errore acquisizione info");
        });

        request.always(function () {
            // alert("Chiamato sempre");
        });
    }
    
    $(document).ready(function(){
        $("#trxnewbutton").click( function (){ 
            console.log("start");
            alert("start");
            fetch_rec("resultcontainer");
            alert("start");
        });
        
        $("#searchbutton").click ( function () {
            alert("Click search-- load ajax");
        });
    });
</script>

</head>

<body>

<div id="pagecontainer">
    <form action="" method="POST">
            
        <h1> techr*c :: macchina del tempo </h1>
        
        <h2> <a href="new.html"> Nuova registrazione</a> </h2>

        <div id="newrec">
            <form id="searchform" name="searchform" action="#" method=POST>
                <input type="hidden" name="op" value="new">
      	        <input type="text" id="trxname"   name="trxname"   placeholder="Nome Registrazione" />            
                <input type="text" id="starttime" name="starttime" placeholder="Inizio, es:2013/03/23 13:42:53" />
    	        <input type="text" id="endtime"   name="endtime"   placeholder="Fine, es:2013/03/23 13:45:23" />
                <input type="button" id="trxnewbutton" value="Crea" class="newrecbutton" />
            </form>
        </div>
    
        <div id="formsearchrec">
            <form action="" method="GET">
                <input type="text"   name="trxname" id="trxname" placeholder="Cerca una trasmissione" />  
                <input type="text"   name="trxtime" id="trxtime" placeholder="Data, es:2013/03/23 13:45:23" />  
                <input type="button" name="searchbutton" id="searchbutton" value="Cerca" /> 
            </form>
        </div>

        <div id="oldrec">
            <table>
                <tr>
                    <td> </td>
                    <td> </td>
                </tr>
            </table>
        </div>
    
    </form>
    
    <div id="resultcontainer">
    
    </div>
</div>

<div id="footer">
    techbl*c
</div>

</body>
</html>
