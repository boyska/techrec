/*global $*/

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
		if(v.val === '') {
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

	$('#form').ajaxForm({
		beforeSubmit: function() {
			console.log("check", form.check());
			if(form.check().length > 0) {
				console.log("Form not valid, aborting");
				return false;
			}
			return true;
		},
		success: function() {
			/*global RecAPI*/
			var v = form.get_values();
			RecAPI.fullcreate(v.name, v.start, v.end)
			.done(function(res) {
				console.log("ok, created");
				RecAPI.generate(res.rec)
				.done(function(res) {
					console.log("ok, generated", res);
				})
				.fail(function() {
					console.error("Oh shit, generate failed", res.rec);
				});
			})
			.fail(function() {
				console.error("Oh shit, fullcreate failed");
			});

			return false;
		}
	});
});
/* vim: set ts=2 sw=2 noet fdm=indent: */
