function selectTime(date, time) {
    const formattedTime = encodeURIComponent(time);
    const formattedDate = encodeURIComponent(date);
    const bookingUrl = `/booking?date=${formattedDate}&time=${formattedTime}`;
    
    fetch('/check_login')
        .then(response => {
            if (!response.ok) {
                throw new Error('서버 응답 오류');
            }
            return response.json();
        })
        .then(data => {
            if (!data.is_logged_in) {
                // 로그인되지 않은 경우
                window.location.href = `/auth/login?next=${encodeURIComponent(bookingUrl)}`;
                return;
            }

            if (data.user_type === 'patient') {
                // 환자인 경우 예약 페이지로 이동
                window.location.href = bookingUrl;
            } else if (data.user_type === 'doctor') {
                // 의사인 경우 에러 메시지
                alert('의사는 예약할 수 없습니다. 환자 계정으로 로그인해주세요.');
                window.location.href = '/auth/login';
            } else {
                // 그 외의 경우
                alert('예약을 위해서는 환자로 등록되어야 합니다.');
                window.location.href = '/auth/login';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('오류가 발생했습니다. 다시 시도해주세요.');
            window.location.href = `/search`;
        });
}

function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

window.onload = function () {
    const date = getQueryParam("date");
    let time = getQueryParam("time");

    if (date && time) {
        time = parseInt(time);

        if (time >= 24) {
            time -= 24;
        }

        if (time === 0) {
            document.getElementById("time").textContent = "12:00 AM";
            document.getElementById("appointment-date").textContent = date;
        }

        else if (time < 12) {
            time = time.toString().padStart(2, '0') + ":00";
            document.getElementById("time").textContent = `${time} AM`;
            document.getElementById("appointment-date").textContent = date;
        }

        else if (time === 12) {
            document.getElementById("time").textContent = "12:00 PM";
            document.getElementById("appointment-date").textContent = date;
        }

        else {
            time = (time - 12).toString().padStart(2, '0') + ":00";
            document.getElementById("time").textContent = `${time} PM`;
            document.getElementById("appointment-date").textContent = date;
        }
    }
}