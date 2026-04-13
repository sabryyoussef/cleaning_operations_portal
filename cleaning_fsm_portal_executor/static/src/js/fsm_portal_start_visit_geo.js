/** Portal Start Visit: optional browser geolocation before POST (resilience-first). */
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("o_fsm_portal_start_visit_form");
    if (!form) {
        return;
    }
    form.addEventListener("submit", (ev) => {
        if (form.dataset.fsmGeoDone === "1") {
            return;
        }
        ev.preventDefault();
        const latInput = form.querySelector('input[name="fsm_portal_start_geo_lat"]');
        const lonInput = form.querySelector('input[name="fsm_portal_start_geo_lon"]');
        const accInput = form.querySelector('input[name="fsm_portal_start_geo_accuracy"]');
        if (!latInput || !lonInput || !accInput) {
            form.dataset.fsmGeoDone = "1";
            form.submit();
            return;
        }
        if (!navigator.geolocation) {
            form.dataset.fsmGeoDone = "1";
            form.submit();
            return;
        }
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                latInput.value = String(pos.coords.latitude);
                lonInput.value = String(pos.coords.longitude);
                if (pos.coords.accuracy != null && !Number.isNaN(pos.coords.accuracy)) {
                    accInput.value = String(pos.coords.accuracy);
                }
                form.dataset.fsmGeoDone = "1";
                form.submit();
            },
            () => {
                form.dataset.fsmGeoDone = "1";
                form.submit();
            },
            { enableHighAccuracy: false, timeout: 12000, maximumAge: 0 }
        );
    });
});
