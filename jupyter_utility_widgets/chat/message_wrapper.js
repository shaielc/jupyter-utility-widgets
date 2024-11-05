async function unpack_model(model_id, manager) {
    return await manager.get_model(model_id.slice("IPY_MODEL_".length))

}

async function update(label, output, wrapper, model) {
    label.innerHTML = `<b>${model.get("sender")}:</b>`;
    let child_model = await unpack_model(model.get("child"), model.widget_manager)
    let child_view = await model.widget_manager.create_view(child_model);
    output.appendChild(child_view.el)
    wrapper.style.cssText = model.get("inline_style");
}

function render({ model, el }) {
    let output = document.createElement("div")
    let label = document.createElement("span")
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

    wrapper.appendChild(label)
    wrapper.appendChild(output);
    wrapper.appendChild(button);
    el.appendChild(wrapper)

    let update_func = update.bind(this, label, output, wrapper, model);
    model.on('change', update_func)
    update_func()
}

export default {render};