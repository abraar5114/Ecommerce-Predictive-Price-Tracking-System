// =============================================
// ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
// JavaScript File
// =============================================

// --- Show Loading When Search Button Clicked ---
document.addEventListener("DOMContentLoaded", function() {

    const form = document.querySelector("form");
    const button = document.querySelector("button[type='submit']");

    if (form && button) {
        form.addEventListener("submit", function() {
            button.textContent = "🔍 Searching... Please wait!";
            button.disabled = true;
            button.style.backgroundColor = "#666";
        });
    }

    // --- Auto hide success/error messages after 5 seconds ---
    const messages = document.querySelectorAll(".error, .success");
    messages.forEach(function(msg) {
        setTimeout(function() {
            msg.style.display = "none";
        }, 5000);
    });

    // --- Highlight best deal row ---
    const bestDeal = document.querySelector(".best-deal");
    if (bestDeal) {
        bestDeal.scrollIntoView({ behavior: "smooth", block: "center" });
    }

});