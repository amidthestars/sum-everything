const alertTimeouts = {};

function showAlert(element, message, color, icon_class = null, seconds = 10000) {
    clearAlert(element);
    if (icon_class != null) {
        element.children[0].classList.add("fas", "pr-4");
        DOMTokenList.prototype.add.apply(element.children[0].classList, icon_class);
    }
    element.children[1].innerHTML = message;
    element.classList.add(`text-${color}-400`, `border-${color}-400`);
    element.classList.remove("hidden");
    clearTimeout(alertTimeouts[element]);
    currTimeout = setTimeout(function () {
        clearAlert(element);
    }, seconds);
    alertTimeouts[element] = currTimeout;
}

function clearAlert(element) {
    clearTimeout(alertTimeouts[element]);
    color = matchClass(textcolor400, element);
    if (color != null) {
        color = color.replace(textcolor400, "$1");
        element.classList.remove(`text-${color}-400`, `border-${color}-400`);
        element.classList.add("hidden");
        element.children[0].className = "";
        element.children[1].innerHTML = "";
    }
}
