function update(output, wrapper, model) {
    output.innerHTML = `<b>${model.get("sender")}:</b> ${model.get("message")}`;
    wrapper.style.cssText = model.get("inline_style");
}

function render({ model, el }) {
    
    let output = document.createElement("span")

    let button = document.createElement("i");
    button.onclick = () => {
        model.send("edit_request")
    }
    button.style.display = 'none';
    button.className = "fas fa-edit"

    let wrapper = document.createElement("div");
    wrapper.onmouseover = () => {
        button.style.display = 'inline-block';
    }
    wrapper.onmouseleave = () => {
        button.style.display = 'none';
    }

    wrapper.appendChild(output);
    wrapper.appendChild(button);
    el.appendChild(wrapper)

    let update_func = update.bind(this, output, wrapper, model);
    model.on('change', update_func)
    update_func()
}

export default {render};