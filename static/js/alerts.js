const alertTimeouts = {}

function showAlert(element, message, color, icon=null, seconds=10000) {
    clearAlert(element)
    if (icon != null) {
        element.children[0].classList.remove("hidden")
        element.children[0].classList.add(icon)
    } else {
        element.children[0].classList.add("hidden")
    }
    element.children[1].innerHTML = message
    element.classList.add(`text-${color}-400`, `border-${color}-400`)
    element.classList.remove("hidden")
    clearTimeout(alertTimeouts[element])
    currTimeout = setTimeout(function () {
        clearAlert(element)
    }, seconds);
    alertTimeouts[element] = currTimeout
}

function clearAlert(element) {
    clearTimeout(alertTimeouts[element])
    color = matchClass(textcolor400, element)
    if (color != null) {
        color = color.replace(textcolor400, '$1')
        icon = matchClass(iconfa, element.children[0])
        console.log(color)
        element.classList.remove(`text-${color}-400`, `border-${color}-400`)
        element.classList.add("hidden")
        element.children[0].classList.replace(icon, "hidden")
        element.children[1].innerHTML = ""
    }
}