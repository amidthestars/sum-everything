function getModels() {
    available_models.innerHTML=""
    fetch('/v1/models')
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        let models = data["models"];
        models.sort()
        
        models.forEach(model => {
            let temp_model = available_model_template.cloneNode(true);
            temp_model.value=model
            temp_model.innerHTML=model
            available_models.appendChild(temp_model)
        });
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
        return response.json();
    })
    .then(data => {
        return data;
    });
}
