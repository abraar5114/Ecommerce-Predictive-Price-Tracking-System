// =============================================
// ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
// =============================================

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const button = document.querySelector("button[type='submit']");

    if (form && button) {
        form.addEventListener("submit", function () {
            button.textContent = "🔍 Checking product... please wait";
            button.disabled = true;
            button.style.opacity = "0.6";
        });
    }

    const messages = document.querySelectorAll(".error, .success");
    messages.forEach(function (msg) {
        setTimeout(function () {
            msg.style.display = "none";
        }, 6000);
    });
});