document.addEventListener("DOMContentLoaded", function () {
    const cancelButtons = document.querySelectorAll(".cancel-btn");
    const modal = document.getElementById("cancelModal");
    const closeModal = document.getElementById("closeModal");
    const confirmCancel = document.getElementById("confirmCancel");
    const cancelReason = document.getElementById("cancelReason");
    let currentAppointmentId = null;

    // Show modal on cancel button click
    cancelButtons.forEach((btn) => {
        btn.addEventListener("click", (event) => {
            currentAppointmentId = event.target.getAttribute("data-id");
            modal.style.display = "block";
        });
    });

    // Close modal
    closeModal.addEventListener("click", () => {
        modal.style.display = "none";
        cancelReason.value = ""; // Clear reason field
    });

    // Confirm cancellation
    confirmCancel.addEventListener("click", () => {
        const reason = cancelReason.value.trim();
        if (!reason) {
            return;
        }

        fetch(`/myappointments/${currentAppointmentId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reason }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    location.reload();
                }
            });
    });
});