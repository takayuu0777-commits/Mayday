document.addEventListener("DOMContentLoaded", async function () {
    const mapContainer = document.getElementById("japan-map-container");
    const dataElement = document.getElementById("prefecture-data");
    const modal = document.getElementById("prefecture-modal");
    const modalPanel = modal
        ? modal.querySelector(".prefecture-modal-panel")
        : null;

    const modalTitle = document.getElementById("prefecture-modal-title");
    const saveMessage = document.getElementById("prefecture-save-message");

    const statusButtons = document.querySelectorAll(
        ".prefecture-status-button"
    );

    if (
        !mapContainer ||
        !dataElement ||
        !modal ||
        !modalPanel
    ) {
        return;
    }

    let prefectures = [];

    try {
        prefectures = JSON.parse(dataElement.textContent);
    } catch (error) {
        mapContainer.innerHTML =
            '<p class="muted">都道府県データを読み込めませんでした。</p>';
        return;
    }

    const prefectureByCode = {};

    let selectedPrefecture = null;
    let selectedMapElement = null;

    prefectures.forEach(function (prefecture) {
        const code = String(prefecture.code).padStart(2, "0");
        prefectureByCode[code] = prefecture;
    });

    function removeStatusClasses(element) {
        element.classList.remove(
            "status-none",
            "status-passed",
            "status-visited",
            "status-stayed",
            "status-lived"
        );
    }

    function setMapStatus(element, status) {
        removeStatusClasses(element);
        element.classList.add("status-" + status);
        element.dataset.status = status;
    }

    function updateSelectedButton(status) {
        statusButtons.forEach(function (button) {
            button.classList.toggle(
                "selected",
                button.dataset.status === status
            );
        });
    }

    function setModalPosition(clientX, clientY) {
        const screenPadding = 12;

        modal.style.setProperty("--popup-x", clientX + "px");
        modal.style.setProperty("--popup-y", clientY + "px");

        requestAnimationFrame(function () {
            const panelRect = modalPanel.getBoundingClientRect();

            let correctedX = clientX;
            let correctedY = clientY + 14;

            const halfWidth = panelRect.width / 2;

            if (correctedX - halfWidth < screenPadding) {
                correctedX = screenPadding + halfWidth;
            }

            if (
                correctedX + halfWidth >
                window.innerWidth - screenPadding
            ) {
                correctedX =
                    window.innerWidth -
                    screenPadding -
                    halfWidth;
            }

            if (
                correctedY + panelRect.height >
                window.innerHeight - screenPadding
            ) {
                correctedY =
                    clientY -
                    panelRect.height -
                    14;
            }

            if (correctedY < screenPadding) {
                correctedY = screenPadding;
            }

            modal.style.setProperty(
                "--popup-x",
                correctedX + "px"
            );

            modal.style.setProperty(
                "--popup-y",
                correctedY + "px"
            );
        });
    }

    function openModal(prefecture, mapElement, event) {
        selectedPrefecture = prefecture;
        selectedMapElement = mapElement;

        modalTitle.textContent = prefecture.name;
        saveMessage.textContent = "";
        saveMessage.classList.remove("success", "error");

        updateSelectedButton(prefecture.status);

        let clientX = window.innerWidth / 2;
        let clientY = window.innerHeight / 2;

        if (
            event &&
            typeof event.clientX === "number" &&
            typeof event.clientY === "number"
        ) {
            clientX = event.clientX;
            clientY = event.clientY;
        } else {
            const elementRect = mapElement.getBoundingClientRect();

            clientX = elementRect.left + elementRect.width / 2;
            clientY = elementRect.top + elementRect.height / 2;
        }

        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");

        setModalPosition(clientX, clientY);
    }

    function closeModal() {
        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");

        selectedPrefecture = null;
        selectedMapElement = null;

        saveMessage.textContent = "";
    }

    function updateListSelect(prefectureName, status) {
        const select = document.querySelector(
            'select[data-prefecture="' + prefectureName + '"]'
        );

        if (select) {
            select.value = status;
        }
    }

    function updateProgress(previousStatus, newStatus) {
        const visitedElement =
            document.getElementById("japan-visited");

        const totalElement =
            document.getElementById("japan-total");

        const percentElement =
            document.getElementById("japan-percent");

        if (
            !visitedElement ||
            !totalElement ||
            !percentElement
        ) {
            return;
        }

        let visited = Number(
            visitedElement.textContent.trim()
        );

        const total = Number(
            totalElement.textContent.trim()
        );

        if (
            previousStatus === "none" &&
            newStatus !== "none"
        ) {
            visited += 1;
        }

        if (
            previousStatus !== "none" &&
            newStatus === "none"
        ) {
            visited -= 1;
        }

        visited = Math.max(
            0,
            Math.min(total, visited)
        );

        const percent = Math.floor(
            (visited / total) * 100
        );

        visitedElement.textContent = String(visited);
        percentElement.textContent = percent + "%";
    }

    async function savePrefectureStatus(status) {
        if (!selectedPrefecture || !selectedMapElement) {
            return;
        }

        const previousStatus = selectedPrefecture.status;

        statusButtons.forEach(function (button) {
            button.disabled = true;
        });

        saveMessage.textContent = "保存しています…";
        saveMessage.classList.remove("success", "error");

        const formData = new FormData();

        formData.append(
            "name",
            selectedPrefecture.name
        );

        formData.append(
            "status",
            status
        );

        try {
            const response = await fetch(
                "/statistics/prefecture/update",
                {
                    method: "POST",
                    body: formData,
                    redirect: "follow"
                }
            );

            if (!response.ok) {
                throw new Error("保存に失敗しました。");
            }

            selectedPrefecture.status = status;

            setMapStatus(
                selectedMapElement,
                status
            );

            updateSelectedButton(status);

            updateListSelect(
                selectedPrefecture.name,
                status
            );

            updateProgress(
                previousStatus,
                status
            );

            saveMessage.textContent = "保存しました ✨";
            saveMessage.classList.add("success");

            setTimeout(function () {
                closeModal();
            }, 450);
        } catch (error) {
            saveMessage.textContent =
                "保存できませんでした。もう一度お試しください。";

            saveMessage.classList.add("error");
        } finally {
            statusButtons.forEach(function (button) {
                button.disabled = false;
            });
        }
    }

    document
        .querySelectorAll("[data-close-modal]")
        .forEach(function (element) {
            element.addEventListener(
                "click",
                closeModal
            );
        });

    statusButtons.forEach(function (button) {
        button.addEventListener(
            "click",
            function () {
                savePrefectureStatus(
                    button.dataset.status
                );
            }
        );
    });

    document.addEventListener(
        "keydown",
        function (event) {
            if (
                event.key === "Escape" &&
                modal.classList.contains("open")
            ) {
                closeModal();
            }
        }
    );

    try {
        const response = await fetch(
            "/static/japan-map-final.svg",
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            throw new Error(
                "日本地図を取得できませんでした。"
            );
        }

        const svgText = await response.text();

        mapContainer.innerHTML = svgText;

        const svg =
            mapContainer.querySelector(
                ".geolonia-svg-map"
            ) ||
            mapContainer.querySelector("svg");

        if (!svg) {
            throw new Error(
                "日本地図SVGが見つかりません。"
            );
        }

        svg.setAttribute("role", "img");
        svg.setAttribute(
            "aria-label",
            "日本制覇マップ"
        );

        const prefectureElements =
            svg.querySelectorAll(
                ".prefecture[data-code]"
            );

        prefectureElements.forEach(
            function (element) {
                const code = String(
                    element.dataset.code
                ).padStart(2, "0");

                const prefecture =
                    prefectureByCode[code];

                if (!prefecture) {
                    return;
                }

                element.classList.add(
                    "prefecture-area"
                );

                setMapStatus(
                    element,
                    prefecture.status
                );

                element.dataset.name =
                    prefecture.name;

                element.setAttribute(
                    "tabindex",
                    "0"
                );

                element.setAttribute(
                    "role",
                    "button"
                );

                element.setAttribute(
                    "aria-label",
                    prefecture.name +
                    "の状態を変更"
                );

                element.addEventListener(
                    "click",
                    function (event) {
                        event.preventDefault();
                        event.stopPropagation();

                        openModal(
                            prefecture,
                            element,
                            event
                        );
                    }
                );

                element.addEventListener(
                    "keydown",
                    function (event) {
                        if (
                            event.key === "Enter" ||
                            event.key === " "
                        ) {
                            event.preventDefault();

                            openModal(
                                prefecture,
                                element,
                                null
                            );
                        }
                    }
                );
            }
        );
    } catch (error) {
        mapContainer.innerHTML =
            '<p class="muted">日本地図を表示できませんでした。ページを再読み込みしてください。</p>';
    }
});