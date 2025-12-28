/**
 * Backdrop crossfading system for Observatory Mode
 * Crossfades between era-specific backdrops based on timeline position
 */

// Define backdrops by time ranges (years)
// Each backdrop can use gradients or optional image URLs
// Images would go in static/img/backdrops/ (e.g., hadean.webp, paleozoic.webp, etc.)
const BACKDROPS = [
    {
        startYear: -5000000000,
        endYear: -4000000000,
        name: 'Hadean',
        gradient: 'radial-gradient(ellipse at center, rgba(139, 69, 19, 0.3) 0%, rgba(0, 0, 0, 0.6) 100%)',
        // image: '/static/img/backdrops/hadean.webp' // Optional
    },
    {
        startYear: -4000000000,
        endYear: -2500000000,
        name: 'Archean',
        gradient: 'radial-gradient(ellipse at center, rgba(75, 0, 130, 0.3) 0%, rgba(0, 0, 0, 0.6) 100%)',
    },
    {
        startYear: -2500000000,
        endYear: -541000000,
        name: 'Proterozoic',
        gradient: 'radial-gradient(ellipse at center, rgba(0, 100, 0, 0.3) 0%, rgba(0, 0, 0, 0.6) 100%)',
    },
    {
        startYear: -541000000,
        endYear: -252000000,
        name: 'Paleozoic',
        gradient: 'radial-gradient(ellipse at center, rgba(0, 150, 255, 0.3) 0%, rgba(0, 0, 0, 0.6) 100%)',
    },
    {
        startYear: -252000000,
        endYear: -66000000,
        name: 'Mesozoic',
        gradient: 'radial-gradient(ellipse at center, rgba(34, 139, 34, 0.3) 0%, rgba(0, 0, 0, 0.6) 100%)',
    },
    {
        startYear: -66000000,
        endYear: -10000,
        name: 'Cenozoic',
        gradient: 'radial-gradient(ellipse at center, rgba(255, 140, 0, 0.3) 0%, rgba(0, 0, 0, 0.6) 100%)',
    },
    {
        startYear: -10000,
        endYear: 2025,
        name: 'Human Era',
        gradient: 'radial-gradient(ellipse at center, rgba(70, 130, 180, 0.3) 0%, rgba(0, 0, 0, 0.6) 100%)',
    },
    {
        startYear: 2025,
        endYear: 10000000000,
        name: 'Future',
        gradient: 'radial-gradient(ellipse at center, rgba(138, 43, 226, 0.3) 0%, rgba(0, 0, 0, 0.6) 100%)',
    },
];

let currentBackdrop = null;
let backdropA = document.getElementById('backdrop-a');
let backdropB = document.getElementById('backdrop-b');
let isBackdropA = true;
let backdropTransitionTimeout = null;

/**
 * Find the backdrop that matches the given year
 */
function getBackdropForYear(year) {
    for (let backdrop of BACKDROPS) {
        if (year >= backdrop.startYear && year < backdrop.endYear) {
            return backdrop;
        }
    }
    // Fallback to first backdrop
    return BACKDROPS[0];
}

/**
 * Set backdrop based on midpoint year of visible timeline range
 */
function setBackdropForYear(midYear) {
    const backdrop = getBackdropForYear(midYear);
    
    // If same backdrop, no need to change
    if (currentBackdrop && currentBackdrop.name === backdrop.name) {
        return;
    }
    
    currentBackdrop = backdrop;
    
    // Clear any pending transition
    if (backdropTransitionTimeout) {
        clearTimeout(backdropTransitionTimeout);
    }
    
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const transitionDuration = prefersReducedMotion ? 0 : 2000; // 2 second crossfade
    
    // Determine which backdrop div to update
    const activeBackdrop = isBackdropA ? backdropA : backdropB;
    const inactiveBackdrop = isBackdropA ? backdropB : backdropA;
    
    // Set the new backdrop
    if (backdrop.image) {
        activeBackdrop.style.backgroundImage = `url(${backdrop.image}), ${backdrop.gradient}`;
    } else {
        activeBackdrop.style.backgroundImage = backdrop.gradient;
    }
    activeBackdrop.style.backgroundSize = 'cover';
    activeBackdrop.style.backgroundPosition = 'center';
    
    // Crossfade
    if (prefersReducedMotion) {
        // Instant switch for reduced motion
        activeBackdrop.style.opacity = '1';
        inactiveBackdrop.style.opacity = '0';
    } else {
        // Fade in active, fade out inactive
        activeBackdrop.style.transition = `opacity ${transitionDuration}ms ease-in-out`;
        inactiveBackdrop.style.transition = `opacity ${transitionDuration}ms ease-in-out`;
        activeBackdrop.style.opacity = '1';
        inactiveBackdrop.style.opacity = '0';
        
        // Switch which backdrop is active for next transition
        backdropTransitionTimeout = setTimeout(() => {
            isBackdropA = !isBackdropA;
        }, transitionDuration);
    }
}

/**
 * Initialize backdrops with default (middle of timeline)
 */
function initBackdrops() {
    if (!backdropA || !backdropB) return;
    
    // Start with middle of timeline
    const defaultBackdrop = getBackdropForYear(-2500000000);
    
    backdropA.style.backgroundImage = defaultBackdrop.gradient;
    backdropA.style.backgroundSize = 'cover';
    backdropA.style.backgroundPosition = 'center';
    backdropA.style.opacity = '1';
    
    backdropB.style.backgroundImage = defaultBackdrop.gradient;
    backdropB.style.backgroundSize = 'cover';
    backdropB.style.backgroundPosition = 'center';
    backdropB.style.opacity = '0';
    
    currentBackdrop = defaultBackdrop;
}

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBackdrops);
} else {
    initBackdrops();
}

