// For modals
class BaseModal {
    constructor(modalId) {
        this.modal = document.getElementById(modalId);
        this.closeButton = this.modal.querySelector('.close-btn');
        this.initListeners();
    }

    initListeners() {
        // close modal when clicking close button
        if (this.closeButton){
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





class EditModal extends BaseModal {
    constructor(modalId, formId) {
        super(modalId);
        this.form = document.getElementById(formId);
        this.newDateInput = this.form.querySelector('#newDate');
        this.newTimeSelect = this.form.querySelector('#newTime');
        this.doctorId = null;
        this.appointmentId = null;

        this.form.addEventListener('submit', (event) => this.submitForm(event));
    }

    open(date, time, day, appointmentId) {
        super.open();
        this.newDateInput.value = date;
        this.appointmentId = appointmentId;
        this.fetchAvailableTimes(date, appointmentId, time, day);
    }

    fetchAvailableTimes(date, appointmentId, selectedTime, day) {
        fetch(`myappointments/edit?doctor_id=${appointmentId}&date=${date}&day=${day}`)
            .then(response => response.json())
            .then(times => {
                this.newTimeSelect.innerHTML = `<option value="">Select a time</option>`;
                times.forEach(time => {
                    const option = document.createElement('option');
                    option.value = time;
                    option.textContent = time;
                    if (time === selectedTime) {
                        option.selected = true;
                    }
                    this.newTimeSelect.appendChild(option);
                });
            })
            .catch(err => console.error('Error fetching times:', err));
    }

    submitForm(event) {
        event.preventDefault();
        const newDate = this.newDateInput.value;
        const newTime = this.newTimeSelect.value;

        if (!newDate || !newTime) {
            alert('Please select a new date and time.');
            return;
        }

        // Prevent date and time conflicts with existing appointments
        fetch('/myappointments/check-availability', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                doctor_id: this.doctorId,
                date: newDate,
                time: newTime,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Proceed to update appointment
                this.updateAppointment(newDate, newTime);
            } else {
                alert('The selected time is already booked. Please choose a different time.');
            }
        })
        .catch(err => console.error('Error checking availability:', err));
    }

    updateAppointment(newDate, newTime) {
        fetch('/myappointments/edit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                doctor_id: this.doctorId,
                appointment_id: this.appointmentId,
                new_date: newDate,
                new_time: newTime,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Reservation updated successfully!');
                this.close();
                location.reload();
            } else {
                alert('Failed to update reservation: ' + data.message);
            }
        })
        .catch(err => console.error('Error updating reservation:', err));
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
        preventDefault();
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
                        alert('Appointment canceled successfully!');
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
    const editModal = new EditModal('editModal', 'editAppointmentForm');
    const cancelModal = new CancelModal('cancelModal');

    // open edit modal
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', () => {
            const date = button.getAttribute('date');
            const time = button.getAttribute('time');
            const day = button.getAttribute('day');
            const appointmentId = button.getAttribute('data-id');
            editModal.open(date, time, day, appointmentId);
        });
    });

    // Open cancel modal
    document.querySelectorAll('.cancel-btn').forEach(button => {
        button.addEventListener('click', () => {
            const appointmentId = button.getAttribute('data-id');
            cancelModal.open(appointmentId);
        });
    });
});
