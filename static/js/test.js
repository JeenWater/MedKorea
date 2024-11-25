document.addEventListener("DOMContentLoaded", function () {
    const userInfoList = document.getElementById("user-info-list");

    function loadUserInfo() {
        fetch("/api/user-info")
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Failed to load user info");
                }
                return response.json();
            })
            .then((data) => {
                if (data.error) {
                    userInfoList.innerHTML = `<p>${data.error}</p>`;
                    return;
                }

                // 유저 타입에 따라 렌더링
                if (data.user_type === "patient") {
                    renderPatientInfo(data.data);
                } else if (data.user_type === "doctor") {
                    renderDoctorInfo(data.data);
                }
            })
            .catch((error) => {
                console.error(error);
                userInfoList.innerHTML =
                    "<p>Failed to load user information. Please try again later.</p>";
            });
    }

    function renderPatientInfo(appointments) {
        userInfoList.innerHTML = "";
        appointments.forEach((a) => {
            const card = document.createElement("div");
            card.classList.add("user-info-card");

            card.innerHTML = `
                    <img src="${a.doctor_image || '/static/img/default-doctor.png'}" alt="Doctor Image">
                    <h3>Dr. ${a.doctor_name}</h3>
                    <p>Specialization: ${a.specialization}</p>
                    <p>Hospital: ${a.hospital_name}</p>
                    <p>Address: ${a.address}</p>
                    <p>Appointment: ${a.date} at ${a.time}</p>
                    <p>Status: ${a.status}</p>
                `;
            userInfoList.appendChild(card);
        });
    }

    function renderDoctorInfo(appointments) {
        userInfoList.innerHTML = "";
        appointments.forEach((a) => {
            const card = document.createElement("div");
            card.classList.add("user-info-card");

            card.innerHTML = `
                    <h3>Patient: ${a.patient_name}</h3>
                    <p>Phone: ${a.phone}</p>
                    <p>Birth Date: ${a.birth}</p>
                    <p>Gender: ${a.sex}</p>
                    <p>Appointment: ${a.date} at ${a.time}</p>
                    <p>Status: ${a.status}</p>
                `;
            userInfoList.appendChild(card);
        });
    }

    // 데이터 로드
    loadUserInfo();
});
