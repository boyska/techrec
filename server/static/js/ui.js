/*global $*/
$.widget("ror.thebutton", {
	options: {
		state: 'Create',
		filename: null,
		errormsg: null
	},
	_create: function() {
		"use strict";
		//create an appropriate button
		var widget = this;
		var state = this.options.rec;
		widget.element.addClass('pure-button');

		widget.element.on("click", function(evt) {
			/*global error_dialog*/
			if(widget.element.hasClass("rec-failed")) {
				error_dialog(widget.options.errormsg,
										 function() {
											 console.log("Should retry, TODO");
											 $(this).dialog("close");
											 widget._setOption('state', 'Create');
											 widget.element.click();
										 },
										 function() {
											 $(this).dialog("close");
										 });
			}
		});

		this._update();
	},
	_setOption: function(key, value) {
		this.options[key] = value;
		if(key === 'state') {
			if(this.options.state !== 'Download') {
				this.options.filename = null;
			}
		}
		this._update();
	},
	_update: function() {
		this.element.removeClass('pure-button-disabled rec-run rec-create ' +
														 'rec-encoding rec-download rec-failed rec-stop');
		switch(this.options.state) {
			case 'Stop':
				this.element.addClass("rec-stop rec-run").html(
					$('<i/>').addClass('fa fa-stop')).append(' Stop');
			break;
			case 'Create':
				this.element.addClass('rec-create rec-run').html(
					$('<i/>').addClass('fa fa-gear')).append(' Create');
			break;
			case 'Failed':
				this.element.addClass("rec-failed").html(
					$('<i/>').addClass('fa fa-warning')).append(' Errori');
			break;
			case 'Wait':
				this.element.addClass("pure-button-disabled rec-encoding") .html(
					$('<i/>').addClass('fa fa-clock-o')).append(' Wait');
			break;
			case 'Download':
				this.element
			.addClass("rec-download")
			.prop('href', this.options.filename)
			.html(
				$('<i/>').addClass('fa fa-download').css('color', 'green'))
				.append(' Scarica');
				break;
		}
	}
});

function error_dialog(msg, retry, cancel) {
	$('<div/>').html($('<pre/>').text(msg))
	.dialog({modal: true, title: "Dettaglio errori",
					buttons: {
						Retry: retry,
						Cancel: cancel
					}
	});
}
/* vim: set ts=2 sw=2 noet fdm=indent: */
