// For preload
window.addEventListener('load', function () {
    const preloader = document.querySelector('.preloader');
    preloader.classList.add('fade-out');
});



// For Flash
setTimeout(function() {
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        alert.style.opacity = '0';
        setTimeout(function () {
            alert.style.display = 'none';
        }, 300);
    });
}, 5000);


// For hamburger menu
function toggleMenu() {
    const menu = document.getElementById('user-menu');
    menu.classList.toggle('show');

    window.addEventListener('click', (event) => {
        if (event.target === menu) {
            menu.style.display = 'none';
        }
    });
}