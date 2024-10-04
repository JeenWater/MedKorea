const doctors = [
    {
        name: 'Doctor Name',
        description: 'Doctor Speciality',
        rating: '5/5',
        image: './img/imgMain.png',
        availableDates: {
            'October 1': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 2': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 3': ['10:00 AM', '11:00 AM', '1:00 PM'],
        }
    },
    {
        name: 'Doctor Name',
        description: 'Doctor Speciality',
        rating: '5/5',
        image: './img/imgMain.png',
        availableDates: {
            'October 1': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 2': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 3': ['10:00 AM', '11:00 AM', '1:00 PM'],
        }
    },
    {
        name: 'Doctor Name',
        description: 'Doctor Speciality',
        rating: '5/5',
        image: './img/imgMain.png',
        availableDates: {
            'October 1': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 2': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 3': ['10:00 AM', '11:00 AM', '1:00 PM'],
        }
    },
    {
        name: 'Doctor Name',
        description: 'Doctor Speciality',
        rating: '5/5',
        image: './img/imgMain.png',
        availableDates: {
            'October 1': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 2': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 3': ['10:00 AM', '11:00 AM', '1:00 PM'],
        }
    },
    {
        name: 'Doctor Name',
        description: 'Doctor Speciality',
        rating: '5/5',
        image: './img/imgMain.png',
        availableDates: {
            'October 1': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 2': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 3': ['10:00 AM', '11:00 AM', '1:00 PM'],
        }
    },
    {
        name: 'Doctor Name',
        description: 'Doctor Speciality',
        rating: '5/5',
        image: './img/imgMain.png',
        availableDates: {
            'October 1': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 2': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 3': ['10:00 AM', '11:00 AM', '1:00 PM'],
        }
    },
    {
        name: 'Doctor Name',
        description: 'Doctor Speciality',
        rating: '5/5',
        image: './img/imgMain.png',
        availableDates: {
            'October 1': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 2': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 3': ['10:00 AM', '11:00 AM', '1:00 PM'],
        }
    },
    {
        name: 'Doctor Name',
        description: 'Doctor Speciality',
        rating: '5/5',
        image: './img/imgMain.png',
        availableDates: {
            'October 1': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 2': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 3': ['10:00 AM', '11:00 AM', '1:00 PM'],
        }
    },
    {
        name: 'Doctor Name',
        description: 'Doctor Speciality',
        rating: '5/5',
        image: './img/imgMain.png',
        availableDates: {
            'October 1': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 2': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 3': ['10:00 AM', '11:00 AM', '1:00 PM'],
        }
    },
    {
        name: 'Doctor Name',
        description: 'Doctor Speciality',
        rating: '5/5',
        image: './img/imgMain.png',
        availableDates: {
            'October 1': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 2': ['10:00 AM', '11:00 AM', '1:00 PM'],
            'October 3': ['10:00 AM', '11:00 AM', '1:00 PM'],
        }
    },
    // You can add more doctors here
];

let visibleDoctors = 0;
const doctorsPerPage = 3;

document.addEventListener("DOMContentLoaded", function() {
    loadMore();
});

function loadMore() {
    const container = document.getElementById('doctor-container');
    const nextDoctors = doctors.slice(visibleDoctors, visibleDoctors + doctorsPerPage);

    nextDoctors.forEach((doctor) => {
        const doctorArticle = document.createElement('article');
        doctorArticle.className = 'doctor-info';
        doctorArticle.style.opacity = 0;
        doctorArticle.innerHTML = `
            <div class="details">
                <div class="doctor-profile">
                    <div class="doctor-img">
                        <img src="${doctor.image}" alt="${doctor.name}'s Photo" class="doctor-photo" style="width: 100px; height: 100px;">
                        <div class="rating"><span>★</span>${doctor.rating}</div>
                    </div>
                    <span class="doctor-detail">
                        <h2 class="doctor-tit">${doctor.name}</h2>
                        <h3 class="doctor-subtit">${doctor.description}</h3>
                        <p>Doctor Description${visibleDoctors+1}</p>
                    </span>
                </div>
                <div class="reservation-container">
                    <div class="reservation-tit">
                        <h3>Available Reservations</h3>
                    </div>
                    <div class="reservation-content">
                        ${Object.keys(doctor.availableDates).map(date => `
                            <span class="reservations">
                                <h4>${date}</h4>
                                <ul>
                                    ${doctor.availableDates[date].map(time => `
                                        <li><a href="#" onclick="selectTime('${date}', '${time}')">${time}</a></li>
                                    `).join('')}
                                </ul>
                            </span>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        container.appendChild(doctorArticle);

        requestAnimationFrame(() => {
            doctorArticle.style.transition = "opacity 1s ease-in-out"; // 트랜지션 설정
            doctorArticle.style.opacity = 1; // 점차적으로 나타나도록 변경
        });
    });

    visibleDoctors += doctorsPerPage;

    if (visibleDoctors >= doctors.length) {
        document.getElementById('load-more-btn').style.display = 'none';
    }
}