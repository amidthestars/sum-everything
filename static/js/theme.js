// Define a function that returns the theme defined by localStorage
function getTheme() {
    let theme = localStorage.getItem("theme");
    if (theme == null) {
        localStorage.setItem("theme", "light");
        theme = "light";
    }
    return theme;
}

// Define a function that sets the theme
function setTheme(theme) {
    if (theme == "dark") {
        localStorage.setItem("theme", "dark");
        dark_mode_toggle.innerHTML = "☀️";
        body.classList.replace("text-gray-700", "text-gray-300");
        body.classList.replace("bg-gray-100", "bg-gray-900");
    } else if (theme == "light") {
        localStorage.setItem("theme", "light");
        dark_mode_toggle.innerHTML = "🌙";
        body.classList.replace("text-gray-300", "text-gray-700");
        body.classList.replace("bg-gray-900", "bg-gray-100");
    } else {
        console.log("Not a valid theme.");
    }
}

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Event Handlers

// When button is clicked, set theme to the inverse
dark_mode_toggle.addEventListener("click", () => {
    if (getTheme() == "light") {
        setTheme("dark");
    } else if (getTheme() == "dark") {
        setTheme("light");
    } else {
        console.log("Not a valid theme.");
    }
});
