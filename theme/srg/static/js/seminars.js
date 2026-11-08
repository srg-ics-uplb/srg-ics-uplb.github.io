    function shareItem(itemId) {
        const currentUrl = window.location.href.split('#')[0];
        const shareUrl = `${currentUrl}#${itemId}`;
        
        // Copy to clipboard
        navigator.clipboard.writeText(shareUrl).then(() => {
            showShareNotification();
        }).catch(() => {
            // Fallback for browsers that don't support clipboard API
            const textArea = document.createElement('textarea');
            textArea.value = shareUrl;
            document.body.appendChild(textArea);
            textArea.select();
            textArea.setSelectionRange(0, 99999);
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showShareNotification();
        });
    }

    function showShareNotification() {
        const notification = document.getElementById('shareNotification');
        notification.classList.add('show');
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }

    // Scroll to item if URL contains hash
    function scrollToItemFromHash() {
        const hash = window.location.hash;
        if (hash) {
            const element = document.querySelector(hash);
            if (element) {
                setTimeout(() => {
                    element.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                    // Add highlight effect
                    element.style.outline = '3px solid #8B1538';
                    element.style.outlineOffset = '5px';
                    setTimeout(() => {
                        element.style.outline = 'none';
                        element.style.outlineOffset = '0';
                    }, 3000);
                }, 500);
            }
        }
    }

    // Call on page load
    window.addEventListener('load', scrollToItemFromHash);
    window.addEventListener('hashchange', scrollToItemFromHash);

    function toggleCollapsible(button, contentId) {
        const content = document.getElementById(contentId);
        const isActive = content.classList.contains('active');
        
        // Close all other collapsibles in the same seminar item
        const seminarItem = button.closest('.seminar-item');
        const allContents = seminarItem.querySelectorAll('.collapsible-content');
        const allButtons = seminarItem.querySelectorAll('.collapsible-btn');
        
        allContents.forEach(c => c.classList.remove('active'));
        allButtons.forEach(b => b.classList.remove('active'));
        
        // Toggle the clicked one
        if (!isActive) {
            content.classList.add('active');
            button.classList.add('active');
        }
    }

    // Add smooth scrolling for navigation links
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

    // Add scroll animation
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

    document.querySelectorAll('.section, .seminar-item').forEach(element => {
        element.style.transform = 'translateY(20px)';
        element.style.opacity = '0';
        element.style.transition = 'transform 0.6s ease, opacity 0.6s ease';
        observer.observe(element);
    });
