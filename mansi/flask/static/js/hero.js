/* ===== SCROLL REVEAL ===== */
const reveals = document.querySelectorAll(".reveal");

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = "1";
            entry.target.style.transform = "translateY(0)";
            entry.target.style.transition = "1s ease";
        }
    });
}, { threshold: 0.2 });

reveals.forEach(el => observer.observe(el));

/* ===== FLOATING SHAPES ===== */
document.addEventListener("mousemove", e => {
    document.querySelector(".sphere").style.transform =
        `translate(${e.clientX * 0.02}px, ${e.clientY * 0.02}px)`;

    document.querySelector(".small-sphere").style.transform =
        `translate(${e.clientX * -0.01}px, ${e.clientY * -0.01}px)`;
});

/* ===== PARTICLES ===== */
const particleContainer = document.getElementById("particles");

for (let i = 0; i < 40; i++) {
    const p = document.createElement("span");
    p.style.left = Math.random() * 100 + "%";
    p.style.top = Math.random() * 100 + "%";
    p.style.animationDuration = 5 + Math.random() * 5 + "s";
    particleContainer.appendChild(p);
}
