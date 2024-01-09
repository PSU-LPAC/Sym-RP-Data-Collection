## Introduction
This is the old Recurring Pattern (RP) data collection interface.

## Files
### User Interface (`RecurringPattern/`)
The core files are:
- html
    - `index.html`: the main page of the interface
    - `start.html`: the start page of the interface (will be loaded when the interface is first opened, see `batch.js` -> `loadStart()` for details)
    - `label.html`: the label page of the interface (see `batch.js` -> `loadTask()` for details)
    - `end.html`: the end page of the interface (see `batch.js` -> `loadEnd()` for details)
- js
    - `batch.js`: the batch controller of the interface, loads the start page, label page, and end page, and handles the data collection process
    - `turker.js`: the mturk related functions: defines the annotation canvas, handle callback functions, etc.
    - `reload.js`: reload the interface, from the `rp.xml` file
- xml
    - `rp.xml`: the xml file that defines the interface content, which can be mainly separated into:
        - `<text>`: the text content of the interface, including title, instructions, etc.
        - `<alerts>`: the alert messages that will be shown to the participants
        - `<buttons>`: the buttons used in the interface
        - `<url>`: the urls used in the interface
        - `<figures>`: the figures used in the interface & the tutorial
        - etc.
- css
    - `rp.css`: the css file that defines the style of the interface


### RP Tutorial (`RecurringPattern/Tutorial/`)
The core files are:
- html
    - `tutorial.html`: the main page of the tutorial
    - `rp_test.html`: the test page which partcipants are required to pass before they can start the main task
    - `congrats.html`: the congratulation page after passing the test, with a link to the background survey
- js
    - `rp_test.js`: the functions for the test page (noting that the test page also uses the `../reload.js` and `../turker.js` files)
- xml
    - `tutorial.xml`: the xml file that defines the tutorial content
