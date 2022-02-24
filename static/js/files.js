//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Event Handlers

// Click the "real" input
upload_file_buttton.addEventListener("click", () => {
    file_input.click();
});

// Read file data
file_input.addEventListener("change", function () {
    var fr = new FileReader();
    fr.onload = function () {
        console.log("Got file!");

        resLen = fr.result.length;

        // Check proper file length
        if (resLen < 20 || resLen > 5000) {
            alertStr =
                "Input length cannot be less than 20 or more than 5000 characters. Current length: " +
                fr.result.length;
            showAlert(article_alert, alertStr, "red", ["fa-exclamation-triangle"], 20000);
        } else {
            // CheckAscii holds array of values not in normal unicode "ascii" area
            checkAscii = fr.result.match(/[^\u0000-\u007f]/);

            if (checkAscii != null) {
                caLen = checkAscii.length;
                numNonAsciiVals = caLen;

                // If there was a value picked up in checkAscii make sure it isn't unicode \u2018-\u201f
                for (let i = 0; i < caLen; i++) {
                    if (!checkAscii[i].match(/[^\u2018-\u201f]/)) {
                        checkAscii[i] = checkAscii[i].match(/[^\u2018-\u201f]/);
                        numNonAsciiVals -= 1;
                    }
                }
            } else {
                numNonAsciiVals = 0;
            }

            if (numNonAsciiVals > 0) {
                showAlert(article_alert, "File must be plain text!", "red", [
                    "fa-exclamation-triangle",
                ]);
            } else {
                // Create new article
                showAlert(article_alert, "Article submitted!", "green");
                setArticle(String(+new Date()), fr.result);
            }
        }
    };

    // Reads as plain text
    fr.readAsText(this.files[0]);
});
