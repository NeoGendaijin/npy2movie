import os
import glob
from pathlib import Path

# Create results directory if it doesn't exist
results_dir = Path("results/movie")
results_dir.mkdir(exist_ok=True, parents=True)

# Get all PNG files in the images directory, sorted by name
image_files = sorted(glob.glob("source/images/frame_*.png"))

print(f"Found {len(image_files)} image files")

# Define the target size for upscaling (16x16 -> 256x256)
TARGET_SIZE = (128, 256)

# Try to create GIF using PIL/Pillow
# try:
#     from PIL import Image

#     print("Creating GIF using Pillow...")

#     # Open all images and resize them to 256x256
#     images = []
#     for image_file in image_files:
#         img = Image.open(image_file)
#         # Use nearest neighbor resampling to maintain pixel art look
#         img_resized = img.resize(TARGET_SIZE, Image.NEAREST)
#         images.append(img_resized)

#     # Save as GIF
#     gif_path = results_dir / "animation_256x256.gif"
#     images[0].save(
#         gif_path,
#         save_all=True,
#         append_images=images[1:],
#         optimize=False,
#         duration=33,  # 33ms per frame (approx. 30 fps)
#         loop=0  # 0 means loop forever
#     )

#     print(f"GIF saved to {gif_path}")
# except ImportError:
#     print("Pillow (PIL) is not installed. Cannot create GIF.")

# Try to create MP4 using OpenCV
try:
    import cv2
    import numpy as np

    print("Creating MP4 using OpenCV...")

    # Read first image to get dimensions
    first_img = cv2.imread(image_files[0])
    # Resize to 256x256
    first_img_resized = cv2.resize(first_img, TARGET_SIZE, interpolation=cv2.INTER_NEAREST)
    height, width, layers = first_img_resized.shape

    # Define codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'avc1'
    mp4_path = str(results_dir / "animation_256x256.mp4")
    out = cv2.VideoWriter(mp4_path, fourcc, 30.0, (width, height))

    # Write frames to video
    for image_file in image_files:
        img = cv2.imread(image_file)
        # Resize to 256x256 with nearest neighbor interpolation
        img_resized = cv2.resize(img, TARGET_SIZE, interpolation=cv2.INTER_NEAREST)
        out.write(img_resized)

    # Release the VideoWriter
    out.release()

    print(f"MP4 saved to {mp4_path}")
except ImportError:
    print("OpenCV is not installed. Trying imageio...")

    # Try to create MP4 using imageio as an alternative
    try:
        import imageio

        print("Creating MP4 using imageio...")

        # Read images and resize them
        images = []
        for image_file in image_files:
            img = imageio.imread(image_file)
            # Resize to 256x256
            img_resized = np.array(Image.fromarray(img).resize(TARGET_SIZE, Image.NEAREST))
            images.append(img_resized)

        # Save as MP4
        mp4_path = results_dir / "animation_256x256.mp4"
        imageio.mimsave(mp4_path, images, fps=30)

        print(f"MP4 saved to {mp4_path}")
    except ImportError:
        print("imageio is not installed. Cannot create MP4.")

print("Done!")
