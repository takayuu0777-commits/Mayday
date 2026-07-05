document.addEventListener("DOMContentLoaded", function () {
    const launch = document.getElementById("launch-screen");

    if (!launch) {
        return;
    }

    const launchDone = sessionStorage.getItem("secondBrainLaunchDone");

    if (launchDone === "yes") {
        launch.remove();
        return;
    }

    launch.style.display = "flex";
    launch.style.opacity = "1";
    launch.classList.remove("launch-enter");

    setTimeout(function () {
        launch.classList.add("launch-ready");
    }, 100);

    launch.addEventListener("click", function () {
        sessionStorage.setItem("secondBrainLaunchDone", "yes");
        launch.classList.add("launch-enter");

        setTimeout(function () {
            launch.remove();
        }, 700);
    });
});