let translateX, translateY, correctX, correctY;
let anchorX, anchorY, dragX, dragY, mouseX, mouseY;
let dragged, dragStart, delta, scaleRatio, scaleDiff;
let child, parent, canvas, ctx, img;
let annotations, classSelection;
let transparency_level = 0.25;
let dragOffsetX = 0;
let dragOffsetY = 0;
let scalingOffsetX = 0;
let scalingOffsetY = 0;
let oldScale = 1.0;
let newScale = 1.0;
let firstPoint = true;
let modes = ["bbox", "polygon"];
let mode = "";
let modeNum = 0;
let dotSize = 4;
let scaleTransform = 1;
let translateTransform = [0, 0];
let translateTransform_raw = [0, 0];
let delete_mode = false;
let delete_idx = -1;
let trashcan = new Array();
let colors = {};
let timeDownUp = null;
let rightClick = false;

let lineWidth = 4;

let classes = [];
let instsNum = {};     // number of instance for each class
let currentLink = { class: [], mode: "link", data: [] };
let currentPolygon = { class: [], mode: "polygon", data: [] };
let currentBbox = { class: [], mode: "bbox", data: [] };

let classNum = 0;
let selectedRPIndex = -1;

let distinctColors = ['(230, 25, 75)', '(60, 180, 75)', '(255, 225, 25)', '(0, 130, 200)', '(245, 130, 48)', '(145, 30, 180)', '(70, 240, 240)', '(240, 50, 230)', '(210, 245, 60)', '(250, 190, 212)', '(0, 128, 128)', '(220, 190, 255)', '(170, 110, 40)', '(255, 250, 200)', '(128, 0, 0)', '(170, 255, 195)', '(128, 128, 0)', '(255, 215, 180)', '(0, 0, 128)', '(128, 128, 128)'];       // * 20 distinct colors

let classMaxNum = distinctColors.length;

