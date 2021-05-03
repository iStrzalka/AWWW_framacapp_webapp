var current_filename = ""
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

function hide_section(id) {
    document.getElementById("section" + id).style.display = "none"
    document.getElementById("hidden_section" + id).style.display = "block"
}

function unhide_section(id) {
    document.getElementById("section" + id).style.display = "block"
    document.getElementById("hidden_section" + id).style.display = "none"
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

function addfile_form() {
    document.getElementById("printfile").style.display = "none"
    document.getElementById("addfileform").style.display = "block"
    document.getElementById("adddirform").style.display = "none"
    document.getElementById("removefile").style.display = "none"

    $.ajax({
           type: "POST",
           url: "/add_file/",
           datatype: "json",
           data: {"user" : current_filename},
           success: function(data) {
               document.getElementById('addfileform').innerHTML = data.form;
           }
    })
}

function reload_tree() {
    $.ajax({
           type: "POST",
           url: "/reload_tree/",
           datatype: "json",
           data: {"user" : current_filename},
           success: function(data) {
               document.getElementById('tree').innerHTML = data.tree;
           }
    })
}

function add_filep() {
    var fd = new FormData();
    fd.append("name", document.getElementById('id_name').value)
    fd.append("id_parent", document.getElementById('id_parent').value)
    fd.append("description", document.getElementById('id_description').value)
    fd.append("file", document.getElementById('id_Provide_file').files[0])

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/add_filep/", true)
    xhr.send(fd)
    reload_tree()
}

function adddir_form() {
    document.getElementById("printfile").style.display = "none"
    document.getElementById("addfileform").style.display = "none"
    document.getElementById("adddirform").style.display = "block"
    document.getElementById("removefile").style.display = "none"

    $.ajax({
           type: "POST",
           url: "/add_dir/",
           datatype: "json",
           data: {"user" : current_filename},
           success: function(data) {
               document.getElementById('adddirform').innerHTML = data.form;
           }
    })
}

function add_dirp() {
    var fd = new FormData();
    fd.append("name", document.getElementById('id_namedir').value)
    fd.append("id_parent", document.getElementById('id_parentdir').value)
    fd.append("description", document.getElementById('id_descriptiondir').value)

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/add_dirp/", true)
    xhr.send(fd)
    reload_tree()
}

function remove_form() {
    document.getElementById("printfile").style.display = "none"
    document.getElementById("addfileform").style.display = "none"
    document.getElementById("adddirform").style.display = "none"
    document.getElementById("removefile").style.display = "block"

    $.ajax({
           type: "POST",
           url: "/remove/",
           datatype: "json",
           data: {"user" : current_filename},
           success: function(data) {
               document.getElementById('removefile').innerHTML = data.form;
           }
    })
}

async function remove(file) {
    if (file === 'file') {
        $.ajax({
            type: "POST",
            url: "/removep/",
            datatype: "json",
            data: {
                "isfile": true,
                "id": document.getElementById('id_Remove_File').value
            },
            success: function (data) {

            }
        })
    } else {
        $.ajax({
            type: "POST",
            url: "/removep/",
            datatype: "json",
            data: {
                "isfile": false,
                "id": document.getElementById('id_Remove_Directory').value
            },
            success: function (data) {

            },
        })
    }
    await reload_tree()
    remove_form()
}


function changeProver(input_prover, id) {
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

function get_file_contents(filename) {
    document.getElementById("printfile").style.display = "block"
    document.getElementById("addfileform").style.display = "none"
    document.getElementById("adddirform").style.display = "none"
    document.getElementById("removefile").style.display = "none"
    current_filename = filename;
    $.ajax({
           type: "POST",
           url: "/load_file/",
           datatype: "json",
           data: {"filename" : filename},
           success: function(data) {
               document.getElementById('program-elements').innerHTML = data.program_elements;
               document.getElementById('filecontent').innerHTML = data.content;
           }
    })
}


function run_prover() {
    document.getElementById('program-elements').innerHTML = "Processing request";
    $.ajax({
           type: "POST",
           url: "/run_prover/",
           datatype: "json",
           data: {"filename" : current_filename},
           success: function(data) {
               document.getElementById('program-elements').innerHTML = data.result;
           }
    })
}

function changeresult() {
    document.getElementById('result').innerHTML = "Processing request";
    $.ajax({
           type: "POST",
           url: "/get_result/",
           datatype: "json",
           data: {"filename" : current_filename,
                  "prover" : prover,
                  "wp_rte" : wp_rte,
                  "wp_propflag" : wp_prop},
           success: function(data) {
               document.getElementById('result').innerHTML = data.result;
           }
    })
    toggleList(3);
}

$(document).ready(function() {
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