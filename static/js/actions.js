navbar = document.querySelector('.r-navbar')

shownav.addEventListener('click', () =>{
    navbar.classList.toggle('deploid')
})

hidenav.addEventListener('click', () =>{
    navbar.classList.toggle('deploid')
})

window.addEventListener("load", function () {
    const spinner = document.getElementById("loading-spinner");
    if (spinner) {
    spinner.style.display = "none";
    }
});
