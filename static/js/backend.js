function getModels() {
    available_models.innerHTML=""
    fetch('/v1/models')
    .then((response) => {
        if (response.status != 200){
            showAlert(article_alert, "Cannot get model data", "red", "fa-exclamation-triangle");
        }
        else{
            return response.json();
        }
    })
    .then((models) => {
        // If data is null then improper response
        if (models != null){
            for (const [key, value] of Object.entries(models)) {
                let temp_model = available_model_template.cloneNode(true);
                temp_model.value = key
                temp_model.innerHTML = key
                temp_model.disabled = !value 
                available_models.appendChild(temp_model)
            }
        }
      })
}

function getSummary(input) {
    let options = {
        "method": "POST",
        "headers": {
            "Content-Type": "application/json;charset=utf-8"
        },
        "body": JSON.stringify(
            {
                "model": available_models.value,
                "input": input
            }
        )
    };

    console.log("FETCHING SUMMARY");
    showAlert(summary_alert, "Loading article summary... \nGive us a second :)", "green", null, 120000);

    return fetch("/v1/query", options)
    .then(response => { 
        if (response.status == 200){

            //console.log("FETCHING SUCCEEDED!");
            showAlert(summary_alert, "Summary received!", "green");

            return response.json();
        }
        showAlert(summary_alert, "Failed to receive summary.", "red", "fa-exclamation-triangle");
    })
    .then(data => {
        return data;
    });
}

/*
socket.on('connect', function() {
    console.log("CONNECTED")
    socket.emit('message', {data: 'I\'m connected!'});
});
*/