/**
 * Starfield animation for Observatory Mode
 * Lightweight canvas-based starfield with parallax effect
 */

let starfieldAnimationId = null;
let stars = [];
let mouseX = 0;
let mouseY = 0;

function initStarfield(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // Set canvas size
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Calculate star count based on screen area (keep CPU low)
    const screenArea = canvas.width * canvas.height;
    const starCount = Math.min(Math.floor(screenArea / 15000), 200); // Max 200 stars
    
    // Initialize stars
    stars = [];
    for (let i = 0; i < starCount; i++) {
        stars.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            z: Math.random() * 1000, // Depth
            speed: prefersReducedMotion ? 0 : 0.1 + Math.random() * 0.2,
            size: Math.random() * 1.5 + 0.5
        });
    }
    
    // Mouse tracking for parallax
    if (!prefersReducedMotion) {
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX / canvas.width - 0.5;
            mouseY = e.clientY / canvas.height - 0.5;
        });
    }
    
    // Animation loop with improved rendering
    function animate() {
        // Use darker clear for better star visibility
        ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        
        stars.forEach(star => {
            // Update position
            if (!prefersReducedMotion) {
                star.z -= star.speed;
                if (star.z <= 0) {
                    star.z = 1000;
                    star.x = Math.random() * canvas.width;
                    star.y = Math.random() * canvas.height;
                }
            }
            
            // Calculate parallax offset (reduced for subtlety)
            const parallaxX = prefersReducedMotion ? 0 : mouseX * (star.z / 1000) * 15;
            const parallaxY = prefersReducedMotion ? 0 : mouseY * (star.z / 1000) * 15;
            
            // Project 3D to 2D
            const k = 128 / star.z;
            const px = (star.x - centerX) * k + centerX + parallaxX;
            const py = (star.y - centerY) * k + centerY + parallaxY;
            const r = Math.max(0.5, star.size * k);
            
            // Draw star with improved rendering
            if (px >= 0 && px <= canvas.width && py >= 0 && py <= canvas.height) {
                const opacity = Math.min(k * 0.9, 1);
                // Draw glow for larger stars
                if (r > 1) {
                    const gradient = ctx.createRadialGradient(px, py, 0, px, py, r * 2);
                    gradient.addColorStop(0, `rgba(255, 255, 255, ${opacity})`);
                    gradient.addColorStop(0.5, `rgba(255, 255, 255, ${opacity * 0.5})`);
                    gradient.addColorStop(1, `rgba(255, 255, 255, 0)`);
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(px, py, r * 2, 0, Math.PI * 2);
                    ctx.fill();
                }
                // Draw core star
                ctx.beginPath();
                ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
                ctx.arc(px, py, r, 0, Math.PI * 2);
                ctx.fill();
            }
        });
        
        starfieldAnimationId = requestAnimationFrame(animate);
    }
    
    animate();
}

function stopStarfield() {
    if (starfieldAnimationId) {
        cancelAnimationFrame(starfieldAnimationId);
        starfieldAnimationId = null;
    }
}

