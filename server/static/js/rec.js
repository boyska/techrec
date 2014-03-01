/*global $*/
var config = {
	polling_interval: 500,
	date_write: function(d) {
		return Math.floor(d.getTime() / 1000);
	},
	datetimeformat: function(d) {
		if(Math.abs(new Date() - d) > (3*60*60*1000)) {
			return d.toLocaleString();
		}
		return d.toLocaleTimeString();
	}
};

var RecAPI = {
	create: function() {
		return $.ajax('/api/create', {
			method: 'POST',
			dataType: 'json'
		});
	},
	stop: function(rec) {
		return $.post('/api/update/' + rec.id, {
			starttime: rec.starttime
		});
	},
	update: function(id, data) {
		return $.post('/api/update/' + id, data);
	},
	fullcreate: function(name, start, end) {
		return $.ajax(
			'/api/create', {
			method: 'POST',
			dataType: 'json',
			data: { name: name,
				starttime: config.date_write(start),
				endtime: config.date_write(end)
			}
		});
	},
	generate: function(rec) {
		return $.post('/api/generate', {
			id: rec.id
		});
	},
	get_ongoing: function() {
		return $.getJSON('/api/get/ongoing');
	}
};
