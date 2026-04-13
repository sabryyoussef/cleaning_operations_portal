/** Portal FSM: optional browser geolocation before POST (Start Visit + photo uploads). */
function fsmPortalAttachGeoOnSubmit(form, latSel, lonSel, accSel) {
    if (!form) {
        return;
    }
    form.addEventListener("submit", (ev) => {
        if (form.dataset.fsmGeoDone === "1") {
            return;
        }
        ev.preventDefault();
        const latInput = form.querySelector(latSel);
        const lonInput = form.querySelector(lonSel);
        const accInput = form.querySelector(accSel);
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
}

document.addEventListener("DOMContentLoaded", () => {
    fsmPortalAttachGeoOnSubmit(
        document.getElementById("o_fsm_portal_start_visit_form"),
        'input[name="fsm_portal_start_geo_lat"]',
        'input[name="fsm_portal_start_geo_lon"]',
        'input[name="fsm_portal_start_geo_accuracy"]'
    );
    fsmPortalAttachGeoOnSubmit(
        document.getElementById("o_fsm_portal_photo_before_form"),
        'input[name="fsm_portal_photo_before_geo_lat"]',
        'input[name="fsm_portal_photo_before_geo_lon"]',
        'input[name="fsm_portal_photo_before_geo_accuracy"]'
    );
    fsmPortalAttachGeoOnSubmit(
        document.getElementById("o_fsm_portal_photo_after_form"),
        'input[name="fsm_portal_photo_after_geo_lat"]',
        'input[name="fsm_portal_photo_after_geo_lon"]',
        'input[name="fsm_portal_photo_after_geo_accuracy"]'
    );
});
