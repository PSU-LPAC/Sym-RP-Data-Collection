let setup_flag = false;
let gt = [];
let test_id;


function loadTestPage(xml, idx = 1) {
    // * load the content of test page
    let root_url = $(xml).find("rp-root-url").text();

    test_id = idx;

    let test_xml = $(xml).find(`test-${test_id}`);
    $('.test-title').html(test_xml.find('test-title').text());

    // $(selector).attr(attributeName, value);
    let img_url = test_xml.find('test-img-url').text();
    $('#pic').attr('src', `../${img_url}`);

    $('#pic').load(function () {
        console.log(`Image ${$("#pic").attr("src")} is loaded!`);
        if (!setup_flag) {
            setupAll(xml);
            // bindBatchBtn(xml, img_urls, callback);
            setup_flag = true;

            $("#test-submit").click(() => check_test(xml));
        }
    })

    gt = JSON.parse(test_xml.find('gt').text());
    // console.log(gt);
}

function check_test(xml){
    if (test_id == 1)
        return check_test1(xml);
    else if (test_id == 2)
        return check_test2(xml);
    else if (test_id == 3)
        return check_test3(xml);
    else if (test_id == 4)
        return check_test4(xml);
}


function check_test1(xml) {
    // * check the result of Test 1


    var success_flag = true;

    console.log(annotations);
    let rps = get_rps(annotations);
    if (Object.keys(rps).length != 1) {
        success_flag = false;
        val_alert("<b>Incorrect!</b> You should label <b>ONE</b> Recurring Pattern.", 'alert-danger',  function(){return reset(false);});
        return;
    }

    var user_label = annotations[0]["data"];
    console.log(user_label);

    if (!(rps[Object.keys(rps)[0]].length == 4)) {
        success_flag = false;
        val_alert("<b>Incorrect!</b> You should label the <b>FOUR</b> RP Instances of this Recurring Pattern.", 'alert-danger', function(){return reset(false);});
        return;
    }

    if (success_flag) {
        val_alert("<b>Correct!</b> Close this message to continue. The message will be automatically closed in 3 second.", 'alert-success', function () {
            // loadTestPage(xml, 2);
            // reset(false);
            // dismissAlerts();

            location.href = 'congrats.html';
        });
        return;
    }
}

function get_rps(annos){
    rps = {}
    annos.forEach(element => {
        let rp_class = element['class'];
        if (!(rp_class in rps)) rps[rp_class] = []
        rps[rp_class].push(element)
    });

    return rps
}



function val_alert(message, alert_class = null, close_callback = null) {
    dismissAlerts();
    let alert = $(`
    <div class="alert alert-dismissible fade show val_alert"  role="alert">
    </div>
    `);
    if (alert_class != null)
        alert.addClass(alert_class);

    alert.html(`
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `)

    if (close_callback != null)
    {
        setTimeout(()=>{
            alert.alert('close');
        }, 3000);
        alert.on('closed.bs.alert', close_callback);
    }
        

    $("#test-alert-box").append(alert);
}

function rp_IOD_metric(rp, gt){
    // Meature the IOD metric of a given RP and GT
    
}