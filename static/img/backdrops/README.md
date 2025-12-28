# Backdrop Images Directory

This directory can contain optional backdrop images for different eras in Observatory Mode.

## Expected Image Names

The backdrop system in `static/js/backdrops.js` supports optional images. To use images, uncomment the `image` property in the BACKDROPS array and add images here:

- `hadean.webp` - Hadean Eon (-5B to -4B years)
- `archean.webp` - Archean Eon (-4B to -2.5B years)
- `proterozoic.webp` - Proterozoic Eon (-2.5B to -541M years)
- `paleozoic.webp` - Paleozoic Era (-541M to -252M years)
- `mesozoic.webp` - Mesozoic Era (-252M to -66M years)
- `cenozoic.webp` - Cenozoic Era (-66M to -10K years)
- `human.webp` - Human Era (-10K to present)
- `future.webp` - Future (2025+)

## Format

- Recommended: WebP format for best compression
- Alternative: PNG or JPG
- Size: 1920x1080 or larger recommended
- Style: Should be semi-transparent or dark to work with the overlay system

## Note

The app works perfectly without any images - gradients are used as fallbacks. Images are purely optional enhancements.

