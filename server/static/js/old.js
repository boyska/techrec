/* BEGIN Validation */
function form_check() {
  "use strict";
  var errs = [];
  function err(msg, element) {
    errs.unshift({ msg: msg, el: element});
  }
  if($('#name').val() == '') {
    errs.unshift("Nome mancante", $('#name'));
  }
  if(parseInt($('#to-hour').val(), 10) - parseInt($('#from-hour').val(), 10) > 5) {
    errs.unshift("Too long");
  }
  if(parseInt($('#to-hour').val(), 10) - parseInt($('#from-hour').val(), 10) < 0) {
    //TODO: better date handling
    errs.unshift("Inverted from/to ?");
  }
  return errs;
}

function update_form_check(errors) {
  "use strict";
  /* This function reads results and changes "things" consequently */
  if(errors.length > 0) {
    console.log(errors);
    $('#download').addClass("pure-button-disabled");
  } else { /* everything fine */
    $('#download').removeClass("pure-button-disabled");
  }
}
/* END validation */

$(function() {
  "use strict";
  $( "#from-date" ).datepicker({
    defaultDate: "+0d",
  changeMonth: true,
  numberOfMonths: 1,
  onClose: function( selectedDate ) {
    if($('#to-date').val() == '') {
      $('#to-date').datepicker("setDate", selectedDate);
    }
    $("#to-date").datepicker("option", "minDate", selectedDate);
  }
  });
  $( "#to-date" ).datepicker({
    defaultDate: "+0d",
    changeMonth: true,
    numberOfMonths: 1,
    onClose: function( selectedDate ) {
      $("#from-date").datepicker("option", "maxDate", selectedDate);
    }
  });
  $('#to-date, #from-date').datepicker($.datepicker.regional['it']);

  $('form input').change(function() {
    update_form_check(form_check());
  })
});
