document.addEventListener("DOMContentLoaded", function () {
    const launch = document.getElementById("launch-screen");

    if (!launch) {
        return;
    }

    launch.classList.remove("launch-enter");
    launch.style.display = "flex";
    launch.style.opacity = "1";

    launch.addEventListener("click", function () {
        launch.classList.add("launch-enter");

        setTimeout(function () {
            launch.style.display = "none";
        }, 600);
    });
});