/*global $, config, RecAPI, poll_job*/

//TODO: move to a separate file(?)
$.widget("ror.countclock", {
	options: {
		errormsg: null,
		since: null,
		to: null
	},
	_create: function() {
		this._update();
		//TODO: aggiungi conto secondi/minuti passati
	},
	_setOption: function(key, value) {
		this.options[key] = value;
		this._update();
	},
	_update: function() {
		if(this.options.since !== null) {
			if(this.options.to === null) {
				this.element.text("Registrando da " +
					config.datetimeformat(this.options.since)
					);
			} else {
				this.element.text("Registrando da " +
					config.datetimeformat(this.options.since) +
					" a " + 
					config.datetimeformat(this.options.to)
					);
			}
		} else {
			this.element.text('');
		}
	}
});

$.widget("ror.ongoingrec", {
	options: {
		rec: null,
		state: 0,
		filename: null,
		/*0 = ongoing, 1 = encoding, 2 = ready to download, 9 = errors*/
	},
	_create: function() {
		"use strict";
		//convert a Rec into a <tr>
		var widget = this;
		var rec = this.options.rec;
		var view = this.element.data('rec', rec).addClass('ongoing-rec').append(
			$('<td/>').append(
				$('<input/>').attr('placeholder', 'Nome trasmissione')
		)
		).append( $('<td class="ongoingrec-time"/>').countclock()).append(
		$('<td/>').append($('<a/>')
											.addClass('pure-button pure-button-large'))
		);
		this._update();

		view.on("change", "input", function(evt) {
			console.log('change', evt);
			var prevrec = widget.options.rec;
			prevrec.name = $(evt.target).val();
			$(evt.target).parents('tr.ongoing-rec').data('rec', prevrec);
			widget._trigger("change", evt,
											{rec: rec, widget: widget, changed: {name: rec.name}}
										 );
		});
		view.on("click", ".rec-stop", function(evt) {
			widget._trigger("stop", evt, {rec: rec, widget: widget});
		});
		view.on("click", ".rec-failed", function(evt) {
			$('<div/>').html($('<pre/>').text(widget.options.errormsg))
			.dialog({modal: true, title: "Dettaglio errori",
							buttons: {
								Retry: function() {
									console.log("retrying");
									widget._setOption("state", 0);
									widget._trigger("retry", evt, {rec: rec, widget: widget});
									$(this).dialog("close");
								}, Cancel: function() {
									$(this).dialog("close");
								}
							}
			});
		});

		return view;
	},
	_setOption: function(key, value) {
		this.options[key] = value;
		if(key === 'state') {
			if(value !== 9) {
				this.options.errormsg = null;
			}
			if(value < 2) {
				this.options.filename = null;
			}
		}
		this._update();
	},
	_update: function() {
		var rec = this.options.rec;
		this.element.find('input').val(rec.name);
		this.element.find(':ror-countclock').countclock("option", "since",
									rec.starttime !== null ? config.date_read(rec.starttime) :	null);
		if(this.options.state > 0) {
			this.element.find(':ror-countclock').countclock("option", "to", 
																											rec.endtime !== null ? config.date_read(rec.endtime) : null
																											);
		} else {
			this.element.find(':ror-countclock').countclock("option", "to", null);
		}

		this.element.find('a').removeClass(
			'pure-button-disabled rec-encoding rec-download rec-failed rec-stop');
			switch(this.options.state) {
				case 0:
					this.element.find('a').addClass("rec-stop").html(
						$('<i/>').addClass('fa fa-stop')).append(' Stop');
				break;
				case 1:
					this.element.find('a')
					.addClass("pure-button-disabled rec-encoding").html(
						$('<i/>').addClass('fa fa-clock-o')).append(' Aspetta');
				break;
				case 2:
					this.element.find('a').addClass("rec-download")
					.prop('href', this.options.filename)
					.html(
						$('<i/>').addClass('fa fa-download').css('color', 'green'))
						.append(' Scarica');
				break;
				case 9:
					this.element.find('a').addClass("rec-failed")
					.html(
						$('<i/>').addClass('fa fa-warning')).append(' Errori');
				break;
			}
	}
});

function add_new_rec() {
	//progress()
	return RecAPI.create()
	.done(function(res) {
		/*global show_ongoing*/
		//passa alla seconda schermata
		$('#rec-inizia').remove();
		$('#rec-normal').show();
		show_ongoing([res.rec]);
	})
	.fail(function() {
		/*global alert*/
		alert("C'e' stato qualche problema nella comunicazione col server");
	});
}

function gen_rec(rec, widget) {
	"use strict";
	var gen_xhr = RecAPI.generate(rec);
	gen_xhr.done(function(res_gen) {
		widget.option("state", 1);
		poll_job(res_gen.job_id, function(data) {
			if(data.job_status !== 'DONE') {
				console.error("Job failed!", data);
				widget.option("errormsg", "Generation failed");
				widget.option("state", 9);
			} else {
				widget.option("filename", res_gen.result);
				widget.option("state", 2);
			}
		});
	});
	gen_xhr.fail(function(res_gen) {
		var error = JSON.parse(res_gen.responseText).message;
		widget.option("errormsg", error);
		widget.option("state", 9);
	});
	return gen_xhr;
}

function stop_rec(rec, widget) {
	"use strict";
	var stop_xhr = RecAPI.stop(rec);
	stop_xhr.done(function(res_update) {
		widget.option("rec", res_update.rec);
		return gen_rec(rec, widget);
	});
	stop_xhr.fail(function(res_update) {
		var error = JSON.parse(res_update.responseText).message;
		widget.option("errormsg", error);
		widget.option("state", 9);
	});
	return stop_xhr; //RecAPI.stop
}

function show_ongoing(ongoing_recs) {
	return ongoing_recs.map(function(rec) {
		var viewrec = $('<tr/>').ongoingrec({rec: rec});
		viewrec.on("ongoingrecstop", function(evt, data) {
			stop_rec(data.rec, data.widget);
		}).on("ongoingrecretry", function(evt, data) {
			//FIXME: bisognerebbe solo generare, senza stoppare
			gen_rec(data.rec, data.widget);
		}).on("ongoingrecchange", function(evt, data) {
			//TODO: aggiorna nome sul server
			RecAPI.update(data.rec.id, data.rec);
		});
		$('#ongoing-recs-table tbody').prepend(viewrec);
		return viewrec;
	});
}

$(function() {
	"use strict";
	/*global getKeys*/
	//TODO: get-ongoing
	RecAPI.get_ongoing()
	.done(function(recs) {
		$('.add-new-rec').click(add_new_rec);
		console.log(recs);
		if(getKeys(recs).length !== 0) {
			$('#rec-inizia').remove();
			$('#rec-normal').show();
			show_ongoing(getKeys(recs).map(function(id) { console.log(id); return recs[id]; }));
		}
	});
});

//POLYFILL for Object.keys
function getKeys(obj) {
	var keys = [];
	var key;
	for(key in obj) {
		if(obj.hasOwnProperty(key)) {
			keys.push(key);
		}
	}
	return keys;
}

/* vim: set ts=2 sw=2 noet fdm=indent: */
