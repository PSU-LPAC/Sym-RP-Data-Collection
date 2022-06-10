// Reload the html content from XML

function reloadMain(xml) {
    reloadText(xml);

    reloadSymDef(xml);

    reloadFigs(xml);

    reloadButtons(xml);
}

function reloadText(xml) {
    let xml_arr = ['title', 'sym-tutorial', 'sym-instruction', 'sym-irb', 'worker-info', 'notify-real-sym', 'warning-msg', 'sym-legend'];

    xml_arr.forEach((tag) => {
        // console.log($(`.${tag}`));
        $(`.${tag}`).html($(xml).find(`${tag}`).text());
    })
}

function reloadButtons(xml) {
    let btn_xmls = $(xml).find('buttons').children();  
    // btn_xml = $.parseXML(btn_xml);
    btn_xmls.each((idx, btn_xml)=>{
        let btn_name = $(btn_xml).prop('nodeName');
        $(`.${btn_name}`).html($(btn_xml).text());
    })
}

function reloadFigs(xml) {
    let sym_root_url = $(xml).find('sym-root-url').text();
    $(xml).find('real-img-urls item').each(function () {
        let img_url = `${sym_root_url}/figures/tutorial/${$(this).text()}`
        $(`div#real-images`).append(
            `
            <div class="col-5 border">
                <div class="image">
                    <img src="${img_url}" class="img img-responsive full-width" />
                </div>
            </div>
            `
        );
    });

    $(xml).find('sample-results-urls item').each(function () {
        let img_url = `${sym_root_url}/figures/tutorial/${$(this).text()}`
        $(`div#sample-results`).append(
            `
            <div class="col-5 border">
                <div class="image">
                    <img src="${img_url}" class="img img-responsive full-width" />
                </div>
            </div>
            `
        );
    });
}

function reloadSymDef(xml) {
    // * reload sym-definition
    let sym_root_url = $(xml).find('sym-root-url').text();
    let sym_def_url = `${sym_root_url}/Tutorial/definition.html`;

    $("div#sym-definition").load(`${sym_def_url} div#sym-definition`);

    // $.get(`${sym_def_url}`, function(data){
    //     console.log($(data).find('div#sym-definition').html());
    //     console.log($("div#sym-definition"));
    //     $("div#sym-definition").html($(data).find('div#sym-definition').html());
    // });
}


function reloadPanel(xml){
    let sym_root_url = $(xml).find('sym-root-url').text();
    let label_url = `${sym_root_url}/label.html`;

    $("div#left-panel").load(`${label_url} div#left-panel div`);

    // $.get(`${label_url}`, function(data){
    //     // console.log($(data).find('div#left-panel').html());
    //     // console.log($("div#label-panel"));
    //     $("div#left-panel").html($(data).find('div#left-panel').html());
    // });
}


