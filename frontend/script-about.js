// About Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initAnimations();
    
    // Initialize hover effects
    initHoverEffects();
});

function initAnimations() {
    // Animate process steps
    const processSteps = document.querySelectorAll('.process-step');
    processSteps.forEach((step, index) => {
        step.style.animationDelay = `${index * 0.2}s`;
        step.classList.add('fade-in');
    });
    
    // Animate workflow steps
    const workflowSteps = document.querySelectorAll('.workflow-step');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animate');
                }, index * 200);
            }
        });
    }, { threshold: 0.5 });
    
    workflowSteps.forEach(step => observer.observe(step));
}

function initHoverEffects() {
    // Add hover effects to spec cards
    const specCards = document.querySelectorAll('.spec-card');
    
    specCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px)';
            card.style.boxShadow = 'var(--shadow-xl)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = 'var(--shadow-lg)';
        });
    });
    
    // Add hover effects to contact cards
    const contactCards = document.querySelectorAll('.contact-card');
    
    contactCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            const icon = card.querySelector('.contact-icon');
            icon.style.transform = 'scale(1.1)';
            icon.style.background = 'linear-gradient(135deg, var(--soft-blue-600) 0%, var(--soft-blue-700) 100%)';
        });
        
        card.addEventListener('mouseleave', () => {
            const icon = card.querySelector('.contact-icon');
            icon.style.transform = 'scale(1)';
            icon.style.background = 'linear-gradient(135deg, var(--soft-blue-500) 0%, var(--soft-blue-600) 100%)';
        });
    });
}

// Add CSS animation classes
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease forwards;
    }
    
    .workflow-step {
        opacity: 0;
        transform: translateX(-20px);
        transition: all 0.6s ease;
    }
    
    .workflow-step.animate {
        opacity: 1;
        transform: translateX(0);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .cnn-feature:hover .feature-icon {
        animation: pulse 0.6s ease;
    }
`;
document.head.appendChild(style);