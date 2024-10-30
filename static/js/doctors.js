let offset = 0;  // 초기 offset 설정

function getAvailableTimes(start, end, day) {
    const times = [];
    let currentTime = new Date(`1970-01-01T${start}:00`);
    const endTime = new Date(`1970-01-01T${end}:00`);

    while (currentTime <= endTime) {
        const hour = currentTime.getHours();
        
        if (day === 'Saturday' && (hour === 13 || (hour === 14 && currentTime.getMinutes() === 0))) {
            currentTime.setMinutes(currentTime.getMinutes() + 30);
            continue;
        }

        if (!(hour === 13 || (hour === 14 && currentTime.getMinutes() === 0))) {
            times.push(currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        }
        
        currentTime.setMinutes(currentTime.getMinutes() + 30);
    }

    return times;
}

// 예약 정보를 가지고 예약 페이지로 이동하는 함수
function selectTime(day, time, doctorId) {
    const bookingUrl = `/booking?doctorId=${doctorId}&date=${encodeURIComponent(day)}&time=${encodeURIComponent(time)}`;
    window.location.href = bookingUrl;
}

function loadMoreDoctors() {
    fetch(`/api/doctors?offset=${offset}`)
        .then(response => response.json())
        .then(data => {
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

                for (let i = 1; i <= 3; i++) {
                    const nextDate = new Date(today);
                    nextDate.setDate(today.getDate() + i);
                    const options = { weekday: 'long', year: 'numeric', month: 'numeric', day: 'numeric' };
                    datesToShow.push({
                        date: nextDate.toLocaleDateString('en-US', options),
                        day: nextDate.toLocaleDateString('en-US', { weekday: 'long' }),
                        hours: doctor.operating_hours[nextDate.toLocaleDateString('en-US', { weekday: 'long' })] || {},
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
                                <div class="rating"><span>★</span>${doctor.rating || 'No ratings yet'}</div>
                            </div>
                            <span class="doctor-detail">
                                <h2 class="doctor-tit">Dr. ${doctor.first_name} ${doctor.last_name}</h2>
                                <h3 class="doctor-speciality">Specialty: ${doctor.specialization}</h3>
                                <h4 class="hospital-address">${doctor.hospital_name}</h4>
                                <h5>${doctor.address}</h5>
                                <p class="doctor-description">${doctor.bio}</p>
                                <div class="reviews">${reviewsHtml}</div>
                            </span>
                        </div>
                        <div class="reservation-container">
                            <div class="reservation-tit">
                                <h3>Available Reservations</h3>
                            </div>
                            <div class="reservation-content">
                                ${datesToShow.map(({ day, hours }) => {
                                    const availableTimes = getAvailableTimes(hours.start, hours.end, day);
                                    
                                    if (availableTimes.length === 0) {
                                        // 예약 가능한 시간이 없을 때 아예 해당 날짜 섹션을 숨김
                                        return '';
                                    }

                                    return `
                                        <span class="reservations">
                                            <h4>${day}</h4>
                                            <select onchange="selectTime('${day}', this.value, '${doctor._id}')">
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

                // 카드에 트랜지션 효과 추가
                setTimeout(() => {
                    card.classList.add('show');
                }, 0);

                container.appendChild(card);
            });
            offset += data.length;

            // 버튼을 숨기거나 보이도록 처리
            if (data.length < 3) {
                document.getElementById('load-more-btn').style.display = 'none';
            }
        })
        .catch(error => console.error('Error fetching doctors:', error));
}

window.onload = loadMoreDoctors;

document.getElementById('load-more-btn').addEventListener('click', loadMoreDoctors);
