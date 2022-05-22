// training JS scripts

$(document).ready(function () {
    $(".btn#next-train").click(function () {
        var my_url = window.location.href;
        var page_name = my_url.split('/').at(-1);
        if (page_name == 'train1.html')
            window.location = "train2.html";
    });
});