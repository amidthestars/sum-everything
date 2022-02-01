//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Event Handlers

// Click the "real" input
upload_file_buttton.addEventListener('click', () => {
    file_input.click();
});

// Read file data
file_input.addEventListener('change', function() {
    var fr = new FileReader();
    fr.onload = function(){
        // Create new article
        setArticle(String(+ new Date()), fr.result);
    }
    fr.readAsText(this.files[0]);
})