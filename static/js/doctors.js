// for MVP page

function getAvailableTimes(start, end, day, date, isToday = false) {
    const times = [];
    let currentTime = new Date(`1970-01-01T${start}:00`);
    const endTime = new Date(`1970-01-01T${end}:00`);
    
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();

    while (currentTime <= endTime) {
        const hour = currentTime.getHours();
        const minutes = currentTime.getMinutes();

        if (isToday) {
            if (hour < currentHour || (hour === currentHour && minutes <= currentMinute)) {
                currentTime.setMinutes(currentTime.getMinutes() + 30);
                continue;
            }
        }

        if (day !== 'Saturday') {
            if (hour === 13 || (hour === 14 && minutes === 0)) {
                currentTime.setMinutes(currentTime.getMinutes() + 30);
                continue;
            }
        }

        if (day === 'Saturday' && hour >= 14) {
            break;
        }

        times.push({
            time: currentTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true}),
            date: date,
            day: day
        });

        currentTime.setMinutes(currentTime.getMinutes() + 30);
    }
    return times;
}





function selectTime(day, date, time, doctor_id) {
    const bookingUrl = `/booking?doctor_id=${doctor_id}&date=${encodeURIComponent(date)}&day=${encodeURIComponent(day)}&time=${encodeURIComponent(time)}`;
    window.location.href = bookingUrl;
}



let offset = 0;

function loadMoreDoctors() {
    const today = new Date();
    const year = today.getFullYear();
    const month = ('0' + (today.getMonth() + 1)).slice(-2);
    const day = ('0' + today.getDate()).slice(-2);
    const currentTime = `${year}-${month}-${day}`;
    document.getElementById("date").value = currentTime;

    // console.log(`today: ${today}\nyear: ${year}\nmonth: ${month}\nday: ${day}\ncurrentTime: ${currentTime}`);
    // console.log(`year: ${year}\nmonth: ${month}\nday: ${day}`);

    fetch(`/api/doctors?offset=${offset}`).then(response => response.json()).then(data => {
        const container = document.getElementById('doctor-container');
        if (data.length === 0) {
            document.getElementById('load-more-btn').style.display = 'none';
            return;
        }

        data.forEach(doctor => {
            const card = document.createElement('div');
            card.className = 'doctor-info';

            const imageUrl = `/static/img/${doctor.image}`;
            const today = new Date();
            const datesToShow = [];

            let availableTimesForDoctor = 0;

            for (let i = 0; i <= 7; i++) {
                const nextDate = new Date(today);
                nextDate.setDate(today.getDate() + i);

                const dayOfWeek = nextDate.toLocaleDateString('en-US', { weekday: 'long' });
                const fullDate = nextDate.toDateString('en-US', { year: 'numeric', month: 'numeric', day: 'numeric' });
                const hours = doctor.operating_hours[dayOfWeek] || {};
                const isToday = i === 0;
                const availableTimes = getAvailableTimes(hours.start, hours.end, dayOfWeek, fullDate, isToday);

                availableTimesForDoctor += availableTimes.length;

                const filteredAvailableTimes = availableTimes.filter(time => {
                    const isBooked = doctor.booked_times.some(booked => 
                        booked.date === fullDate.slice(4) && 
                        booked.time === time.time
                    );
                    return !isBooked;
                });

                datesToShow.push({
                    date: fullDate,
                    day: dayOfWeek,
                    availableTimes: filteredAvailableTimes,
                    isToday: isToday
                });
            }

            // bio 글자 줄이기
            let bioText = '';
            if (availableTimesForDoctor <= 42) {
                bioText = `<p class="doctor-description" style="overflow: hidden; text-overflow: ellipsis; white-space: normal; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 3;">${doctor.bio}</p>`;
            } else {
                bioText = `<p class="doctor-description">${doctor.bio}</p>`;
            }


            const rating = doctor.rating ? `⭐ ${doctor.rating.toFixed(1)}` : "No ratings yet";
            const reviewsHtml = doctor.reviews.map(review => 
                `<p>${review.comment} - ${review.rating}⭐</p>`).join('');

            card.innerHTML = `
                <div class="details">
                    <div class="doctor-profile">
                        <div class="doctor-img">
                            <img src="${imageUrl}" alt="${doctor.first_name} ${doctor.last_name}'s img" class="doctor-img" style="width: 100px; height: 100px;">
                            <div class="rating"><span>★</span>${rating || 'No ratings yet'}</div>
                        </div>
                        <span class="doctor-detail">
                            <h2 class="doctor-tit">Dr. ${doctor.first_name} ${doctor.last_name}</h2>
                            <h3 class="doctor-specialty">Specialty: ${doctor.specialty}</h3>
                            <h4 class="hospital-address">${doctor.hospital_name}</h4>
                            <h5>${doctor.address}</h5>
                            <h5>Preferred Language: ${doctor.preferred_language}</h5>
                            ${bioText}
                            <!-- <div class="reviews">${reviewsHtml}</div> -->
                        </span>
                    </div>
                    <div class="reservation-container">
                        <div class="reservation-tit">
                            <h3>Available Reservations</h3>
                        </div>
                        <div class="reservation-content">
                            ${datesToShow.map(({ day, date, availableTimes }) => {

                                if (availableTimes.length === 0) {
                                    return '';
                                }

                                return `
                                    <span class="reservations">
                                        <h4>${date.slice(4)}</h4>
                                        <p style="margin: .5em 0;">${day}</p>
                                        <select onchange="selectTime('${day}', '${date.slice(4)}', this.value, '${doctor.id}')">
                                            <option value="">Select a time</option>
                                            ${availableTimes.map(time => {
                                                const isBooked = doctor.booked_times.some(booked => 
                                                    booked.date === date.slice(4) && 
                                                    booked.time === time.time
                                                );
                                                const optionClass = isBooked ? 'disabled-time' : '';
                                                return `
                                                    <option value="${time.time}" class="${optionClass}">
                                                        ${time.time}
                                                    </option>
                                                `;
                                            }).join('')}
                                        </select>
                                    </span>
                                `;
                            }).join('')}
                        </div>
                    </div>
                </div>
            `;

            setTimeout(() => {
                card.classList.add('show');
            }, 0);

            container.appendChild(card);
        });
        offset += data.length;

        if (data.length < 3) {
            document.getElementById('load-more-btn').style.display = 'none';
        }
    })
    .catch(error => console.error('Error fetching doctors:', error));
}

window.onload = loadMoreDoctors;

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById('load-more-btn')?.addEventListener('click', loadMoreDoctors);
});