// Function gets a list of unique ids from localstorage
function getArticles(most_recent = false) {
    // articles is a list of unique identifiers
    let articles = localStorage.getItem('articles');
    if (articles != null && articles != "[]") {
        articles = JSON.parse(articles);
        articles.sort();
        if (most_recent) {
            return articles[articles.length - 1]
        } else {
            return articles
        }
    }
    return null
}

function getArticle(article) {
    let stored_text = localStorage.getItem(article);
    if (stored_text == null) {
        return [null, null]
    } else {
        return JSON.parse(stored_text)
    }
}

function setArticle(article, text) {
    let articles = getArticles()
    if (articles == null) {
        articles = [article]
    } else if  (!articles.includes(article)) {
        articles.push(article)
    }
    let [_, summary] = getArticle(article);
    localStorage.setItem(article, JSON.stringify([text, summary]))
    localStorage.setItem("articles", JSON.stringify(articles))
    showArticle(article);
}

function removeArticle(article) {
    let articles = getArticles()
    var index = articles.indexOf(article);
    if (index !== -1) {
        articles.splice(index, 1);
    }
    localStorage.removeItem(article)
    localStorage.setItem("articles", JSON.stringify(articles))
    article = getArticles(most_recent=true)
    showArticle((article) ? article : String(+ new Date()));
}

// Function checks unique id in localstorage and updates the article field accordingly
function showArticle(article, edit=false) {
    // article is a unique identifier
    let input_text = document.getElementById("input-text");
    let [text, summary] = getArticle(article);
    showSummary(summary)
    showHistory();
    if (text == null || edit == true) {
        temp_element = input_template;
        temp_element.value = text;
        edit_text_toggle.classList.replace("fa-pen-nib", "fa-save");
    } else {
        temp_element = text_template;
        text_template.innerHTML = text.replaceAll(multinewline, "<br><br>");
        edit_text_toggle.classList.replace("fa-save", "fa-pen-nib");
    }
    input_text.remove()
    temp_element.id = "input-text";
    article_area.append(temp_element);
    current_id = article;

    // a bit of buton cleanup
    new_text_button.classList.remove("hidden")
    remove_text_button.classList.remove("hidden")
    if (edit == true) {
        new_text_button.classList.add("hidden")
    }
    if (getArticles() == null) {
        new_text_button.classList.add("hidden")
        remove_text_button.classList.add("hidden")
    }

    cleanupButtons(article_button_container);
    cleanupButtons(summary_button_container);
}

function showArticles() {

}

function showSummary(summary) {
    if (summary == null) {
        summary_text.innerHTML = "🤔 I don't think I've done this one yet!";
        copy_summary_buttton.classList.add("hidden");
    } else {
        summary_text.innerHTML = summary;
        copy_summary_buttton.classList.remove("hidden");
    }
}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Event Handlers

// Event trigger for editing/saving text
edit_text_toggle.addEventListener('click', () => {
    if (edit_text_toggle.classList.contains("fa-save")) {
        let input_text = document.getElementById("input-text");
        if (input_text.value.length < 20) {
            redShake(input_text)
        } else {
            setArticle(current_id, input_text.value)
            showArticle(current_id, edit=false);
        }
    } else if (edit_text_toggle.classList.contains("fa-pen-nib")) {
        showArticle(current_id, edit=true);
    }
});

//Event trigger for starting new article
new_text_button.addEventListener('click', () => {
    showArticle(String(+ new Date()), edit=true);
});

//Event trigger for removing current article
remove_text_button.addEventListener('click', () => {
    removeArticle(current_id);
});

//Copy trigger
copy_summary_buttton.addEventListener('click', () => {
    navigator.clipboard.writeText(summary_text.innerHTML);
});