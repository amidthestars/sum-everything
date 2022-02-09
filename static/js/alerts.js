function showAlert(element, message, color, icon=null, seconds=10000) {
    if (icon != null) {
        element.children[0].classList.remove("hidden")
        element.children[0].classList.add(icon)
    } else {
        element.children[0].classList.add("hidden")
    }
    element.children[1].innerHTML = message
    element.classList.add(`text-${color}-400`, `border-${color}-400`)
    element.classList.remove("hidden")
    setTimeout(function () {
        element.classList.remove(`text-${color}-400`, `border-${color}-400`)
        element.classList.add("hidden")
        element.children[0].classList.replace(icon, "hidden")
        element.children[1].innerHTML = ""
    }, seconds);
}