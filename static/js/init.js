// At initial load, set theme to last set
setTheme(getTheme());

// On page load, check if there are stored articles. If not, load empty, if so, load omst recent
let init_article = getArticles(most_recent=true)
showArticle((init_article) ? init_article : current_id);

// On page load, show summary history
showHistory()

// On page load, get models avaiable
getModels()