window.onload = function(){
    const today = new Date();
    const year = today.getFullYear();
    const month = ('0' + (today.getMonth() + 1)).slice(-2);  // 월은 0부터 시작하므로 1을 더해줌
    const day = ('0' + today.getDate()).slice(-2);
    const correntTime = `${year}-${month}-${day}`;
    document.getElementById("date").value = correntTime;
}