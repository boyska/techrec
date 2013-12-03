/*global $*/
//TODO: move to a separate file(?)
var config = {
	polling_interval: 500,
	datetimeformat: function(d) {
		if(Math.abs(new Date() - d) > (3*60*60*1000)) {
			return d.toLocaleString();
		}
		return d.toLocaleTimeString();
	}
};

$.widget("ror.countclock", {
	options: {
		since: null,
	},
	_create: function() {
		console.log("create");
		this._update();
		//TODO: aggiungi conto secondi/minuti passati
	},
	_setOption: function(key, value) {
		this.options[key] = value;
		this._update();
	},
	_update: function() {
		if(this.options.since !== null) {
			this.element.text("Registrando da " +
				config.datetimeformat(this.options.since)
				);
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
	/*0 = ongoing, 1 = encoding, 2 = ready to download*/
	},
	_create: function() {
		"use strict";
		//convert a Rec into a <tr>
		console.log(this.element);
		var widget = this;
		var rec = this.options.rec;
		console.log("rec", rec);
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

		return view;
	},
	_setOption: function(key, value) {
		this.options[key] = value;
		if(key === 'state') {
			if(value < 2) {
				this.options.filename = null;
			}
		}
		this._update();
	},
	_update: function() {
		var rec = this.options.rec;
		this.element.find('input').val(rec.name);
		this.element.find('.ongoingrec-time').countclock("option", "since",
				rec.starttime !== null ? new Date(rec.starttime*1000) : null
				);
			
		switch(this.options.state) {
			case 0:
				this.element.find('a').removeClass('pure-button-disabled rec-encoding rec-download')
					.addClass("rec-stop").html(
							$('<i/>').addClass('fa fa-stop')).append(' Stop');
				break;
			case 1:
				this.element.find('a').removeClass('rec-stop rec-download')
					.addClass("pure-button-disabled rec-encoding").html(
							$('<i/>').addClass('fa fa-clock-o')).append(' Aspetta');
				break;
			case 2:
				this.element.find('a').removeClass('pure-button-disabled rec-stop rec-encoding')
					.addClass("rec-download")
					.prop('href', this.options.filename)
					.html(
							$('<i/>').addClass('fa fa-download').css('color',
								'green')).append(' Scarica');
				break;
		}
	}
});

function poll_job(job_id, callback) {
	$.getJSON('/api/jobs/' + job_id)
		.done(function(data) {
			if(data.job_status !== 'WIP') {
				console.log("polling completed for job[" + job_id + "]", data);
				callback(data);
			} else {
				setTimeout(function() { poll_job(job_id, callback); },
					config.polling_interval);
			}
		});
}

function add_new_rec() {
	//progress()
	return $.ajax('/api/create', {
		method: 'POST',
		dataType: 'json'
	})
	.done(function(res) {
		//passa alla seconda schermata
		$('#rec-inizia').remove();
		$('#rec-normal').show();
		show_ongoing([res.rec]);
	})
	.fail(function() {
		alert("C'e' stato qualche problema nella comunicazione col server");
	});
}

function stop_rec(rec, widget) {
	"use strict";
	var data = {
		recid: rec.recid,
		starttime: rec.starttime
	};
	var xhr = $.ajax('/api/update', {
		method: 'POST',
		dataType: 'json',
		data: data
	});
	xhr.done(function(res_update) {
		if(res_update.status !== true) {
			console.error(res_update.status);
			return;
		}
		$.ajax('/api/generate', {
			method: 'POST',
			data: { 'recid': rec.recid }
		}).done(function(res_gen) {
			//TODO: start polling on res.job_id
			widget.option("state", 1);
			poll_job(res_gen.job_id, function(data) {
				if(data.job_status !== 'DONE') {
					console.error("Job failed!", data);
				} else {
					widget.option("filename", res_gen.result);
					widget.option("state", 2);
				}
			});
		});
		return xhr;
	});
}

function show_ongoing(ongoing_recs) {
	return ongoing_recs.map(function(rec) {
		var viewrec = $('<tr/>').ongoingrec({rec: rec});
		viewrec.on("ongoingrecstop", function(evt, data) {
			stop_rec(data.rec, data.widget);
		}).on("ongoingrecchange", function(evt, data) {
			//TODO: aggiorna nome sul server
			$.ajax('/api/update', {
				method: 'POST',
				data: data.rec,
			});
		});
		$('#ongoing-recs-table tbody').prepend(viewrec);
		return viewrec;
	});
}

$(function() {
	"use strict";
	//TODO: get-ongoing
	$('.add-new-rec').click(add_new_rec);
});

/* vim: set ts=2 sw=2 noet fdm=indent: */