$(document).ready(function () {
    parent = document.getElementById("parent");
    child = document.getElementById("child");
    canvas = document.getElementById("myCanvas");
    ctx = canvas.getContext("2d");
    img = document.getElementById("pic");

    modeButton = $("#mode_button")

    canvas.width = img.width;
    canvas.height = img.height;
    canvas.style.cursor = "crosshair";

    classSelection = $("select#label_class")[0];

    // * setup the hidden instruction
    $("#instruction").slideUp(0);

    $("#instruction_button").click(function () {
        $("#instruction").clearQueue();
        $("#instruction").slideToggle();
    });

    annotations_str = "${annotations}";
    if (annotations_str == "$" + "{annotations}") {
        annotations = [];
    } else {
        annotations_str = annotations_str.replace(/'/g, '"');
        annotations_str = annotations_str.replace(/;/g, ",");
        annotations = JSON.parse(annotations_str);
    }

    annotations.push = function (obj) {
        Array.prototype.push.call(annotations, obj);
    };

    annotations.splice = function (idx, numElements) {
        Array.prototype.splice.call(annotations, idx, numElements);
    };

    mode = modes[0];

    modeButton.text("Mode: " + capitalize(mode));

    // * generate RP list options
    // addRPClass(0);

    // * initialize buttons
    $("#reset_button").click(reset);
    $("#reposition_button").click(reposition);
    $("#undo_button").click(undo);
    $("#mode_button").click(toggleMode);
    $("#delete_button").click(() => setDeleteMode(true));
    $("#annotate_button").click(() => setDeleteMode(false));

    $("#add_rp_button").click(() => addRPClass(-1));
    $("#remove_rp_button").click(removeRPClass);

    $("#submit").click(function () {
        $("crowd-form")[0].submit();
    });


    // document.getElementById("submitButton").disabled = false;
    // document
    //     .getElementById("buttons")
    //     .appendChild(document.getElementById("submitButton"));

    child.addEventListener("DOMMouseScroll", handleScroll, false);
    child.addEventListener("mousewheel", handleScroll, false);

    // * disable right click context menu on canvas
    canvas.oncontextmenu = function () {
        return false;
    };

    $("img#pic").on('load', function () {
        var canvas = $(this).siblings("canvas")[0];
        // setupCanvas(canvas, this);
    });

    canvas.addEventListener("mouseout", function (evt) {
        dragStart = false;
        dragged = false;
    });

    canvas.addEventListener("pointerdown", function (evt) {
        rightClick = evt == 3;
        getCorrectCoords(evt);
        timeDownUp = new Date().getTime();
        anchorX = evt.clientX;
        anchorY = evt.clientY;
        dragged = false;
        dragStart = true;
        if (selectedRPIndex == -1 ) {return;}
        if (mode == "bbox" && !rightClick && !getDeleteMode()) {
            currentBbox.class = getClass();
            currentBbox.data = new Array();
            currentBbox.data.push([correctX, correctY]);
        }
    });

    canvas.addEventListener("pointerup", function (evt) {
        timeDownUp = new Date().getTime();
        getCorrectCoords(evt);
        if (selectedRPIndex == -1 ) {return;}
        if (dragged) {
            if (mode == "bbox" && !rightClick) {
                currentBbox.data.push([correctX, correctY]);
                if (currentBbox.data.length == 2) {
                    annotations.push(Object.assign({}, currentBbox));
                }
                currentBbox.data = new Array();
            }
        } else {
            if (!rightClick) {
                if (getDeleteMode() == true) {
                    deleteAnnotation();
                } else {
                    updateAnnotation();
                }
            } else {
                currentBbox.data = new Array();
            }
        }

        rightClick = false;
        dragStart = false;
        updateGraphics();


    });

    canvas.addEventListener("mousemove", function (evt) {
        getCorrectCoords(evt);
        if (getDeleteMode() == true) {
            delete_idx = getDeleteIdx();
            updateGraphics();
        } else if (rightClick) {
            let timeMove = new Date().getTime();
            if (timeMove > timeDownUp) {
                if (dragStart) {
                    dragged = true;
                    dragX = evt.clientX - anchorX;
                    dragY = evt.clientY - anchorY;
                    translateTransform_raw = [
                        translateTransform_raw[0] + dragX,
                        translateTransform_raw[1] + dragY,
                    ];
                    translateTransform[0] = translateTransform_raw[0] / newScale;
                    translateTransform[1] = translateTransform_raw[1] / newScale;
                    updateTransform();
                    dragOffsetX += dragX;
                    dragOffsetY += dragY;
                    anchorX = evt.clientX;
                    anchorY = evt.clientY;
                }
            } else {
                timeDownUp = null;
            }
        } else if (mode == "bbox" && dragStart) {
            dragged = true;
            updateGraphics();
        } else if (mode == "link") {
            updateGraphics();
        }
    });
});

// end of ready function

function resizeCanvas() {
    // * resize the canvas to avoid scrolling
    $(img).width('50%');
    canvas.style.width = 
    $(canvas).width = $(img).width;
    $(canvas).height = $(img).height;

    // $(img).width = $(canvas).width;
    // $(img).height = $(canvas).height;
}


function getRPIndex(className) {
    let idx = className.match(/\d+$/)[0] - 1;
    return idx;
}

function selectRP() {
    // * get the RP index
    selectedRPIndex = getRPIndex($(this).attr('name'));
    // * active the current RP button
    $(this).parent().children().removeClass('active');
    $(this).parent().siblings().children().removeClass('active');
    $(this).addClass('active');

    updateGraphics();
}

function addRPClass(idx = -1) {
    if (classNum < classMaxNum) {
        classNum += 1;
        classes.push(`Recurring Pattern ${classNum}`);
        if (idx == -1)
            setRPClass(selectedRPIndex + 1);
        else
            setRPClass(idx);
    }

}

function removeRPClass() {
    // * remove the selected RP
    classNum -= 1;
    classNum = Math.max(1, classNum);

    classes = [];


    for (let i = 0; i < classNum; i++) {
        classes.push(`Recurring Pattern ${i + 1}`);
    }



    // * remove the corresponding annotations
    let new_anno = [];
    annotations.forEach(item => {
        if (item['class'] != `Recurring Pattern ${selectedRPIndex + 1}`) {
            let idx = getRPIndex(item['class']);
            if (idx > selectedRPIndex)
                item['class'] = `Recurring Pattern ${idx}`;
            new_anno.push(deep_copy(item));
        }
    });
    // console.log(new_anno);
    annotations = new_anno;

    selectedRPIndex = Math.max(0, selectedRPIndex);
    selectedRPIndex = Math.min(classNum - 1, selectedRPIndex);
    setRPClass(selectedRPIndex);
}

function setRPClass(selectedIndex = 0) {

    $('.rp_container').html("");
    classes.forEach((theClass, idx) => {
        colors[theClass] = distinctColors[idx];
        $(`#${idx%2}.rp_container`).append(`
        <button type="button" class="btn rp_button" name="${theClass}" id="${theClass}"><span style="color:rgb${colors[theClass]};" class="bi bi-square-fill"> </span> ${theClass}</button>
        `);
    });

    let rp_button = $('.rp_button');
    rp_button.click(selectRP);
    //  rp_button[selectedIndex].classList.add('active');
    selectedRPIndex = selectedIndex;
    activeRP();
    updateGraphics();
}

function setRPInstNum() {
    // * add the rp_inst number to each RP button for convenience
    let rp_button = $('.rp_button');
    rp_button.each(function(){
        let theClass = $(this).attr('name');
        let instNum = 0;
        if (theClass in instsNum) {instNum = instsNum[theClass];}
        $(this).html(`<span style="color:rgb${colors[theClass]};" class="bi bi-square-fill"> </span> ${theClass} (${instNum})`);
    });

}

function activeRP() {
    let parent_idx = selectedRPIndex%2;
    let child_idx = Math.floor(selectedRPIndex / 2);
    $(`#${parent_idx}.rp_container .rp_button`)[child_idx].classList.add('active');
}


function highlightRP() {
    // * highlight the annotations belonging to the current RP

    // * get the RP index
    let rpIdx = getRPIndex($(this).text());


}

function drawPolygonOutline(corners) {
    for (let j = 0; j < corners.length; j++) {
        ctx.fillRect(
            corners[j][0] - dotSize / 2,
            corners[j][1] - dotSize / 2,
            dotSize,
            dotSize
        );
    }
    ctx.beginPath();
    ctx.moveTo(corners[0][0], corners[0][1]);
    for (let j = 1; j < corners.length; j++) {
        ctx.lineTo(corners[j][0], corners[j][1]);
        ctx.stroke();
    }
    ctx.stroke();
    ctx.closePath();
}

function fillPolygon(corners) {
    ctx.beginPath();
    ctx.moveTo(corners[0][0], corners[0][1]);
    for (let j = 1; j < corners.length; j++) {
        ctx.lineTo(corners[j][0], corners[j][1]);
        ctx.stroke();
    }
    ctx.lineTo(corners[0][0], corners[0][1]);
    ctx.stroke();
    ctx.closePath();
    ctx.fill();
}

function toggleMode() {
    modeNum += 1;
    if (modeNum >= modes.length) {
        modeNum = 0;
    }
    setDeleteMode(false);
    mode = modes[modeNum];
    modeButton.text("Mode: " + capitalize(mode));
    clearCurrentAnn();
}

function clearCurrentAnn() {
    currentBbox.data = new Array();
    currentLink.data = new Array();
    currentPolygon.data = new Array();
}

function deleteAnnotation() {
    if (delete_idx > -1) {
        let ann_copy = deep_copy(annotations[delete_idx]);
        trashcan.push(ann_copy);
        annotations.splice(delete_idx, 1);
        delete_idx = getDeleteIdx();
        if (annotations.length == 0)
            // no more to delete, go back to annotate mode
            setDeleteMode(false);
    }
}

function toggleDelete() {
    setDeleteMode(!getDeleteMode());
}

function getDeleteMode() {
    return delete_mode;
}

function setDeleteMode(deleteMode) {
    delete_mode = deleteMode;
    if (delete_mode == false) {
        // annotate mode
        canvas.style.cursor = "crosshair";
        $("#delete_button").removeClass("btn-primary");
        $("#delete_button").addClass("btn-outline-secondary");

        $("#annotate_button").removeClass("btn-outline-secondary");
        $("#annotate_button").addClass("btn-primary");
        updateGraphics();
    } else {
        // delete mode
        delete_idx = getDeleteIdx();
        canvas.style.cursor = "pointer";
        $("#annotate_button").removeClass("btn-primary");
        $("#annotate_button").addClass("btn-outline-secondary");

        $("#delete_button").removeClass("btn-outline-secondary");
        $("#delete_button").addClass("btn-primary");
        updateGraphics();
    }
}

function reset() {
    clearAnnotations();
    reposition();
    firstPoint = true;
    dragStart = false;
    dragged = false;
    setDeleteMode(false);

    classes = [];
    classNum = 0;
    selectedRPIndex = 0;
    addRPClass(0);
}

function reposition() {
    child.style.transform = "";
    scaleTransform = 1.0;
    translateTransform = [0, 0];
    translateTransform_raw = [0, 0];
    newScale = 1.0;
    oldScale = 1.0;
    scaleRatio = 1.0;
    scaleDiff = 0;
    dragOffsetX = 0;
    dragOffsetY = 0;
    scalingOffsetX = 0;
    scalingOffsetY = 0;
}

function updateAnnotation() {
    if (selectedRPIndex == -1 ) {return;}
    switch (mode) {
        case "dot": // dot mode
            annotations.push({
                class: getClass(),
                mode: "dot",
                data: [correctX, correctY],
            });
            break;
        case "link": // link mode
            currentLink.class = getClass();
            currentLink.data.push([correctX, correctY]);
            if (firstPoint) {
                firstPoint = false;
            } else {
                annotations.push(Object.assign({}, currentLink));
                currentLink.data = new Array();
                firstPoint = true;
            }
            break;
        case "polygon": // polygon mode
            currentPolygon.class = getClass();
            currentPolygon.data.push([correctX, correctY]);
    }
}

function clearAnnotations() {
    annotations = new Array();
    trashcan = new Array();
    currentLink = { class: [], mode: "link", data: [] };
    currentPolygon = { class: [], mode: "polygon", data: [] };
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function getClass() {
    
    return classes[selectedRPIndex];
    // return $('#rp_container .rp_button')[selectedRPIndex].innerHTML;
}

function checkClass() {
    if (selectedRPIndex == -1 ) {
        // * a warning of no RP class
        let message = `Please click the "Add an RP" button first!`;
        // $("div#body-part").prepend(`
        //     <div class="alert alert-danger alert-dismissible" id="incorrect">
        //     <strong>Warning!</strong> ${message}
        //         <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        //             <span aria-hidden="true">&times;</span>
        //         </button>
        //     </div>
        //     `);
        return false;
    }
    return true;
}

function getColor(annotation, options) {
    if (
        getDeleteMode() === true &&
        "idx" in options &&
        delete_idx === options.idx
    ) {
        return [0.5, 0.5, 0.5];
    } else {
        return rgbColor(colors[annotation.class]);
    }
}

function rgbColor(rgbString) {
    // * convert rgb color to [r, g, b]
    return rgbString.match(/\d+/g);
}


function drawPolygon(annotation, options) {

    const corners = annotation.data;

    const [r, g, b] = getColor(annotation, options);


    if (options.rpIdx == selectedRPIndex) {
        // * set highlight border
        ctx.fillStyle = "rgba(1, 1, 1, 0)";
        ctx.strokeStyle = `rgba(255, 255, 255, 1.0)`;
        ctx.lineWidth = lineWidth + 2;
        fillPolygon(corners);
    }

    ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${transparency_level})`;
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, 1.0)`;

    if (options.current) {
        drawPolygonOutline(corners);
    } else {
        fillPolygon(corners);
    }


}

function drawBbox(annotation, options) {

    const xmin = annotation.data[0][0];
    const ymin = annotation.data[0][1];
    let xmax, ymax;
    if (options.current) {
        xmax = correctX;
        ymax = correctY;
    } else {
        xmax = annotation.data[1][0];
        ymax = annotation.data[1][1];
    }
    const corners = [
        [xmin, ymin],
        [xmax, ymin],
        [xmax, ymax],
        [xmin, ymax],
    ];


    const [r, g, b] = getColor(annotation, options);
    if (options.rpIdx == selectedRPIndex) {
        // * set highlight border
        ctx.fillStyle = "rgba(1, 1, 1, 0)";
        ctx.strokeStyle = `rgba(255, 255, 255, 1.0)`;
        ctx.lineWidth = lineWidth + 2;
        fillPolygon(corners);
    }

    ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${transparency_level})`;
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, 1.0)`;
    fillPolygon(corners);
}

