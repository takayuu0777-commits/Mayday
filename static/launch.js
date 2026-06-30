document.addEventListener("DOMContentLoaded", () => {
    const launch = document.getElementById("launch-screen");

    if (!launch) {
        return;
    }

    launch.style.display = "flex";

    launch.addEventListener("click", () => {
        launch.classList.add("launch-enter");

        setTimeout(() => {
            launch.style.display = "none";
        }, 500);
    });
});