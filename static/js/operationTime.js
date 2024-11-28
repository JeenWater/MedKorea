// For MVP time
document.addEventListener('DOMContentLoaded', function() {
    const operatingHoursHidden = document.getElementById('operating-hours-hidden');
    if (operatingHoursHidden) {
        const operatingHoursValue = operatingHoursHidden.value;

        if (operatingHoursValue) {
            try {
                const operatingHours = JSON.parse(operatingHoursValue.trim());

                Object.keys(operatingHours).forEach(day => {
                    const checkbox = document.getElementById(`${day}-check`);
                    const timeInputs = document.getElementById(`${day}-times`);
                    const startInput = timeInputs.querySelector('.start-time');
                    const endInput = timeInputs.querySelector('.end-time');

                    if (checkbox) {
                        checkbox.checked = true;
                        timeInputs.style.display = 'block';
                        startInput.value = operatingHours[day].start;
                        endInput.value = operatingHours[day].end;
                    }
                });
            } catch (error) {
                console.error('Failed to parse operating hours:', error);
            }
        }
    }

    const dayCheckboxes = document.querySelectorAll('.day-checkbox');
    if (dayCheckboxes.length > 0) {
        dayCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const dayTimes = document.getElementById(`${this.value}-times`);
                if (this.checked) {
                    dayTimes.style.display = 'block';
                } else {
                    dayTimes.style.display = 'none';
                    dayTimes.querySelector('.start-time').value = '';
                    dayTimes.querySelector('.end-time').value = '';
                }
            });
        });
    }

    const form = document.getElementById('signup-form');
    if (form && operatingHoursHidden) {
        form.addEventListener('submit', function(e) {
            const operatingHours = {};

            document.querySelectorAll('.day-checkbox').forEach(checkbox => {
                if (checkbox.checked) {
                    const day = checkbox.value;
                    const startTime = document.getElementById(`${day}-start`).value;
                    const endTime = document.getElementById(`${day}-end`).value;

                    if (startTime && endTime) {
                        operatingHours[day] = {
                            start: startTime,
                            end: endTime
                        };
                    }
                }
            });

            console.log('Operating Hours:', operatingHours);
            operatingHoursHidden.value = JSON.stringify(operatingHours);
        });
    }
});