function updateGraphics() {
    if (selectedRPIndex == -1 ) {return;}
    ctx.clearRect(0, 0, canvas.width, canvas.height);


    instsNum = [];
    annotations.forEach((ann, idx) => {
        let rpIdx = getRPIndex(ann.class);
        if (ann.class in instsNum) {
            instsNum[ann.class] += 1;
        }
        else {
            instsNum[ann.class] = 1;
        }
        switch (ann.mode) {
            case "polygon":
                drawPolygon(ann, { current: false, idx, rpIdx });
                break;
            case "bbox":
                drawBbox(ann, { current: false, idx, rpIdx });
        }
    });

    if (currentPolygon.data.length != 0) {
        drawPolygon(currentPolygon, { current: true });
    }

    if (currentBbox.data.length != 0) {
        drawBbox(currentBbox, { current: true });
    }

    
    if (annotations.length == 0) {
        document.getElementById("coordinates").value = "";
    } else {
        document.getElementById("coordinates").value =
            JSON.stringify(annotations);
    }

    document.getElementById("imageSize").value = `[${$(img).width()}, ${$(img).height()}]`;

    setRPInstNum();
}

// depending on mode, either undo deletion or undo annotation
function undo() {
    if (getDeleteMode() == true) {
        if (trashcan.length > 0) {
            annotations.push(trashcan.pop());
        }
    } else {
        switch (mode) {

            case "polygon":
                if (currentPolygon.data.length == 0) {
                    annotations.pop();
                } else {
                    currentPolygon.data.pop();
                }
                break;
            case "bbox":
                if (currentBbox.data.length == 0) {
                    annotations.pop();
                } else {
                    currentBbox.data = new Array();
                    dragStart = false;
                    dragged = false;
                }
        }
    }
    updateGraphics();
}

