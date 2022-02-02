//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Event Handlers

// Click the "real" input
upload_file_buttton.addEventListener('click', () => {
    file_input.click();
});

// Read file data
file_input.addEventListener('change', function() {

    var fr = new FileReader();
    fr.onload = function(){
        console.log("Got file!");

        // Make sure the # of sentences is > 20 & < 1000
        // NOTE: Splitting by period causes problems in cases like "Analyst John L. Allen said."
        const sentences = fr.result.split('.').map(function (line) {
            return line.replace('\n', '');
        })

        if (sentences.length < 20 || sentences.length > 1000) {
            alertStr = "File cannot have less than 20 sentences or more than 1000. Current #: " + sentences.length.toString();
            showAlert(article_alert, alertStr, "red", "fa-exclamation-triangle")
        }
        else{
            // Create new article
            setArticle(String(+ new Date()), fr.result);
        }
    }
    fr.readAsText(this.files[0]);
})