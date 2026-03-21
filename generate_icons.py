import os
from PIL import Image, ImageDraw

def create_icon(size, filename):
    img = Image.new('RGB', (size, size), color=(14, 165, 233)) # Modern primary blue
    d = ImageDraw.Draw(img)
    
    # Draw a medical cross
    d.rectangle([(size * 0.4, size * 0.2), (size * 0.6, size * 0.8)], fill=(255, 255, 255))
    d.rectangle([(size * 0.2, size * 0.4), (size * 0.8, size * 0.6)], fill=(255, 255, 255))
    
    img.save(filename)

# Ensure public directory exists
os.makedirs("frontend/public", exist_ok=True)

# Generate standard PWA sizes
create_icon(192, "frontend/public/pwa-192x192.png")
create_icon(512, "frontend/public/pwa-512x512.png")
create_icon(180, "frontend/public/apple-touch-icon.png")
create_icon(64, "frontend/public/favicon.ico")

print("PWA Icons generated successfully!")
