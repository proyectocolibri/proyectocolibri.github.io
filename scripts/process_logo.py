"""One-off utility: remove the flat background from the hummingbird logo
image and boost saturation slightly so it pops on the teal navbar."""
import numpy as np
from PIL import Image, ImageEnhance

SRC = "img/hummingbird-bird.jpg"
DST = "img/colibri-logo.png"

img = Image.open(SRC).convert("RGB")
arr = np.array(img).astype(np.float32)

h, w, _ = arr.shape
corner_px = np.concatenate([
    arr[0:8, 0:8].reshape(-1, 3),
    arr[0:8, w-8:w].reshape(-1, 3),
    arr[h-8:h, 0:8].reshape(-1, 3),
    arr[h-8:h, w-8:w].reshape(-1, 3),
])
bg_color = corner_px.mean(axis=0)
print("Background color sampled:", bg_color)

dist = np.sqrt(((arr - bg_color) ** 2).sum(axis=2))

low, high = 12.0, 45.0
alpha = np.clip((dist - low) / (high - low), 0.0, 1.0)
alpha = (alpha * 255).astype(np.uint8)

rgba = np.dstack([arr.astype(np.uint8), alpha])
out = Image.fromarray(rgba, mode="RGBA")

rgb = out.convert("RGB")
rgb = ImageEnhance.Color(rgb).enhance(1.25)
rgb = ImageEnhance.Contrast(rgb).enhance(1.08)
r, g, b = rgb.split()
out = Image.merge("RGBA", (r, g, b, out.split()[3]))

bbox = out.split()[3].getbbox()
if bbox:
    pad = 6
    bbox = (
        max(bbox[0] - pad, 0),
        max(bbox[1] - pad, 0),
        min(bbox[2] + pad, out.width),
        min(bbox[3] + pad, out.height),
    )
    out = out.crop(bbox)

out.save(DST)
print(f"Saved {DST}, size={out.size}")
