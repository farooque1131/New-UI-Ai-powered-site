document.addEventListener('DOMContentLoaded', () => {
    let current = 0;
    const slides = document.querySelectorAll(".slide");
    const carousel = document.getElementById('carousel');

    if (slides.length === 0) return;

    function moveSlide(n) {
        slides[current].classList.remove("active-slide");
        current = (current + n + slides.length) % slides.length;
        slides[current].classList.add("active-slide");
    }

    // Auto-play
    let autoScroll = setInterval(() => moveSlide(1), 5000);

    function resetTimer() {
        clearInterval(autoScroll);
        autoScroll = setInterval(() => moveSlide(1), 5000);
    }

    // Button Listeners
    document.querySelector('.prev').addEventListener('click', () => {
        moveSlide(-1);
        resetTimer();
    });

    document.querySelector('.next').addEventListener('click', () => {
        moveSlide(1);
        resetTimer();
    });

    // Mobile Swipe
    let touchStartX = 0;
    carousel.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
    }, {passive: true});

    carousel.addEventListener('touchend', e => {
        let touchEndX = e.changedTouches[0].screenX;
        if (touchEndX < touchStartX - 50) { moveSlide(1); resetTimer(); }
        if (touchEndX > touchStartX + 50) { moveSlide(-1); resetTimer(); }
    }, {passive: true});
});

// Keep this outside for the onclick in HTML
function toggleMenu() {
    const nav = document.getElementById('nav-menu');
    const burger = document.querySelector('.burger');
    nav.classList.toggle('nav-active');
    burger.classList.toggle('toggle');
}


setTimeout(() => {
    document.querySelectorAll('.toast-message').forEach(el => {
        el.remove();
    });
}, 5000);

function confirmDelete() {
    return confirm("Are you sure you want to delete this comment?");
}


function toggleModal() {
    const modal = document.getElementById('editModal');
    if (modal.style.display === "flex") {
        modal.style.display = "none";
    } else {
        modal.style.display = "flex";
    }
}

// Close modal if user clicks outside the white box
window.onclick = function(event) {
    const modal = document.getElementById('editModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}


function toggleElement(elementId) {
    const element = document.getElementById(elementId);
    if (element.style.display === "none") {
        element.style.display = "block";
    } else {
        element.style.display = "none";
    }
}


// Share Functionality
function copyShareLink() {
    const el = document.createElement('textarea');
    el.value = window.location.href;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    
    // Using your existing alert style or a simple alert
    alert("Link copied to clipboard!");
}

// Like Functionality (AJAX)
document.getElementById('like-button').addEventListener('click', function() {
    const postId = this.dataset.postId;
    const button = this;
    const countSpan = document.getElementById('like-count');

    fetch(`/like-post/${postId}/`, {
    method: 'POST',
    headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        'Content-Type': 'application/json'
    }
    })
    .then(response => {
        if (!response.ok) {
            // If user is not logged in or server error, show message
            alert("Please login to like this post!");
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        countSpan.innerText = data.total_likes;
        button.classList.toggle('active', data.liked);
    })
    .catch(error => console.error('Fetch Error:', error));
});