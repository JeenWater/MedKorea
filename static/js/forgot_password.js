document.addEventListener("DOMContentLoaded", function () {
    const codeInput = document.querySelector("input[name='code']");
    const submitButton = document.querySelector("button[type='submit']");
    if (codeInput && submitButton) {
        codeInput.addEventListener("input", function () {
            submitButton.disabled = codeInput.value.trim().length !== 6;
        });
    }
});