// Function gets a list of unique ids from localstorage
function getArticles(most_recent = false) {
    // articles is a list of unique identifiers
    let articles = localStorage.getItem("articles");
    if (articles != null && articles != "[]") {
        articles = JSON.parse(articles);
        articles.sort();
        if (most_recent) {
            return articles[articles.length - 1];
        } else {
            return articles;
        }
    }
    return null;
}

function getArticle(article) {
    let stored_text = localStorage.getItem(article);
    if (stored_text == null) {
        return [null, null];
    } else {
        return JSON.parse(stored_text);
    }
}

function setArticle(id, text) {
    let articles = getArticles();
    if (articles == null) {
        articles = [id];
    } else if (!articles.includes(id)) {
        articles.push(id);
    }
    let [_, summary] = getArticle(id);
    localStorage.setItem(id, JSON.stringify([text, summary]));
    localStorage.setItem("articles", JSON.stringify(articles));
    showArticle(id);
}

function setSummary(id, text, summary) {
    let articles = getArticles();
    if (articles == null) {
        console.log("🤯 Somehow, you made a summary that has no equivalent article...");
        return null;
    }
    localStorage.setItem(id, JSON.stringify([text, summary]));
    showArticle(id);
}

function removeArticle(article) {
    let articles = getArticles();
    var index = articles.indexOf(article);
    if (index !== -1) {
        articles.splice(index, 1);
    }
    localStorage.removeItem(article);
    localStorage.setItem("articles", JSON.stringify(articles));
    article = getArticles((most_recent = true));
    showArticle(article ? article : String(+new Date()));
}

// Function checks unique id in localstorage and updates the article field accordingly
function showArticle(article, edit = false, url_mode = false) {
    // article is a unique identifier
    let input_text = document.getElementById("input-text");
    let [text, summary] = getArticle(article);
    showSummary(summary);
    showHistory();
    if ((text == null && url_mode == false) || edit == true) {
        temp_element = input_template;
        temp_element.children[0].value = text;
        edit_text_toggle.classList.replace("fa-pen-nib", "fa-save");
        upload_link_toggle.classList.replace("fa-save", "fa-link");
    } else if (url_mode == true) {
        url_template.value = null;
        temp_element = url_template;
        upload_link_toggle.classList.replace("fa-link", "fa-save");
        edit_text_toggle.classList.replace("fa-save", "fa-pen-nib");
    } else {
        temp_element = text_template;
        text_template.innerHTML = text.replaceAll(multinewline, "<br><br>");
        edit_text_toggle.classList.replace("fa-save", "fa-pen-nib");
        upload_link_toggle.classList.replace("fa-save", "fa-link");
    }
    input_text.remove();
    temp_element.id = "input-text";
    article_area.append(temp_element);
    current_id = article;

    // a bit of button/info cleanup
    new_text_button.classList.remove("hidden");
    remove_text_button.classList.remove("hidden");
    get_summary_button.classList.remove("hidden");
    if (edit == true) {
        countChars();
        new_text_button.classList.add("hidden");
    }
    if (url_mode == true) {
        new_text_button.classList.add("hidden");
    }
    if (getArticles() == null) {
        new_text_button.classList.add("hidden");
        remove_text_button.classList.add("hidden");
    }
    if (text == null || edit == true) {
        get_summary_button.classList.add("hidden");
    }

    cleanupButtons(article_button_container);
    cleanupButtons(summary_button_container);
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
edit_text_toggle.addEventListener("click", () => {
    if (edit_text_toggle.classList.contains("fa-save")) {
        let input_text = document.getElementById("input-textarea");

        // CheckAscii holds array of values not in normal unicode "ascii" area
        checkAscii = input_text.value.match(/[^\u0000-\u007f]/);

        if (checkAscii != null) {
            caLen = checkAscii.length;
            numNonAsciiVals = caLen;

            // If there was a value picked up in checkAscii make sure it isn't unicode \u2018-\u201f
            for (let i = 0; i < caLen; i++) {
                if (!checkAscii[i].match(/[^\u2010-\u201f]/)) {
                    checkAscii[i] = checkAscii[i].match(/[^\u2010-\u201f]/);
                    numNonAsciiVals -= 1;
                }
            }
        } else numNonAsciiVals = 0;

        // Check that text is proper length
        if (input_text.value.length < 20 || input_text.value.length > 5000) {
            showAlert(
                article_alert,
                "Input length cannot be less than 20 or more than 5000 characters",
                "red",
                ["fa-exclamation-triangle"]
            );
            redShake(input_text);
        }
        // Check that text is not binary
        else if (numNonAsciiVals > 0) {
            showAlert(article_alert, "Input must be plain text!", "red", [
                "fa-exclamation-triangle",
            ]);
            redShake(input_text);
        } else {
            setArticle(current_id, input_text.value);
            showArticle(current_id, (edit = false));
        }
    } else if (edit_text_toggle.classList.contains("fa-pen-nib")) {
        showArticle(current_id, (edit = true));
    }
});

//Event trigger for uploading a link
upload_link_toggle.addEventListener("click", () => {
    let input_text;

    if (upload_link_toggle.classList.contains("fa-save")) {
        // Check whether we have textarea (beginning) or url text
        try {
            input_text = document.getElementById("input-textarea");
            console.log(input_text.value);
        } catch (error) {
            console.log(error);
            input_text = url_template;
            console.log(input_text.value);
        }

        // Send data to flask backend to scrape from page
        fetch(`${window.origin}/parse-js-link`, {
            method: "POST",
            credentials: "include",
            body: JSON.stringify(input_text.value),
            cache: "no-cache",
            headers: new Headers({
                "content-type": "application/json",
            }),
        })
            .then(function (response) {
                if (response.status !== 200) {
                    showAlert(article_alert, "Page could not be reached!", "red", [
                        "fa-exclamation-triangle",
                    ]);
                    showArticle(current_id, (edit = true));
                    return;
                }
                response.json().then(function (article_data) {
                    //console.log(article_data);
                    if (article_data == 0) {
                        showAlert(article_alert, "Page could not be reached!", "red", [
                            "fa-exclamation-triangle",
                        ]);
                    } else {
                        setArticle(current_id, article_data.article);
                        showArticle(current_id, (edit = false));
                    }
                });
            })
            .catch(function (error) {
                showAlert(article_alert, "Error in the backedn... Please stand!", "red", [
                    "fa-exclamation-triangle",
                ]);
                console.log("Fetch error: " + error);
            });
    } else if (upload_link_toggle.classList.contains("fa-link")) {
        showArticle(String(+new Date()), (edit = false), (url_mode = true));
    }
});

//Event trigger for starting new article
new_text_button.addEventListener("click", () => {
    showArticle(String(+new Date()), (edit = true));
});

//Event trigger for removing current article
remove_text_button.addEventListener("click", () => {
    removeArticle(current_id);
    countChars();
});

//Copy trigger
copy_summary_buttton.addEventListener("click", () => {
    navigator.clipboard.writeText(summary_text.innerHTML);
});

get_summary_button.addEventListener("click", () => {
    let [text, _] = getArticle(current_id);
    getSummary(available_models.value, text);
});

//Character count to textarea
document.addEventListener("keyup", countChars);

function countChars() {
    const input_text = document.getElementById("input-textarea");
    try {
        var numChars = input_text.value.length;
        var currChars = document.getElementById("current");

        currChars.textContent = numChars.toString();
        if (numChars < 20 || numChars > 5000) {
            currChars.classList.replace("inherit", "text-red-400");
        } else {
            currChars.classList.replace("text-red-400", "inherit");
        }
    } catch {}
}
