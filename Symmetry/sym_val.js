
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
    console.log("label:", user_label, "gt:", gt);
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
    $("div#body-part").prepend(`
            <div class="alert alert-success fade in alert-dismissible" id="correct">
            <strong>Correct!</strong> ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            `);
    $('div#correct').on('closed.bs.alert', function () {
        // console.log("Click close!");
        clearAll($(".labeling-tool")[0]);
        annos[0] = { "Rotation": [], "Reflection": [] };
        sym_types[0] = ('None');
        prev_XY[0] = ([-1, -1]);

        location.href = redirect_url;
    })

    $("div#correct").fadeTo(5000, 1.0).slideUp("fast", function(){
        // $("div#incorrect").slideUp(500);
        clearAll($(".labeling-tool")[0]);
        annos[0] = { "Rotation": [], "Reflection": [] };
        sym_types[0] = ('None');
        prev_XY[0] = ([-1, -1]);

        location.href = redirect_url;
    });
}

function val_failure(message) {
    $("div#body-part").prepend(`
            <div class="alert alert-danger alert-dismissible" id="incorrect">
            <strong>Incorrect!</strong> ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            `);
    $('div#incorrect').on('closed.bs.alert', function () {
        // console.log("Click close!");
        clearAll($(".labeling-tool")[0]);
        annos[0] = { "Rotation": [], "Reflection": [] };
        sym_types[0] = ('None');
        prev_XY[0] = ([-1, -1]);

        $(".list-group > .list-group-item").each(function(index, element){
            reset_sym_option(element);
        });
    })
    $("div#incorrect").fadeTo(5000, 1.0).slideUp("fast", function(){
        // $("div#incorrect").slideUp(500);
        clearAll($(".labeling-tool")[0]);
        annos[0] = { "Rotation": [], "Reflection": [] };
        sym_types[0] = ('None');
        prev_XY[0] = ([-1, -1]);

        $(".list-group > .list-group-item").each(function(index, element){
            reset_sym_option(element);
        });
    });
}
