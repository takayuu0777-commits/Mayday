document.addEventListener("DOMContentLoaded", () => {
    const launch = document.getElementById("launch-screen");

    if (!launch) return;

    const alreadyPlayed = sessionStorage.getItem("launchPlayed");

    if (alreadyPlayed) {
        launch.style.display = "none";
        return;
    }

    launch.addEventListener("click", () => {
        launch.classList.add("launch-enter");

        sessionStorage.setItem("launchPlayed", "1");

        setTimeout(() => {
            launch.style.display = "none";
        }, 1200);
    });
});