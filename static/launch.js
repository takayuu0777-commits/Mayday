document.addEventListener("DOMContentLoaded", function () {
    const launch = document.getElementById("launch-screen");

    if (!launch) {
        return;
    }

    const launchDone = sessionStorage.getItem("secondBrainLaunchDone");

    if (launchDone === "yes") {
        launch.style.display = "none";
        launch.style.opacity = "0";
        return;
    }

    sessionStorage.setItem("secondBrainLaunchDone", "yes");

    launch.style.display = "flex";
    launch.style.opacity = "1";
    launch.classList.remove("launch-enter");

    setTimeout(function () {
        launch.classList.add("launch-ready");
    }, 100);

    launch.addEventListener("click", function () {
        launch.classList.add("launch-enter");

        setTimeout(function () {
            launch.style.display = "none";
        }, 700);
    });
});