window.addEventListener(
    "keydown",
    function (evt) {
        // Press E for "Mode toggle"
        if (evt.key == "e") {
            toggleMode();
        }

        // Press ctrl + Z for "Undo"
        if (evt.key == "z" && evt.ctrlKey) {
            undo();
        }

        // Press D for "Delete"
        if (evt.key == "d") {
            toggleDelete();
        }

        // Press C for "Close Polygon"
        if (evt.key == "c") {
            if (currentPolygon.data.length > 2) {
                currentPolygon.class = getClass();
                annotations.push(Object.assign({}, currentPolygon));
                currentPolygon.data = new Array();
            }
            // Update coordinates
            if (annotations.length == 0) {
                document.getElementById("coordinates").value = "";
            } else {
                document.getElementById("coordinates").value =
                    JSON.stringify(annotations);
            }
        }
        updateGraphics();
    },
    true
);

let handleScroll = function (evt) {
    

    getCorrectCoords(evt);
    delta = evt.wheelDelta ? evt.wheelDelta / 40 : evt.detail ? -evt.detail : 0;

    newScale += delta / 10;
    newScale = Math.max(newScale, 1.0);
    newScale = Math.min(newScale, 5.0);
    scaleRatio = newScale / oldScale;
    scaleDiff = newScale - oldScale;
    oldScale = scaleTransform = newScale;

    scalingOffsetX = ((newScale - 1) * parent.offsetWidth) / 2;
    scalingOffsetY = ((newScale - 1) * parent.offsetHeight) / 2;

    translateTransform_raw[0] -=
        (correctX - parent.offsetWidth / 2) * scaleDiff;
    translateTransform_raw[1] -=
        (correctY - parent.offsetHeight / 2) * scaleDiff;

    translateTransform[0] = translateTransform_raw[0] / newScale;
    translateTransform[1] = translateTransform_raw[1] / newScale;
    updateTransform();

    // * disable page scroll
    TopScroll = window.pageYOffset || document.documentElement.scrollTop;
    LeftScroll = window.pageXOffset || document.documentElement.scrollLeft;
    window.onscroll = function () {
        window.scrollTo(LeftScroll, TopScroll);
    };
};

