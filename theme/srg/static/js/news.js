        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Add scroll effect to sections
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.transform = 'translateY(0)';
                    entry.target.style.opacity = '1';
                }
            });
        }, {
            threshold: 0.1
        });

        document.querySelectorAll('.section, .news-item').forEach(element => {
            element.style.transform = 'translateY(20px)';
            element.style.opacity = '0';
            element.style.transition = 'transform 0.6s ease, opacity 0.6s ease';
            observer.observe(element);
        });

        // Add staggered animation to news items
        document.querySelectorAll('.news-item').forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
        });
