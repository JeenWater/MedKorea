document.addEventListener("DOMContentLoaded", function () {
    const icon = document.querySelector('.icon');

    // 아이콘을 360도 회전시키는 애니메이션
    icon.style.transition = "transform 2s ease-in-out";
    icon.style.transform = "rotate(360deg)";

    // 아이콘을 클릭했을 때 색상 변경
    icon.addEventListener("click", function() {
        icon.style.filter = "hue-rotate(180deg)";
    });
});