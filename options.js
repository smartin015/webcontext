// Save this script as `options.js`

// Saves options to localStorage.
function save_options() {
  var select = document.getElementById("exttype");
  var exttype = select.children[select.selectedIndex].value;
  localStorage["exttype"] = exttype;

  var server_url = document.getElementById("server_url").value;
  localStorage["server_url"] = server_url;
  
  // Update status to let user know options were saved.
  var status = document.getElementById("status");
  status.innerHTML = "Options Saved.";
  setTimeout(function() {
    status.innerHTML = "";
  }, 750);
}

// Restores select box state to saved value from localStorage.
function restore_options() {
  var exttype = localStorage["exttype"];
  if (!exttype) {
    return;
  }
  var select = document.getElementById("exttype");
  for (var i = 0; i < select.children.length; i++) {
    var child = select.children[i];
    if (child.value == exttype) {
      child.selected = "true";
      break;
    }
  }
  
  document.getElementById("server_url").value = localStorage["server_url"];
}
document.addEventListener('DOMContentLoaded', restore_options);
document.querySelector('#save').addEventListener('click', save_options);