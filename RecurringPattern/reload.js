// * Reload the html content from XML

function reloadMain(xml) {
    reloadText(xml);
    reloadAlert(xml);
    reloadButtons(xml);
}

function reloadText(xml) {
    let text_xmls = $(xml).find('text').children(); 

    text_xmls.each((idx, text_xml)=>{
        let text_name = $(text_xml).prop('nodeName');
        $(`.${text_name}`).html($(text_xml).text());
    })
}

function reloadTime(min_time, max_time) {
    $(`span.min-time`).text(min_time);
    $(`span.max-time`).text(max_time);
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
        let caption = $(btn_xml).find('caption').text();
        let tooltip = $(btn_xml).find('tooltip').text();

        // set button common properties
        $(`.${btn_name}`).attr('data-bs-toggle', 'tooltip');
        $(`.${btn_name}`).attr('data-bs-placement', 'top');
        $(`.${btn_name}`).attr('data-bs-trigger', 'hover');
        $(`.${btn_name}`).attr('data-bs-html', true);

        $(`.${btn_name}`).html(caption);
        $(`.${btn_name}`).attr('title', tooltip);
    })

    initialTooltips();
}

function reloadButton(btn_name, xml){
    let btn_xml = $(xml).find(`buttons ${btn_name}`);
    let caption = $(btn_xml).find('caption').text();
    let tooltip = $(btn_xml).find('tooltip').text();
    $(`.${btn_name}`).html(caption);
    $(`.${btn_name}`).prop('title', tooltip);

    console.log($(`.${btn_name}`));
    $(`.${btn_name}`).tooltip();
}

function reloadPanel(xml){
    let sym_root_url = $(xml).find('sym-root-url').text();
    let label_url = `${sym_root_url}/label.html`;

    $("div#left-panel").load(`${label_url} div#left-panel div`);

}

function reloadRPFigs(xml) {
    // * reload RP figures for tutorial
    let rp_root_url = $(xml).find('rp-root-url').text(); 
    rp_root_url = '..';
    let figs = $(xml).find('figures').children();

    figs.each((_, fig_xmls)=>{
        let fig_container = $(fig_xmls).prop('nodeName');
        console.log(fig_container);
        console.log(fig_xmls);

        $(fig_xmls).find('item').each((_, fig_xml)=> {
            var url = $(fig_xml).find('url').text();
            url = rp_root_url + url
            var caption = $(fig_xml).find('caption').text();
            // console.log(url, caption);
            $(`.${fig_container}`).append(` 
                <div class="col-6 d-flex justify-content-center">
                    <figure class="figure">
                        <img src="${url}" class="figure-img img-fluid rounded">
                        <figcaption class="figure-caption text-center">
                            ${caption}
                        </figcaption>
                    </figure>
                </div>
            `);
        })

        
    })

}

function initialTooltips() {
    console.log($('[data-bs-toggle="tooltip"]'));
    $('[data-bs-toggle="tooltip"]').tooltip();
}
