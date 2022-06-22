let setup_flag = false;
let gt = [];
let test_id;

function loadTestPage(xml, idx = 1) {
    // * load the content of test page
    test_id = idx;
    let test_xml = $(xml).find(`test-${test_id}`);
    $('.test-title').html(test_xml.find('test-title').text());

    // $(selector).attr(attributeName, value);
    let img_url = test_xml.find('test-img-url').text();
    $('#pic').attr('src', `../${img_url}`);

    $('#pic').load(function () {
        console.log(`Image ${$("#pic").attr("src")} is loaded!`);
        if (!setup_flag) {
            setupAll();
            // bindBatchBtn(xml, img_urls, callback);
            setup_flag = true;

            $("#test-submit").click(() => checkTest(xml));
        }
    })

    gt = JSON.parse(test_xml.find('gt').text());
    // console.log(gt);
}

function checkTest(xml) {
    if (test_id == 1)
        return checkTest1(xml);
    else if (test_id == 2)
        return checkTest2(xml);
    else if (test_id == 3)
        return checkTest3(xml);
    else if (test_id == 4)
        return checkTest4(xml);
}

function checkTest1(xml) {
    // * check the result of Test 1


    var success_flag = true;


    if (annotations.length != 1 || annotations[0]["class"] != "Rotation") {
        success_flag = false;
        val_alert("<b>Incorrect!</b> You should label <b>ONE</b> rotation symmetry.", 'alert-danger',  function(){return reset(false);});
        return;
    }

    var user_label = annotations[0]["data"];

    user_label = [user_label[0] / $(img).width(), user_label[1] / $(img).height()]

    if (!validate_rot(user_label, gt, th_dist = 0.05)) {
        success_flag = false;
        val_alert("<b>Incorrect!</b> You should label the <b>CENTER</b> of a rotation symmetry.", 'alert-danger', function(){return reset(false);});
        return;
    }

    if (success_flag) {
        val_alert("<b>Correct!</b> Close this message to continue. The message will be automatically closed in 3 second.", 'alert-success', function () {
            loadTestPage(xml, 2);
            reset(false);
            dismissAlerts();
        });
        return;
    }
}

function checkTest2(xml) {
    // * check the result of Test 2
    var success_flag = true;


    if (annotations.length != 1 || annotations[0]["class"] != "Reflection") {
        success_flag = false;
        val_alert("<b>Incorrect!</b> You should label <b>ONE</b> reflection symmetry.", 'alert-danger',  function(){return reset(false);});
        return;
    }

    var user_label = annotations[0]["data"];

    user_label = [user_label[0] / $(img).width(), user_label[1] / $(img).height(), user_label[2] / $(img).width(), user_label[3] / $(img).height()]

    if (!validate_rot(user_label, gt, th_dist = 0.5)) {
        success_flag = false;
        val_alert("<b>Incorrect!</b> You should label the <b>TWO END-POINTS</b> of a reflection symmetry axis.", 'alert-danger',  function(){return reset(false);});
        return;
    }

    if (success_flag) {
        val_alert("<b>Correct!</b> Close this message to continue. The message will be automatically closed in 3 second", 'alert-success', function () {
            loadTestPage(xml, 3);
            reset(false);
            dismissAlerts();
        });
        return;
    }
}

function checkTest3(xml) {
    // * check the result of Test 3

    var rot_flag = false;
    var ref_flag = false;

    console.log(annotations);

    annotations.forEach(element => {
        if (element["class"] == "Rotation") { rot_flag = true; }
        else if (element["class"] == "Reflection") { ref_flag = true; }
    });


    if (rot_flag && ref_flag) {

        val_alert("<b>Correct!</b> Close this message to continue. The message will be automatically closed in 3 second", 'alert-success', function () {
            loadTestPage(xml, 4);
            reset();
            dismissAlerts();
        });

        return;
    }
    else {
        val_alert("<b>Incorrect!</b> You should label at least <b>ONE</b> rotation and <b>ONE</b> reflection symmetry", 'alert-danger',  function(){return reset(false);});
        return;
    }
}

function checkTest4(xml) {
    // * check the result of Test 4
    location.href = 'congrats.html';
}

