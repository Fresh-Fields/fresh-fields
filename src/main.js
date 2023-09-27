/* ////////////////////////////////
  ////  login related events  ////
 //////////////////////////////// */

let login_button = document.querySelector(".start_button");
let login_popup = document.querySelector(".login-container");
let exitkeys = document.querySelectorAll("#login-exit");

// if "get started" is clicked
login_button.onclick = () => {
  login_popup.classList.remove("hidden");
}

exitkeys.forEach(e => {
  e.onclick = () => {
    login_popup.classList.add("hidden");
  }
});