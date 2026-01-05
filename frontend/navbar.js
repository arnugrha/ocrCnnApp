// Navbar Component
document.addEventListener('DOMContentLoaded', function() {
    // Get current page
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    // Create navbar HTML
    const navbarHTML = `
        <nav class="navbar">
            <div class="container">
                <div class="navbar-content">
                    <!-- Logo -->
                    <a href="index.html" class="navbar-logo">
                        <i class="fas fa-robot logo-icon"></i>
                        <span class="logo-text">OCR CNN</span>
                    </a>
                    
                    <!-- Mobile Menu Toggle -->
                    <button class="navbar-toggle" id="navbarToggle">
                        <i class="fas fa-bars"></i>
                    </button>
                    
                    <!-- Navigation Links -->
                    <div class="navbar-menu" id="navbarMenu">
                        <a href="index.html" class="nav-link ${currentPage === 'index.html' ? 'active' : ''}">
                            <i class="fas fa-home"></i>
                            <span>Beranda</span>
                        </a>
                        <a href="ocr.html" class="nav-link ${currentPage === 'ocr.html' ? 'active' : ''}">
                            <i class="fas fa-font"></i>
                            <span>OCR</span>
                        </a>
                        <a href="about.html" class="nav-link ${currentPage === 'about.html' ? 'active' : ''}">
                            <i class="fas fa-info-circle"></i>
                            <span>Tentang</span>
                        </a>
                    </div>
                    
                    <!-- User Actions -->
                    <div class="navbar-actions">
                        <a href="ocr.html" class="btn btn-primary btn-sm">
                            <i class="fas fa-play"></i>
                            <span>Coba Sekarang</span>
                        </a>
                    </div>
                </div>
            </div>
        </nav>
        
        <!-- Mobile Menu -->
        <div class="mobile-menu" id="mobileMenu">
            <div class="mobile-menu-content">
                <a href="index.html" class="mobile-nav-link ${currentPage === 'index.html' ? 'active' : ''}">
                    <i class="fas fa-home"></i>
                    <span>Beranda</span>
                </a>
                <a href="ocr.html" class="mobile-nav-link ${currentPage === 'ocr.html' ? 'active' : ''}">
                    <i class="fas fa-font"></i>
                    <span>OCR</span>
                </a>
                <a href="about.html" class="mobile-nav-link ${currentPage === 'about.html' ? 'active' : ''}">
                    <i class="fas fa-info-circle"></i>
                    <span>Tentang</span>
                </a>
                <a href="ocr.html" class="btn btn-primary btn-block">
                    <i class="fas fa-play"></i>
                    <span>Coba OCR Sekarang</span>
                </a>
            </div>
        </div>
    `;
    
    // Insert navbar into container
    const navbarContainer = document.getElementById('navbar-container');
    if (navbarContainer) {
        navbarContainer.innerHTML = navbarHTML;
        
        // Initialize mobile menu toggle
        const navbarToggle = document.getElementById('navbarToggle');
        const mobileMenu = document.getElementById('mobileMenu');
        const navbarMenu = document.getElementById('navbarMenu');
        
        if (navbarToggle && mobileMenu) {
            navbarToggle.addEventListener('click', function() {
                mobileMenu.classList.toggle('active');
                navbarToggle.innerHTML = mobileMenu.classList.contains('active') 
                    ? '<i class="fas fa-times"></i>' 
                    : '<i class="fas fa-bars"></i>';
            });
            
            // Close mobile menu when clicking outside
            document.addEventListener('click', function(event) {
                if (!navbarToggle.contains(event.target) && 
                    !mobileMenu.contains(event.target) && 
                    !navbarMenu.contains(event.target)) {
                    mobileMenu.classList.remove('active');
                    navbarToggle.innerHTML = '<i class="fas fa-bars"></i>';
                }
            });
            
            // Close mobile menu when clicking a link
            const mobileLinks = mobileMenu.querySelectorAll('.mobile-nav-link, .btn');
            mobileLinks.forEach(link => {
                link.addEventListener('click', function() {
                    mobileMenu.classList.remove('active');
                    navbarToggle.innerHTML = '<i class="fas fa-bars"></i>';
                });
            });
        }
    }
});