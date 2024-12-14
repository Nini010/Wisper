document.addEventListener('DOMContentLoaded', () => {
    document.getElementById("emoji-toggle").addEventListener("click", function (e) {
        const panel = document.getElementById("emoji-panel");
        panel.style.display = panel.style.display === "block" ? "none" : "block";
        e.stopPropagation();
    });

    document.getElementById("emoji-panel").addEventListener("click", function (e) {
        if (e.target.tagName === "SPAN") {
            const input = document.querySelector(".messages");
            input.value += e.target.textContent;
            e.stopPropagation();
        }
    });

    document.addEventListener("click", function (e) {
        const panel = document.getElementById("emoji-panel");
        const toggle = document.getElementById("emoji-toggle");
        if (!panel.contains(e.target) && e.target !== toggle) {
            panel.style.display = "none";
        }
    });
});