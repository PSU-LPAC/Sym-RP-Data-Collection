// Reload the html content from XML

function reloadMain(xml) {
    reloadText(xml);
    reloadAlert(xml);
    reloadSymDef(xml);
    reloadFigs(xml);
    reloadButtons(xml);
}

function reloadText(xml) {
    let text_xmls = $(xml).find('text').children(); 

    text_xmls.each((idx, text_xml)=>{
        let text_name = $(text_xml).prop('nodeName');
        $(`.${text_name}`).html($(text_xml).text());
    })
}

function reloadAlert(xml) {
    let alert_xmls = $(xml).find('alerts').children(); 

    alert_xmls.each((idx, alert_xml)=>{
        let alert_name = $(alert_xml).prop('nodeName');
        $(`.${alert_name}`).html($(alert_xml).text());
    })
}

function reloadReward(xml, num_imgs, basic_reward, per_reward, valid_num=0) {
    $(`span.num-imgs`).text(num_imgs);
    $(`span.valid-num`).text(valid_num);

    $(`span.basic-reward`).text(basic_reward.toFixed(2));
    $(`span.total-reward`).text((num_imgs*per_reward).toFixed(2));
    $(`span.bonus-reward`).text(Math.max(0, num_imgs*per_reward - basic_reward).toFixed(2));
    $(`span.real-bonus-reward`).text(Math.max(0, valid_num * per_reward-basic_reward).toFixed(2));

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


