let offset = 0;

function getAvailableTimes(start, end, day, isToday = false) {
    const times = [];
    let currentTime = new Date(`1970-01-01T${start}:00`);
    const endTime = new Date(`1970-01-01T${end}:00`);
    
    // 현재 시간 가져오기
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();

    while (currentTime <= endTime) {
        const hour = currentTime.getHours();
        const minutes = currentTime.getMinutes();

        // 오늘인 경우 현재 시간 이전의 시간대는 건너뛰기
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

        times.push(currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        
        currentTime.setMinutes(currentTime.getMinutes() + 30);
    }

    return times;
}





function selectTime(day, time, doctor_id) {
    const bookingUrl = `/booking?doctor_id=${doctor_id}&date=${encodeURIComponent(day)}&time=${encodeURIComponent(time)}`;
    window.location.href = bookingUrl;
}





function loadMoreDoctors() {
    const today = new Date();
    const year = today.getFullYear();
    const month = ('0' + (today.getMonth() + 1)).slice(-2);
    const day = ('0' + today.getDate()).slice(-2);
    const currentTime = `${year}-${month}-${day}`;
    document.getElementById("date").value = currentTime;

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

            for (let i = 0; i <= 7; i++) {
                const nextDate = new Date(today);
                nextDate.setDate(today.getDate() + i);
                const dayOfWeek = nextDate.toLocaleDateString('en-US', { weekday: 'long' });
            
                const hours = doctor.operating_hours[dayOfWeek] || {};
                
                const isToday = i === 0;
                
                const displayDay = isToday ? "today" : dayOfWeek;
                
                datesToShow.push({
                    date: nextDate.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'numeric', day: 'numeric' }),
                    day: displayDay,
                    hours: hours,
                    isToday: isToday
                });
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
                            <h3 class="doctor-specialization">Specialty: ${doctor.specialization}</h3>
                            <h4 class="hospital-address">${doctor.hospital_name}</h4>
                            <h5>${doctor.address}</h5>
                            <h5>Preferred Language: ${doctor.preferred_language}</h5>
                            <p class="doctor-description">${doctor.bio}</p>
                            <div class="reviews">${reviewsHtml}</div>
                        </span>
                    </div>
                    <div class="reservation-container">
                        <div class="reservation-tit">
                            <h3>Available Reservations</h3>
                        </div>
                        <div class="reservation-content">
                        ${datesToShow.map(({ day, hours, isToday }) => {
                            const availableTimes = getAvailableTimes(hours.start, hours.end, day, isToday);
                            
                            if (availableTimes.length === 0) {
                                return '';
                            }

                                return `
                                    <span class="reservations">
                                        <h4>${day}</h4>
                                        <select onchange="selectTime('${day}', this.value, '${doctor.id}')">
                                            <option value="">Select a time</option>
                                            ${availableTimes.map(time => `
                                                <option value="${time}">${time}</option>
                                            `).join('')}
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