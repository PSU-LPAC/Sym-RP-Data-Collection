function setExpand(){
    $("div.expandable-content").slideUp(0);

    $("button.expandable").click(function () {
        // if ($(this).hasClass("hidden")){
        //     $(this).removeClass("hidden");
        //     $(this).text(`Click here to Hide`);
        // }
        // else {

        // }

        
        let content = $(this).siblings(".expandable-content");
        content.clearQueue();
        content.slideToggle();

        // console.log(content);
    });
}