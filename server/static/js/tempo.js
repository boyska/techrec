/*
TODO:
prendere lo stato !!!
*/
$(document).ready(function(){

	$("#searchform").submit(
		function (event) {
			event.preventDefault();
			dataString = $(this).serialize();
			var request = $.getJSON('/api/search', dataString);

			$("#searchresult").html(" ");
			request.done( function(data) {

				$.each(data, function(key, val) {
					console.log("Extract " + key );

					var divstring = "<div class=\"searchresult\" id=\""+ rs_trxarea(key) +"\"> </div>";

					$("#searchresult").append( divstring );
					// var str = newformstr( key ); // new form

					var str = "";
					str += "<div class=\"namevalues\">"+val.name+" - <a href=\"\">Scarica</a> <a href=\"\" id=\"delete-"+val.id+"\">Cancella</a></div>";
					str += "<div class=\"namevalues\">RECID: "+val.recid+" ID: "+ val.id + " Active " + val.active + "</div>";
					str += "<div class=\"timevalues\">["+val.starttime+"  >>> "+val.endtime+"]</div>"

					$("#"+rs_trxarea(key)).html(str);
				$("#delete-"+val.id).click(function(evt) {
					evt.preventDefault();
					recDelete(val.recid, rs_trxarea(key) );

				}
				); // End of delete link handler

				});
			});
		});
$("#searchform").submit();
});

// vim: set ts=4 sw=4 noet:
