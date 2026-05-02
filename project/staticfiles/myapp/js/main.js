// تشغيل أي شيء عام في الموقع
document.addEventListener("DOMContentLoaded", () => {
    console.log("Main.js loaded successfully");

    // تحديث رقم السلة من session (باستخدام endpoint)
    updateCartCount();
});

// -------------------------------
// تحديث عدّاد السلة في الهيدر
// -------------------------------
function updateCartCount() {
    fetch("/cart/count/")
        .then(response => response.json())
        .then(data => {
            const count = data.count;
            const cartCountElement = document.querySelector(".cart-count");

            if (cartCountElement) {
                cartCountElement.textContent = count;
            }
        })
        .catch(err => console.log("Error:", err));
}
