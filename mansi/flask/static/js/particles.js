const particleContainer = document.querySelector(".particles");

if (particleContainer) {
    for (let i = 0; i < 40; i++) {
        const span = document.createElement("span");

        const size = Math.random() * 6 + 3;
        span.style.width = `${size}px`;
        span.style.height = `${size}px`;

        span.style.left = Math.random() * 100 + "%";
        span.style.animationDuration = Math.random() * 10 + 8 + "s";
        span.style.animationDelay = Math.random() * 10 + "s";
        span.style.opacity = Math.random();

        particleContainer.appendChild(span);
    }
}