function updateTransform() {
    child.style.transform = "";
    child.style.transform +=
        "scale(" + scaleTransform + ", " + scaleTransform + ")";
    child.style.transform +=
        "translate(" +
        translateTransform[0] +
        "px, " +
        translateTransform[1] +
        "px)";
}

function getCorrectCoords(evt) {
    // console.log(parent.offsetParent.offsetParent);
    // mouseX = evt.pageX - parent.offsetLeft;
    // mouseY = evt.pageY - parent.offsetTop;

    mouseX =
        evt.clientX - parent.offsetLeft + parent.scrollLeft + window.pageXOffset;
    mouseY =
        evt.clientY - parent.offsetTop + parent.scrollTop + window.pageYOffset;
    correctX = (mouseX + scalingOffsetX - translateTransform_raw[0]) / newScale;
    correctY = (mouseY + scalingOffsetY - translateTransform_raw[1]) / newScale;
    correctX = Math.round(correctX);
    correctY = Math.round(correctY);
}

function getDeleteIdx() {
    let deleteIdx = -1;
    let min_dist = 1000000;
    let dist_array = new Array();
    for (let i = 0; i < annotations.length; i++) {
        let ann = annotations[i];
        let corners = ann.data;
        switch (ann.mode) {
            case "dot":
                dist_array.push(getDist([correctX, correctY], corners));
                break;
            case "link":
                dist_array.push(get_avg_dist(corners));
                break;
            case "polygon":
                dist_array.push(get_avg_dist(corners));
                break;
            case "bbox":
                dist_array.push(get_avg_dist(corners));
        }
    }
    let dist;
    for (let i = 0; i < dist_array.length; i++) {
        dist = dist_array[i];
        if (dist < min_dist) {
            min_dist = dist;
            deleteIdx = i;
        }
    }
    return deleteIdx;
}

function getDist(pair_a, pair_b) {
    let distance = Math.sqrt(
        Math.pow(pair_a[0] - pair_b[0], 2) + Math.pow(pair_a[1] - pair_b[1], 2)
    );
    return distance;
}

function deep_copy(obj) {
    return jQuery.extend(true, {}, obj);
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function mean(array) {
    let total = 0;
    for (let j = 0; j < array.length; j++) {
        total += array[j];
    }
    let avg = total / array.length;
    return avg;
}

function get_avg_dist(corners) {
    let avg_dist_array = new Array();
    for (let j = 0; j < corners.length; j++) {
        avg_dist_array.push(getDist([correctX, correctY], corners[j]));
    }
    return mean(avg_dist_array);
}
