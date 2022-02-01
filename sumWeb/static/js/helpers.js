function redShake(element, shake_style="shake-horizontal", seconds=500) {
    element.classList.replace("border-gray-400", "border-red-400")
    element.classList.add(shake_style, "mb-2.5")
    setTimeout(function () {
        element.classList.remove(shake_style, "mb-2.5")
        element.classList.replace("border-red-400", "border-gray-400")
    }, seconds);
}

function matchClass(pattern, element) {
    for (i=0; i<element.classList.length; i++) {
        if (pattern.test(element.classList[i])) {
            return element.classList[i]
        }
    }
}

function visibleChildren(element) {
    let num_visible = 0
    element.childNodes.forEach(item => {
        if (item.nodeType != Node.TEXT_NODE && !item.classList.contains("hidden")) {
            num_visible += 1;
        }
    });
    return num_visible
}

function cleanupButtons(element) {
    element.classList.remove(matchClass(numcol, element));
    element.classList.add(`grid-cols-${visibleChildren(element)}`);
}