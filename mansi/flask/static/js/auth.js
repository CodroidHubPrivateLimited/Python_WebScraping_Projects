document.addEventListener("DOMContentLoaded", () => {

    /* ================= EYE TOGGLE ================= */
    document.querySelectorAll(".toggle-password").forEach(icon => {
        icon.addEventListener("click", () => {
            const targetId = icon.getAttribute("data-target");
            const input = document.getElementById(targetId);

            if (!input) return;

            if (input.type === "password") {
                input.type = "text";
                icon.textContent = "🙈";
            } else {
                input.type = "password";
                icon.textContent = "👁";
            }
        });
    });

    /* ================= POPUP CLOSE ================= */
    const popupBtn = document.querySelector("#errorPopup button");
    if (popupBtn) {
        popupBtn.addEventListener("click", () => {
            document.getElementById("errorPopup").style.display = "none";
        });
    }

});
