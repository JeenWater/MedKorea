// For modals
class BaseModal {
    constructor(modalId) {
        this.modal = document.getElementById(modalId);
        if (!this.modal) {
            console.error(`Modal with ID "${modalId}" not found.`);
            return; // Exit the constructor if modal is not found
        }
        this.closeButton = this.modal.querySelector('.close-btn');
        this.initListeners();
    }
    initListeners() {
        // close modal when clicking close button
        if (this.closeButton) {
            this.closeButton.addEventListener('click', () => this.close());
        }
        // close modal when clicking outside the modal content
        window.addEventListener('click', (event) => {
            if (event.target === this.modal) {
                this.close();
            }
        });
    }
    open() {
        this.modal.style.display = 'block';
    }
    close() {
        this.modal.style.display = 'none';
    }
}





// Booking modal
class BookingModal extends BaseModal {
    constructor(modalId) {
        super(modalId);
        this.confirmButton = this.modal.querySelector('#confirmBooking');

        this.confirmButton.addEventListener('click', () => this.submitBooking());
    }

    open() {
        super.open();
    }

    submitBooking() {
        const bookingForm = document.getElementById("booking-form");
        bookingForm.submit();
        this.close();
    }
}





class CancelModal extends BaseModal {
    constructor(modalId) {
        super(modalId);
        this.reasonInput = this.modal.querySelector('#cancelReason');
        this.errorText = this.modal.querySelector('#errorText');
        this.confirmButton = this.modal.querySelector('#confirmCancel');
        this.appointmentId = null;

        this.confirmButton.addEventListener('click', () => this.submitCancel());
    }

    open(appointmentId) {
        super.open();
        this.appointmentId = appointmentId;
        this.reasonInput.value = '';
        this.errorText.textContent = '';
    }

    submitCancel() {
        const cancelReason = this.reasonInput.value.trim();

        if (cancelReason) {
            fetch('/myappointments/cancel', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    appointment_id: this.appointmentId,
                    cancel_reason: cancelReason,
                }),
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    if (data.success) {
                        this.close();
                        location.reload();
                    } else {
                        alert('Failed to cancel appointment: ' + data.message);
                    }
                })
                .catch(error => console.error('Error:', error));
        } else {
            this.errorText.textContent = 'Please provide a reason for cancellation.';
            this.errorText.style.color = 'red';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const bookButton = document.querySelectorAll('.book-btn');
    bookButton.forEach(btn => {
        btn.addEventListener('click', () => {
            // For booking modal
            const bookingModal = new BookingModal('myModal');
            bookingModal.open();
        });
    });

    const cancelButtons = document.querySelectorAll('.cancel-btn');
    cancelButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const appointmentId = btn.getAttribute('data-id');
            // For cancel modal
            const cancelModal = new CancelModal('cancelModal');
            cancelModal.open(appointmentId);
        });
    });
});