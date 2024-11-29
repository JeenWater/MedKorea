// For cancel on myappointments
document.querySelectorAll(".cancel-btn").forEach(button => {
    button.addEventListener("click", () => {
        const appointmentId = button.getAttribute("data-id");
        
        // open the modal
        const cancelModal = document.getElementById("cancelModal");
        const cancelReasonInput = document.getElementById("cancelReason");
        const confirmCancelBtn = document.getElementById("confirmCancel");
        const errorText = document.getElementById("errorText"); // error message

        // clear any previous input or error
        cancelReasonInput.value = '';
        errorText.textContent = '';
        cancelModal.style.display = "block";

        // close the modal when the close button is clicked
        document.getElementById("closeModal").addEventListener("click", () => {
            cancelModal.style.display = "none";
        });

        // close modal when clicking outside
        window.onclick = (event) => {
            if (event.target === cancelModal) {
                cancelModal.style.display = "none";
            }
        };

        // remove previous event listener to avoid duplication
        confirmCancelBtn.replaceWith(confirmCancelBtn.cloneNode(true));
        const newConfirmCancelBtn = document.getElementById("confirmCancel");
        newConfirmCancelBtn.addEventListener("click", () => {
            const cancelReason = cancelReasonInput.value.trim();

            if (cancelReason) {
                fetch("/myappointments/cancel", {
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
                })
                .catch(error => console.error("Error:", error));

                // close the modal after submission
                cancelModal.style.display = "none";
            } else {
                // display error message
                errorText.textContent = "Please provide a reason for cancellation.";
                errorText.style.color = "red";
            }
        });
    });
});