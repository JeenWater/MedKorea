// for buttons on the sign up page
const Ybtn = document.getElementById("yes-btn");
const Nbtn = document.getElementById("no-btn");
const first_visit = document.getElementById("first_visit");

Ybtn.addEventListener("click", function(){
    if (Ybtn.classList.contains("active")) {
        Ybtn.classList.remove("active");
        Ybtn.style.backgroundColor = "";
        first_visit.value = "";
    } else {
        first_visit.value = "Yes";
        Ybtn.classList.add("active");
        Ybtn.style.backgroundColor = "#1ABC9C";
        Nbtn.classList.remove("active");
        Nbtn.style.backgroundColor = "";
    }
});

Nbtn.addEventListener("click", function() {
    if (Nbtn.classList.contains("active")) {
        Nbtn.classList.remove("active");
        Nbtn.style.backgroundColor = "";
        first_visit.value = "";
    } else {
        first_visit.value = "No";
        Nbtn.classList.add("active");
        Nbtn.style.backgroundColor = "#E74C3C";
        Ybtn.classList.remove("active");
        Ybtn.style.backgroundColor = "";
    }
});