function pt_dist(A, B) {
    // * compute the Euclidean distance of two points
    d = Math.sqrt((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2);

    return d;
}

function pt_line_dist(p1, p2, p) {
    // * compute the Euclidean distance of point P to line defined by (P1, P2)
    var n = (p2[0] - p1[0]) * (p1[1] - p[1]) - (p1[0] - p[0]) * (p2[1] - p1[1]);
    var d = Math.abs(n) / pt_dist(p1, p2);

    return d;
}

function line_angle(l1, l2) {
    // * compute the angle of two lines defined by (p11, p12), (p21, p22)
    var dAx = l1[2] - l1[0];
    var dAy = l1[3] - l1[1];
    var dBx = l2[2] - l2[0];
    var dBy = l2[3] - l2[1];
    var angle = Math.atan2(dAx * dBy - dAy * dBx, dAx * dBx + dAy * dBy);
    if (angle < 0) { angle *= -1; }

    // * angle in Radians
    return angle;
}

function rot_sym_dist(A, B) {
    // * compute rotation symmetry distance: D_o
    return pt_dist(A, B);
}



function ref_sym_dist_a(A, B) {
    // * compute reflection symmetry distance: D_a
    var l1 = pt_dist(A.slice(0, 2), A.slice(2, 4));
    var l2 = pt_dist(B.slice(0, 2), B.slice(2, 4));
    var R = (l1 + l2) / 2.0;

    var d1 = pt_dist(A.slice(0, 2), B.slice(0, 2));
    var d2 = pt_dist(A.slice(2, 4), B.slice(2, 4));
    var d3 = pt_dist(A.slice(0, 2), B.slice(2, 4));
    var d4 = pt_dist(A.slice(2, 4), B.slice(0, 2));

    var d_a = Math.min((d1 + d2) / 2.0, (d3 + d4) / 2.0);
    d_a /= R;

    return d_a;
}

function ref_sym_dist_b(A, B) {
    // * compute reflection symmetry distance: D_b
    var l1 = pt_dist(A.slice(0, 2), A.slice(2, 4));
    var l2 = pt_dist(B.slice(0, 2), B.slice(2, 4));
    var R = (l1 + l2) / 2.0;

    var m1 = [(A[0] + A[2]) / 2.0, (A[1] + A[3]) / 2.0];
    var m2 = [(B[0] + B[2]) / 2.0, (B[1] + B[3]) / 2.0];


    var d_b = pt_dist(m1, m2);
    d_b /= R;

    return d_b;
}

function ref_sym_dist_c(A, B) {
    // * compute reflection symmetry distance: D_c
    var l1 = pt_dist(A.slice(0, 2), A.slice(2, 4));
    var l2 = pt_dist(B.slice(0, 2), B.slice(2, 4));
    var R = (l1 + l2) / 2.0;

    var m1 = [(A[0] + A[2]) / 2.0, (A[1] + A[3]) / 2.0];
    var m2 = [(B[0] + B[2]) / 2.0, (B[1] + B[3]) / 2.0];

    var d1 = pt_line_dist(B.slice(0, 2), B.slice(2, 4), m1);
    var d2 = pt_line_dist(A.slice(0, 2), A.slice(2, 4), m2);

    var d_c = (d1 + d2) / 2.0
    d_c /= R;

    return d_c;
}

function ref_sym_dist_d(A, B) {
    // * compute reflection symmetry distance: D_d

    return line_angle(A, B);
}

function validate_rot(user_label, gt, th_dist = 0.05) {
    // console.log("label:", user_label, "gt:", gt);
    // * validate a labeled rotation with ground truth
    if (rot_sym_dist(user_label, gt) > th_dist) { return false; }
    else { return true; }
}

function validate_ref(user_label, gt, th_dist = 0.05) {
    // * validate a labeled reflection with ground truth
    var d_a = ref_sym_dist_a(user_label, gt);
    var d_b = ref_sym_dist_b(user_label, gt);
    var d_c = ref_sym_dist_c(user_label, gt);
    var d_d = ref_sym_dist_d(user_label, gt);
    if (d_a > th_dist || d_b > th_dist || d_c > th_dist || d_d > th_dist) { return false; }
    else { return true; }
}

function val_success(message, redirect_url) {
    dismissAlerts();

    $("#test-alert-box").append(`
            <div class="alert alert-success alert-dismissible fade show" role="alert" id="correct">
            <strong>Correct!</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            `);
    $('.alert#correct').on('closed.bs.alert', function () {
        location.href = redirect_url;
    })
    $(".alert#correct").slideUp(3000, function () {
        $(this).alert('close');
    });
}

function val_failure(message) {
    dismissAlerts();

    $("#test-alert-box").append(`
            <div class="alert alert-danger alert-dismissible fade show" role="alert" id="incorrect">
            <strong>Incorrect!</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            `);
    $('.alert#incorrect').on('closed.bs.alert', function () {
        reset();
    })
    // $(".alert#incorrect").fadeTo(5000, 1.0).slideUp("fast", function(){
    //     reset();
    // });
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