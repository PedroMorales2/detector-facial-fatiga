document.addEventListener("DOMContentLoaded", function () {
    const videoElement = document.querySelector('img[src="/video_feed"]');
    const stopButton = document.getElementById('stopButton');
    const startButton = document.getElementById('startButton');
    const audio = document.getElementById('alertSound');
    const modal = document.getElementById('alertModal');
    const reportModal = $('#reportModal'); // Use jQuery for modal handling if Bootstrap JS is included
    const fatigueCounterElement = document.getElementById('fatigueCounter');
    const spinner = document.getElementById('spinner'); // Get the spinner element
    let fatigueCount = 0;  // Initialize the fatigue count

    function showSpinner() {
        spinner.style.display = 'block'; // Display the spinner
    }

    function hideSpinner() {
        spinner.style.display = 'none'; // Hide the spinner
    }

    function checkFatigue() {
        fetch('/check_fatigue')
            .then(response => response.json())
            .then(data => {
                if (data.isFatigued) {
                    $(modal).modal('show');
                    audio.play();
                    fatigueCount++;  // Incrementa el contador de fatiga
                    fatigueCounterElement.textContent = `FATIGAS TOTALES DEL DIA: ${fatigueCount}`;
                } else {
                    $(modal).modal('hide');
                }
            })
            .catch(error => console.error('Error checking fatigue:', error));
    }

    setInterval(checkFatigue, 1000);

    stopButton.addEventListener('click', function () {
        showSpinner();
        videoElement.src = '';
        fetch('/stop_video', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                hideSpinner();
                reportModal.modal('show'); // Using Bootstrap's jQuery method to show the modal
            });
    });

    startButton.addEventListener('click', function () {
        videoElement.src = '/video_feed';
        videoElement.onload = () => {
            hideSpinner();
            alert('Video reiniciado');
        };
    });

});



document.addEventListener("DOMContentLoaded", function () {
    const toggleIcon = document.getElementById('toggleIcon');

    function toggleTheme() {
        document.body.classList.toggle('dark-mode');
        document.body.classList.toggle('light-mode');
        if (document.body.classList.contains('dark-mode')) {
            toggleIcon.classList.remove('fa-sun');
            toggleIcon.classList.add('fa-moon');
        } else {
            toggleIcon.classList.remove('fa-moon');
            toggleIcon.classList.add('fa-sun');
        }
    }

    toggleIcon.addEventListener('click', toggleTheme);
});
