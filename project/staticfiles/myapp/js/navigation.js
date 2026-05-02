// قائمة الهاتف الجوال
document.addEventListener("DOMContentLoaded", () => {
    const menuBtn = document.querySelector(".menu-btn");
    const nav = document.querySelector(".nav-links");

    if (menuBtn) {
        menuBtn.addEventListener("click", () => {
            nav.classList.toggle("active");
        });
    }
});
