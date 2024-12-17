const DoctorManager = {
    selectTime: function (day, date, time, doctor_id) {
        if (!time) {
            alert("Please select a valid time.");
            return;
        }

        // redirect to booking URL
        const bookingUrl = `/booking?doctor_id=${doctor_id}&date=${encodeURIComponent(date)}&day=${encodeURIComponent(day)}&time=${encodeURIComponent(time)}`;
        console.log("Redirecting to:", bookingUrl); // 디버깅용 로그
        window.location.href = bookingUrl;
    }
};