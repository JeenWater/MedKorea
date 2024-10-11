let is_logged_in = true

function selectTime(date, time) {
    const formattedTime = encodeURIComponent(time);
    if (is_logged_in) {
        window.location.href = `/book_loggedin`;
        // window.location.href = `/booking?date=${date}&time=${formattedTime}`;
    } else {
        window.location.href = `/login`;
    }
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