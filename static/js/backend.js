function getModels() {
    available_models.innerHTML = "";
    fetch("/v1/models")
        .then((response) => {
            if (response.status != 200) {
                showAlert(article_alert, "Cannot get model data", "red", [
                    "fa-exclamation-triangle",
                ]);
            } else {
                return response.json();
            }
        })
        .then((models) => {
            // If data is null then improper response
            if (models != null) {
                for (const [key, value] of Object.entries(models)) {
                    let temp_model = available_model_template.cloneNode(true);
                    temp_model.value = key;
                    temp_model.innerHTML = key;
                    temp_model.disabled = !value;
                    available_models.appendChild(temp_model);
                }
            }
        });
}

function getSummary(model, input) {
    if (socket_available) {
        socket_available = false;
        socket.emit("query", {
            model: model,
            input: input,
        });
    }
}

socket.on("model_ack", function (data) {
    /*
    flow should be:
    [query] -> received -> cleaned -> [result]
    Things in brackets are handled by other opera   tors
    */

    let [msg, color, icon] = [data["message"], data["color"], data["icon"]];
    switch (data["status"]) {
        case "received":
            showAlert(summary_alert, msg, color, icon, 1200000);
            break;
        case "cleaned":
            showAlert(summary_alert, msg, color, icon, 1200000);
            setArticle(current_id, data["inputs"]);
            break;
    }
});

socket.on("model_response", function (data) {
    let [msg, color, icon] = [data["message"], data["color"], data["icon"]];
    // enabling get summary button after the query
    get_summary_button.classList.remove("pointer-events-none");
    get_summary_button.classList.remove("opacity-50");
    switch (data["status"]) {
        case "success":
            showAlert(summary_alert, msg, color, icon, 18000);
            let [text, summary] = [data["inputs"][0], data["outputs"][0]];
            setSummary(current_id, text, summary);
            break;
        case "error":
            showAlert(summary_alert, msg, color, icon, 18000);
            console.log(data["info"]);
            break;
    }
    socket_available = true;
});

socket.on("connect", function () {
    console.log("CONNECTED");
});
