document.addEventListener("DOMContentLoaded", function(event) { 
    document.getElementById("form").reset();
});

function changeEditForm(button, menu_item){
    var object_id = button.id.replace("edit_object_", "");
    var form = document.getElementById("editForm"+menu_item);
    form.children[1].value = object_id;
    var elements = button.parentElement.getElementsByClassName("table-data");
    var values = [];
    for(var i = 1; i  < elements.length; i++){
        values.push(elements[i].textContent);
    }

    var inputs = form.children[2].children[0].children[1].getElementsByTagName("input");
    for(var i = 0; i  < inputs.length; i++){
        if(inputs[i].name == "password") continue;
        inputs[i].value = values[i];
    }
}