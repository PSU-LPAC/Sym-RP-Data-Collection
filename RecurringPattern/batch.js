//* Batch Hits related functions
let skip_confirm_str = "Do you want to SKIP this image?";

let submit_confirm_str = "There are NO labelings on the current image. Do you want to SKIP this image?"

let turker_script_flag = false;
let setup_flag = false;


function loadStart(xml, img_urls, callback = null) {
    // * load the start page
    let root_url = $(xml).find("rp-root-url").text();
    let tutorial_url = $(xml).find("tutorial-url").text();

    // Load the content
    $("div#root-container").load(`${root_url}/start.html div#container`, function () {
        console.log("Load start page was performed.");

        reloadMain(xml);
        reloadReward(xml, num_imgs, basic_reward, per_reward, valid_num);
        reloadTime(min_time, max_time);

        
        // bind the buttons
        $("#tutorial-btn").click(() => {
            window.open(tutorial_url);
        })

        $("#task-btn").click(() => {
            loadTask(xml, img_urls, callback);
        })

        if (callback != null) { callback(); }
    })
}

function loadEnd(xml, callback = null) {
    let root_url = $(xml).find("rp-root-url").text();


    // * remove turker script if existed
    let turker_script = $('script#turker');
    turker_script.remove();

    // * unbind the keyboard listener
    // $(document).unbind("keydown", keyboardListener);
    // * load the end page

    // Load the content
    $("div#root-container").load(`${root_url}/end.html div#container`, function () {
        console.log("Load end page was performed.");
        // console.log(all_annos)

        reloadText(xml);
        reloadReward(xml, num_imgs, basic_reward, per_reward, valid_num);
        // * setup submit click
        $(".btn#all-submit").click(function () {
            var suggestion = $('textarea#suggestions').val();

            $("input#annos").val(JSON.stringify(all_annos));
            // $("input#suggestion").val(suggestion);

            $("crowd-form")[0].submit();
        });
        if (callback != null) { callback(); }
    })
}


function loadTask(xml, img_urls, callback = null) {
    // * load the task page
    let root_url = $(xml).find("rp-root-url").text();

    // Load the content
    $("div#root-container").load(`${root_url}/label.html div#container`, function () {
        console.log("Load page was performed.");
        $('#submit').attr('id', 'next');
        // * reload necessary stuff
        reloadText(xml);
        reloadAlert(xml);
        reloadButtons(xml);


        // * set the img
        $("#pic").attr("src", img_urls[img_idx]);

        $('#pic').load(function () {
            console.log(`Image ${$("#pic").attr("src")} is loaded!`);
            if (!setup_flag) {
                setupAll(xml);
                bindBatchBtn(xml, img_urls, callback);
                setup_flag = true;
            }
        })


    })
}

function bindBatchBtn(xml, img_urls, callback = null) {
    // * bind the batch buttons: skip, submit
    $("#skip").click(function () {
        if (checkSkip(img_idx)) {

            all_annos.push(getAnno());
            if (loadNext(xml, img_urls, callback) == -1) {
                loadEnd(xml);
            }
        }
    });

    $("#next").click(function () {
        if (checkSubmit(img_idx)) {
            all_annos.push(getAnno());
            if (loadNext(xml, img_urls, callback) == -1) {
                loadEnd(xml);
            }

        }
    });
}


function loadNext(xml, img_urls, callback = null) {
    // * load the next image
    img_idx += 1;
    if (img_idx >= img_urls.length) { return -1; }
    switchAlert();
    reset();
    disableCanvas();
    startTime = new Date();

    // * set the img
    $("#pic").attr("src", img_urls[img_idx]);
    $('#pic').load(function () {
        console.log("Load Next!");
        resizeCanvas();
        dismissAlerts();
    });

    return 0;
}




function checkSkip() {
    // * check the annotation, and return true to skip the current image

    if (confirm(skip_confirm_str)) {
        skip_num += 1;
        return true;
    }
    else
        return false;
}

function checkSubmit() {
    // * check the annotation, and return true to submit the current image

    single_anno = getAnno();
    // console.log(single_anno);

    if (single_anno['coordinates'].length == 0) {
        if (confirm(submit_confirm_str)) {
            skip_num += 1;
            return true;
        }
    }
    else { 
        valid_num += 1;
        return true; 
    }

    return false;
}

function switchAlert() {
    $('#alert-box').append(`
    <crowd-alert type="info" class="alert switch-alert" dismissible>
        Loading the next image ... 
    </crowd-alert>
    `);
}
