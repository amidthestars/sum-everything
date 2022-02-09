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
    .then((data) => {
        // If data is null then improper response
        if (data != null){
            let models = data["models"];
            models.sort()
            
            models.forEach(model => {
                let temp_model = available_model_template.cloneNode(true);
                temp_model.value=model
                temp_model.innerHTML=model
                available_models.appendChild(temp_model)
            });
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

    return fetch("/v1/query", options)
    .then(response => { 
        if (response.status == 200){
            return response.json();
        }
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