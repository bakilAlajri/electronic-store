document.addEventListener("DOMContentLoaded", () => {
    const addButton = document.getElementById("add-to-cart-btn");

    if (addButton) {
        addButton.addEventListener("click", function () {
            const productId = this.dataset.product;
            addToCart(productId);
        });
    }
});
