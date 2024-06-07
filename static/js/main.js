document.addEventListener("DOMContentLoaded", function() {
    const videoElement = document.querySelector('img[src="/video_feed"]');
    const stopButton = document.getElementById('stopButton');
    const startButton = document.getElementById('startButton');
    const logoutButton = document.getElementById('logoutButton');
    const audio = document.getElementById('alertSound');
    const modal = document.getElementById('alertModal');
    const reportModal = document.getElementById('reportModal');
    const fatigueCounterElement = document.getElementById('fatigueCounter');
    let fatigueCount = 0;  // Inicializar el contador de fatiga

    function checkFatigue() {
        fetch('/check_fatigue')
            .then(response => response.json())
            .then(data => {
                if (data.isFatigued) {
                    $(modal).modal('show');
                    audio.play();
                    fatigueCount++;  // Incrementa el contador de fatiga
                    fatigueCounterElement.textContent = `FATIGAS TOTALES DEL DIA: ${fatigueCount}`;  // Actualiza el texto del contador
                } else {
                    $(modal).modal('hide');
                }
            })
            .catch(error => console.error('Error checking fatigue:', error));
    }

    // Intervalo para verificar la fatiga cada segundo
    setInterval(checkFatigue, 1000);

    stopButton.addEventListener('click', function() {
        videoElement.src = '';
        fetch('/stop_video', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                $(reportModal).modal('show');
            });
    });

    startButton.addEventListener('click', function() {
        videoElement.src = '/video_feed';
        alert('Video reiniciado');
    });

    
});
