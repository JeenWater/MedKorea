document.querySelectorAll('.cancel-btn').forEach(button => {
    button.addEventListener('click', () => {
        const appointmentId = button.getAttribute('data-appointment-id');
        document.getElementById('confirmCancelBtn').onclick = () => cancelAppointment(appointmentId);
        document.getElementById('cancelModal').style.display = 'block';
    });
});

function cancelAppointment(appointmentId) {
    const cancelReason = document.getElementById('cancel_reason').value;
    
    fetch('/cancel_appointment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ appointment_id: appointmentId, cancel_reason: cancelReason })
    }).then(response => response.json()).then(data => {
        if (data.success) {
            alert("Appointment cancelled successfully.");
            location.reload();
        } else {
            alert("Error cancelling appointment.");
        }
    });
}