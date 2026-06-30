document.addEventListener("DOMContentLoaded", () => {
    const launch = document.getElementById("launch-screen");

    if (!launch) {
        return;
    }

    const alreadySeen = sessionStorage.getItem("secondBrainLaunchSeen");

    if (alreadySeen) {
        launch.style.display = "none";
        return;
    }

    setTimeout(() => {
        launch.classList.add("ready");
    }, 2600);

    launch.addEventListener("click", () => {
        sessionStorage.setItem("secondBrainLaunchSeen", "true");
        launch.classList.add("hide");

        setTimeout(() => {
            launch.style.display = "none";
        }, 900);
    });
});