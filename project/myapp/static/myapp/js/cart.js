// إضافة منتج للسلة باستخدام Ajax
function addToCart(productId) {
    fetch(`/add-to-cart/${productId}/`)
        .then(() => {
            alert("تمت إضافة المنتج إلى السلة!");
            updateCartCount();
        })
        .catch(err => console.log(err));
}

// حذف منتج من السلة
function removeFromCart(productId) {
    fetch(`/remove/${productId}/`)
        .then(() => {
            location.reload();
        });
}

// حذف السلة بالكامل
function clearCart() {
    fetch(`/clear-cart/`)
        .then(() => {
            location.reload();
        });
}
