// This 

// Function to fetch configuration settings
async function fetchConfig() {
    try {
        const response = await fetch('config.json');
        return await response.json();
    } catch (error) {
        console.error("Error fetching config:", error);
        // Handle error appropriately
    }
}

// Function to reload text content from the JSON configuration
async function reloadText() {
    const config = await fetchConfig();
    const texts = config.text;

    for (let textName in texts) {
        if (texts.hasOwnProperty(textName)) {
            $(`.${textName}`).html(texts[textName]);
        }
    }
}


// * Load the start page
async function loadStart(callback = null) {
    const config = await fetchConfig();
    const root_url = config.rootUrl;

    $("div#root-container").load(`${root_url}/start.html div#container`, async function () {
        console.log("Load start page was performed.");

        // Call other necessary functions to set up the start page
        setupStartPage(config);

        // Bind the buttons
        $("#tutorial-btn").click(() => {
            window.open(config.tutorialUrl);
        });

        $("#task-btn").click(() => {
            loadTask(callback);
        });

        if (callback != null) { callback(); }
    });
}

// Setup function for the start page
function setupStartPage(config) {
    // Set up texts, rewards, times, etc. from config
    // Example: $("#some-element").text(config.someText);
}

// * Load the task page
async function loadTask(img_urls, callback = null) {
    const config = await fetchConfig();
    const root_url = config.rootUrl;

    $("div#root-container").load(`${root_url}/label.html div#container`, function () {
        console.log("Load task page was performed.");

        // Set up the image for annotation
        $("#pic").attr("src", img_urls[img_idx]);
        setupTaskPage(config, img_urls);

        $('#pic').load(function () {
            console.log(`Image ${$("#pic").attr("src")} is loaded!`);
            // Additional setup if needed
        });
    });
}

// Setup function for the task page
function setupTaskPage(config, img_urls) {
    // Set up tasks, alerts, buttons, etc. from config
}


// * Load the end page
async function loadEnd(callback = null) {
    const config = await fetchConfig();
    const root_url = config.rootUrl;

    $("div#root-container").load(`${root_url}/end.html div#container`, function () {
        console.log("Load end page was performed.");

        // Call other necessary functions to set up the end page
        setupEndPage(config);

        // Submit functionality
        $(".btn#all-submit").click(function () {
            var suggestion = $('textarea#suggestions').val();
            $("input#annos").val(JSON.stringify(all_annos));
            $("crowd-form")[0].submit();
        });

        if (callback != null) { callback(); }
    });
}

// Setup function for the end page
function setupEndPage(config) {
    // Set up texts, rewards, etc. from config
}