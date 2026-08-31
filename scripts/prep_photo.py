import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py hero.png")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    output_path = Path("source-prepped.png")

    print(f"Loading: {input_path}")

    # Open the original image
    image = Image.open(input_path).convert("RGBA")

    print("Removing background with rembg/U2Net...")

    # Remove background
    no_background = remove(image)

    # Convert to OpenCV format
    rgba = np.array(no_background)

    # Separate RGB and alpha channels
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    # Find the visible subject
    alpha_mask = alpha > 10

    if not np.any(alpha_mask):
        print("Error: No subject detected in the image.")
        sys.exit(1)

    ys, xs = np.where(alpha_mask)

    x1, x2 = xs.min(), xs.max()
    y1, y2 = ys.min(), ys.max()

    # Add a small amount of padding around the subject
    padding = int(max(x2 - x1, y2 - y1) * 0.08)

    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(rgb.shape[1] - 1, x2 + padding)
    y2 = min(rgb.shape[0] - 1, y2 + padding)

    cropped_rgb = rgb[y1:y2 + 1, x1:x2 + 1]
    cropped_alpha = alpha[y1:y2 + 1, x1:x2 + 1]

    # Convert to BGR for OpenCV
    bgr = cv2.cvtColor(cropped_rgb, cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # Improve local contrast using CLAHE
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced_gray = clahe.apply(gray)

    # Convert back to RGB
    enhanced_rgb = cv2.cvtColor(
        enhanced_gray,
        cv2.COLOR_GRAY2RGB
    )

    # Keep the original transparency
    result_rgba = np.dstack(
        (enhanced_rgb, cropped_alpha)
    )

    # Make the output square
    height, width = enhanced_rgb.shape[:2]
    size = max(height, width)

    canvas = np.zeros(
        (size, size, 4),
        dtype=np.uint8
    )

    offset_x = (size - width) // 2
    offset_y = (size - height) // 2

    canvas[
        offset_y:offset_y + height,
        offset_x:offset_x + width
    ] = result_rgba

    # Resize to a reasonable working size
    final_size = 900

    resized = cv2.resize(
        canvas,
        (final_size, final_size),
        interpolation=cv2.INTER_AREA
    )

    # Save PNG
    Image.fromarray(resized).save(
        output_path,
        "PNG"
    )

    print(f"Done!")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()