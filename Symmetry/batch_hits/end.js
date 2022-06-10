var params;
var num_labeled = 0;
var money_per_img = 0.2;

$(document).ready(function () {
    // * parse the url parameters
    params = new Array();
    if (params.length == 0) {
        if (window.location.search.split('?').length > 1) {
            var params = window.location.search.split('?')[1].split('&');
            for (var i = 0; i < params.length; i++) {
                var key = params[i].split('=')[0];
                var value = decodeURIComponent(params[i].split('=')[1]);
                params[key] = value;
            }
        }
    }
    console.log(params);

    // * update the message
    if ("num_labeled" in params)
        num_labeled = params["num_labeled"];
    
    $("#congrats").text(`Thank you for your interest in the study. You have labeled ${num_labeled} images making $${num_labeled*money_per_img}.`)

    // * setup submit click
    $(".btn#submit").click(function () {
        var text = $('textarea#suggestions').val();
        console.log(text);
    });
});