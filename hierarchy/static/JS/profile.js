window.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('nav ul li a');
    const sections = document.querySelectorAll('.content section');

    function showSection(id) {
        sections.forEach(section => {
            if (section.id === id) {
                section.classList.remove('hidden');
            } else {
                section.classList.add('hidden');
            }
        });
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = e.target.getAttribute('href').slice(1);
            showSection(targetId);
        });
    });

    showSection('profile');

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.circle .bar').forEach(bar => {
            let progressValue = parseFloat(bar.dataset.progress); // Retrieve data-progress attribute
            let options = {
                startAngle: -1.55,
                size: 150,
                value: progressValue, // Convert progressValue to a percentage between 0 and 1
                fill: { gradient: ['#007C91', '#14FEFF'] }
            };
    
            // Initialize circle progress with options
            $(bar).circleProgress(options).on('circle-animation-progress', function(event, progress, stepValue) {
                $(this).parent().find("span").text(String(Math.round(progressValue)) + "%");
            });
        });
    });
    
    });
    
    


document.querySelectorAll('ul li a').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        const targetSection = document.getElementById(targetId);
        if (targetSection) {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
            targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
