document.querySelectorAll(".cancel-btn").forEach(button => {
    button.addEventListener("click", () => {
        const appointmentId = button.getAttribute("data-id");
        console.log(appointmentId)
        
        // Open the modal
        const cancelModal = document.getElementById("cancelModal");
        const cancelReasonInput = document.getElementById("cancelReason");
        
        // Clear any previous input
        cancelReasonInput.value = '';

        cancelModal.style.display = "block";

        // Close the modal when the close button is clicked
        document.getElementById("closeModal").addEventListener("click", () => {
            cancelModal.style.display = "none";
        });

        document.getElementById("confirmCancel").addEventListener("click", () => {
            const cancelReason = cancelReasonInput.value;

            if (cancelReason) {
                fetch("/myappointment/" + appointmentId, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        appointment_id: appointmentId,
                        cancel_reason: cancelReason
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("Appointment canceled successfully!");
                        location.reload();
                    } else {
                        alert("Failed to cancel appointment: " + data.message);
                    }
                });

                // Close the modal after submission
                cancelModal.style.display = "none";
            } else {
                alert("Please provide a reason for cancellation.");
            }
        });
    });
});