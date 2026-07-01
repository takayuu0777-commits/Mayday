document.addEventListener("DOMContentLoaded", function () {
    const launch = document.getElementById("launch-screen");

    if (!launch) {
        return;
    }

    const alreadyOpened = sessionStorage.getItem("secondBrainLaunchDone");

    if (alreadyOpened) {
        launch.style.display = "none";
        return;
    }

    launch.classList.remove("launch-enter");
    launch.style.display = "flex";
    launch.style.opacity = "1";

    setTimeout(function () {
        launch.classList.add("launch-ready");
    }, 100);

    launch.addEventListener("click", function () {
        sessionStorage.setItem("secondBrainLaunchDone", "1");

        launch.classList.add("launch-enter");

        setTimeout(function () {
            launch.style.display = "none";
        }, 700);
    });
});