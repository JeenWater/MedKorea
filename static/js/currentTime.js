window.onload = function(){
    const today = new Date();
    const year = today.getFullYear();
    const month = ('0' + (today.getMonth() + 1)).slice(-2);
    const day = ('0' + today.getDate()).slice(-2);
    const currentTime = `${year}-${month}-${day}`;
    document.getElementById("date").value = currentTime;
}