var prover = ""
var wp_rte = ""
var wp_prop = ""

function toggleList(a){
    if (a === 1) {
        document.getElementById("div1").style.display = "block"
        document.getElementById("div2").style.display = "none"
        document.getElementById("div3").style.display = "none"
    }
    if (a === 2) {
        document.getElementById("div1").style.display = "none"
        document.getElementById("div2").style.display = "block"
        document.getElementById("div3").style.display = "none"
    }
    if (a === 3) {
        document.getElementById("div1").style.display = "none"
        document.getElementById("div2").style.display = "none"
        document.getElementById("div3").style.display = "block"
    }
}

function performAction() {
    document.getElementById("result").innerHTML = prover + " " + wp_rte + " " + wp_prop
}

function toggleChildren(id) {
   var elem = document.getElementById(id)
   if(!elem) alert("error: not found!")
   else {
      if(elem.style.display === "block")
         elem.style.display = "none"
      else
         elem.style.display = "block"
   }
}

function changeProver(input_prover, id) {
    document.getElementById('prover').value = input_prover
    prover = input_prover
    if (id === 0) {
        document.getElementById("Altbtn").innerHTML = "<b style=\"color:yellow;\">Alt-Ergo</b>"
        document.getElementById("Z3btn").innerHTML = "Z3"
        document.getElementById("CVC4btn").innerHTML = "CVC4"
    }
    if (id === 1) {
        document.getElementById("Altbtn").innerHTML = "Alt-Ergo"
        document.getElementById("Z3btn").innerHTML = "<b style=\"color:yellow;\">Z3</b>"
        document.getElementById("CVC4btn").innerHTML = "CVC4"
    }
    if (id === 2) {
        document.getElementById("Altbtn").innerHTML = "Alt-Ergo"
        document.getElementById("Z3btn").innerHTML = "Z3"
        document.getElementById("CVC4btn").innerHTML = "<b style='color:yellow;'>CVC4</b>"
    }
}

function processFormVC() {
    wp_prop = document.getElementById("wp_propflag").value
    wp_rte = document.getElementById("wp_rte").value
    wp_rte = document.getElementById("wp_rte").value
    return false;
}

function processForm(){
    var name = document.getElementById("idname").value
    var age = document.getElementById("idage").value
    var t = document.getElementById("table2")
    var row = t.insertRow()
    var c1 = row.insertCell()
    c1.innerHTML = name
    c1 = row.insertCell()
    c1.innerHTML = age

    var x = document.getElementById("select")
    var option = document.createElement("option")
    option.text = name + " - " + age
    x.add(option)

    var t = document.getElementById("table4")
    var row = t.insertRow()
    var c1 = row.insertCell()
    c1.innerHTML = name
    c1 = row.insertCell()
    c1.innerHTML = age
    c1 = row.insertCell()
    c1.innerHTML = "Added"
    return false
}

function remove() {
    var select = document.getElementById("select")
    var index = select.options.selectedIndex

    var input = select.options[index].value
    var name = input.split(" ")[0]
    var age = input.split(" ")[2]

    var row = t.insertRow()
    var c1 = row.insertCell()
    c1.innerHTML = name
    c1 = row.insertCell()
    c1.innerHTML = age
    c1 = row.insertCell()
    c1.innerHTML = "Deleted"

    document.getElementById("select").remove(index)
    document.getElementById("table2").deleteRow(index + 1)
    
}

$(document).ready(function() {
    $('.add-todo').click(function() {
       $.ajax({
           type: "POST",
           url: "/framacapp/test",
           datatype: "json",
           data: {"filename" : 'filename.c'},
           success: function(data) {
               alert(data.message);
           }
       })
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))
    }

    $.ajaxSetup({
       crossDomain: false,
       beforeSend: function(xhr, settings) {
           if (!csrfSafeMethod(settings.type)) {
               xhr.setRequestHeader("X-CSRFTOKEN", csrftoken)
           }
       }
    });
});