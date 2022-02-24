function showHistory() {
    let max_length = 30;
    let max_list = 6;
    let article_ids = getArticles();
    history_button_container.innerHTML = "";
    if (article_ids != null) {
        for (i = article_ids.length - 1; i > article_ids.length - max_list && i >= 0; i--) {
            let article = article_ids[i];
            let [text, _] = getArticle(article);
            text = text.length > max_length ? text.substring(0, max_length - 4) + " ..." : text;
            temp_history = history_template.cloneNode(true);
            temp_link = link_template.cloneNode(true);
            temp_history.innerHTML = "";
            temp_link.id = article;
            temp_link.innerHTML = text;
            temp_history.appendChild(temp_link);
            history_button_container.appendChild(temp_history);

            // Add an event handler for each child
            temp_history.addEventListener("click", () => {
                showArticle(article);
            });
        }

        // Show "more..." button when overflow
        if (article_ids.length >= max_list) {
            history_more.classList.remove("hidden");
        } else {
            history_more.classList.add("hidden");
        }
    } else {
        temp_history = history_template.cloneNode(true);
        temp_history.innerHTML = "😎 No history";
        history_button_container.appendChild(temp_history);
    }
}
