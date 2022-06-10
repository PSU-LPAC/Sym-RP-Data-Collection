// Reload the html content from XML

function reloadMain(xml) {
    reloadText(xml);

    reloadSymDef(xml);

    reloadFigs(xml);
}

function reloadText(xml) {
    // * reload Text
    let xml_arr = ['title', 'sym-tutorial', 'sym-instruction', 'sym-irb', 'worker-info', 'notify-real-sym', 'warning-msg', 'sym-legend'];

    xml_arr.forEach((tag) => {
        // console.log($(`#${tag}`));
        $(`#${tag}`).html($(xml).find(`${tag}`).text());
    })
}

function reloadSymDef(xml) {
    // * reload sym-definition
    let sym_root_url = $(xml).find('sym-root-url').text();
    let sym_def_url = `${sym_root_url}/Tutorial/definition.html`;
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


