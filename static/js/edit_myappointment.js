// // open and close modal logic
// const modal = document.getElementById("reservationModal");
// const closeModal = document.getElementById("closeModal");

// function openModal(date, time, doctorId) {
//     modal.style.display = "block";

//     // prepopulate date and times
//     document.getElementById("newDate").value = date;
//     const newTimeSelect = document.getElementById("newTime");
//     newTimeSelect.innerHTML = `<option value="">Select a time</option>`;
    
//     // fetch available times for the selected date
//     fetch(`/api/available-times?doctor_id=${doctorId}&date=${date}`)
//         .then(response => response.json())
//         .then(times => {
//             times.forEach(time => {
//                 const option = document.createElement('option');
//                 option.value = time;
//                 option.textContent = time;
//                 if (time === time) {
//                     // pre-select the current time
//                     option.selected = true;
//                 }
//                 newTimeSelect.appendChild(option);
//             });
//         });
// }

// // Close modal
// closeModal.onclick = () => modal.style.display = "none";

// // Close modal when clicking outside
// window.onclick = (event) => {
//     if (event.target === modal) {
//         modal.style.display = "none";
//     }
// };

// function addEditButtons() {
//     document.querySelectorAll('.edit-reservation-btn').forEach(button => {
//         button.addEventListener('click', (event) => {
//             const date = button.getAttribute('data-date');
//             const time = button.getAttribute('data-time');
//             const doctorId = button.getAttribute('data-doctor-id');
//             openModal(date, time, doctorId);
//         });
//     });
// }

// document.getElementById("reservationForm").addEventListener("submit", (event) => {
//     event.preventDefault();

//     const doctorId = ...; // 가져올 방법 설정
//     const newDate = document.getElementById("newDate").value;
//     const newTime = document.getElementById("newTime").value;

//     fetch(`/api/update-reservation`, {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//             doctor_id: doctorId,
//             new_date: newDate,
//             new_time: newTime,
//         }),
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 alert("Reservation updated successfully!");
//                 modal.style.display = "none";
//                 location.reload(); // reload for the info
//             } else {
//                 alert("Failed to update reservation. Please try again.");
//             }
//         })
//         .catch(err => console.error("Error:", err));
// });