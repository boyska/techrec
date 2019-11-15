/*global $, poll_job*/

var form = {
	MAX_MINS: 5*60, // 5 hours
	get_values: function() {
		var name = $('#name').val();
		var start = $('#from-date').datepicker('getDate');
		if(start !== null) {
			start.setHours($('#from-hour').val());
			start.setMinutes($('#from-min').val());
		}
		var end = $('#to-date').datepicker('getDate');
		if(end !== null) {
			end.setHours($('#to-hour').val());
			end.setMinutes($('#to-min').val());
		}
		return { name: name, start: start, end: end };
	},
	check: function() {
		"use strict";
		var errs = [];
		function err(msg, element) {
			errs.unshift({ msg: msg, el: element});
		}
		var v = form.get_values();
		if(v.name === '') {
			err("Nome mancante", $('#name'));
		}
		if(v.start === null) {
			err("Start unspecified");
		}
		if(v.end === null) {
			err("End unspecified");
		}
		if(v.end <= v.start) {
			err("Inverted from/to ?");
		}
		if( (v.end - v.start) / (1000*60) > form.MAX_MINS) {
			err("Too long");
		}
		return errs;
	}
};

function click(widget) {
	/*global RecAPI*/
	var v = form.get_values();
	RecAPI.fullcreate(v.name, v.start, v.end)
	.done(function(res_create) {
		console.log("ok, created");
		RecAPI.generate(res_create.rec)
		.done(function(res_gen) {
			console.log("ok, generated", res_create);
			//TODO: start polling
			$('#download').thebutton('option', 'state', 'Wait');
			poll_job(res_gen.job_id, function(data) {
				if(data.job_status !== 'DONE') {
					console.error("Job failed!", data);
					widget.thebutton("option", "state", 'Failed');
					widget.thebutton("option", "errormsg", data.exception);
				} else {
					widget.thebutton("option", "filename", res_gen.result);
					widget.thebutton("option", "state", 'Download');
				}
			});
		})
		.fail(function() {
			console.error("Oh shit, generate failed", res_create.rec);
		});
	})
	.fail(function() {
		console.error("Oh shit, fullcreate failed");
	});
}

$(function() {
	"use strict";
	$( "#from-date" ).datepicker({
		defaultDate: "+0d",
		changeMonth: true,
		numberOfMonths: 1,
		maxDate: new Date(),
		onClose: function( selectedDate ) {
			if($('#to-date').val() === '') {
				$('#to-date').datepicker("setDate", selectedDate);
			}
			$("#to-date").datepicker("option", "minDate", selectedDate);
		}
	});
	$( "#to-date" ).datepicker({
		defaultDate: "+0d",
		changeMonth: true,
		numberOfMonths: 1,
		maxDate: new Date(),
		onClose: function( selectedDate ) {
			$("#from-date").datepicker("option", "maxDate", selectedDate);
		}
	});
	$('#to-date, #from-date').datepicker($.datepicker.regional.it);
	$('#download').thebutton();

	$('#download').click(function() {
			if(!$('#download').hasClass('rec-run')) {
				return;
			}
			var check = form.check();
			if(check.length > 0) {
				console.log("Errors in form", check);
				error_dialog(check.map(function(err) { return err.msg; }).join('\n'));
				return;
			}
			click($('#download'));
	});
});
/* vim: set ts=2 sw=2 noet fdm=indent: */
