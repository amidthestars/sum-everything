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