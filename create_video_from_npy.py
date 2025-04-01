import os
import numpy as np
import cv2
from pathlib import Path

def create_video_from_npy(npy_file_path, target_size=(256, 256), fps=8):
    """
    Create an MP4 video from a NumPy array file (.npy)

    Args:
        npy_file_path: Path to the .npy file
        target_size: Output video resolution (width, height)
        fps: Frames per second
    """
    # Create results directory if it doesn't exist
    results_dir = Path("results/movie")
    results_dir.mkdir(exist_ok=True, parents=True)

    # Load the NumPy array
    print(f"Loading {npy_file_path}...")
    data = np.load(npy_file_path)

    # Print the shape of the array
    print(f"Array shape: {data.shape}")

    # Get the base name of the file without extension
    base_name = os.path.splitext(os.path.basename(npy_file_path))[0]

    # Define the output path
    output_path = results_dir / f"{base_name}.mp4"

    # Normalize the data to 0-255 range if needed
    if data.max() <= 1.0:
        # If data is in 0-1 range, scale to 0-255
        data = (data * 255).astype(np.uint8)
    elif data.max() > 255:
        # If data is beyond 255, normalize to 0-255
        data = ((data - data.min()) / (data.max() - data.min()) * 255).astype(np.uint8)
    else:
        # Ensure data is uint8
        data = data.astype(np.uint8)

    # Create a VideoWriter object
    # Try different codecs in order of compatibility
    codecs = [
        ('avc1', 'mp4'),  # H.264 in MP4
        ('mp4v', 'mp4'),  # MPEG-4 in MP4
        ('MJPG', 'avi'),  # Motion JPEG in AVI
        ('XVID', 'avi')   # XVID in AVI
    ]

    out = None
    for codec, ext in codecs:
        codec_path = results_dir / f"{base_name}.{ext}"
        print(f"Trying codec {codec} with container {ext}...")
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(str(codec_path), fourcc, fps, target_size)

        if writer.isOpened():
            out = writer
            output_path = codec_path
            print(f"Successfully created VideoWriter with codec {codec}")
            break
        else:
            print(f"Failed to create VideoWriter with codec {codec}")

    if out is None:
        print("Error: Could not create VideoWriter with any codec.")
        return None

    # Process each frame
    print(f"Processing {len(data)} frames...")
    for i, frame in enumerate(data):
        # Print debug info for the first frame
        if i == 0:
            print(f"Frame shape: {frame.shape}")
            print(f"Frame min: {frame.min()}, max: {frame.max()}, dtype: {frame.dtype}")

        # Handle different frame shapes
        if len(frame.shape) == 2:
            # For grayscale data, convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif len(frame.shape) == 3 and frame.shape[2] == 1:
            # For grayscale data with channel dimension, convert to RGB
            frame = frame.squeeze()  # Remove the channel dimension
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        else:
            frame_rgb = frame

        # Print debug info for the first processed frame
        if i == 0:
            print(f"Processed frame shape: {frame_rgb.shape}")
            print(f"Processed frame min: {frame_rgb.min()}, max: {frame_rgb.max()}, dtype: {frame_rgb.dtype}")

        # Resize the frame to target size using nearest neighbor interpolation
        frame_resized = cv2.resize(frame_rgb, target_size, interpolation=cv2.INTER_NEAREST)

        # Write the frame to the video
        out.write(frame_resized)

    # Release the VideoWriter
    out.release()

    print(f"Video saved to {output_path}")
    return output_path

def create_gif_from_npy(npy_file_path, target_size=(256, 256), fps=30):
    """
    Create a GIF from a NumPy array file (.npy)

    Args:
        npy_file_path: Path to the .npy file
        target_size: Output GIF resolution (width, height)
        fps: Frames per second
    """
    try:
        from PIL import Image
        import imageio

        # Create results directory if it doesn't exist
        results_dir = Path("results/movie")
        results_dir.mkdir(exist_ok=True, parents=True)

        # Load the NumPy array
        print(f"Loading {npy_file_path} for GIF creation...")
        data = np.load(npy_file_path)

        # Get the base name of the file without extension
        base_name = os.path.splitext(os.path.basename(npy_file_path))[0]

        # Define the output path
        output_path = results_dir / f"{base_name}.gif"

        # Normalize the data to 0-255 range if needed
        if data.max() <= 1.0:
            data = (data * 255).astype(np.uint8)
        elif data.max() > 255:
            data = ((data - data.min()) / (data.max() - data.min()) * 255).astype(np.uint8)
        else:
            data = data.astype(np.uint8)

        # Process frames
        frames = []
        for i, frame in enumerate(data):
            # Handle different frame shapes
            if len(frame.shape) == 2:
                # For grayscale data, convert to RGB using PIL
                img = Image.fromarray(frame).convert('RGB')
            elif len(frame.shape) == 3 and frame.shape[2] == 1:
                # For grayscale data with channel dimension, convert to RGB using PIL
                img = Image.fromarray(frame.squeeze()).convert('RGB')
            else:
                img = Image.fromarray(frame)

            # Resize the image
            img_resized = img.resize(target_size, Image.NEAREST)
            frames.append(np.array(img_resized))

        # Calculate duration in milliseconds
        duration = int(1000 / fps)

        # Save as GIF
        print(f"Creating GIF with {len(frames)} frames...")
        imageio.mimsave(output_path, frames, duration=duration, loop=0)

        print(f"GIF saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error creating GIF: {e}")
        return None

if __name__ == "__main__":
    # Path to the .npy file
    npy_file = "source/npy/tactile_target_array.npy"

    # Create video from the NumPy array
    video_path = create_video_from_npy(npy_file)

    # Also create a GIF version which might be more compatible
    gif_path = create_gif_from_npy(npy_file)

    if video_path:
        print(f"Done! Video created at {video_path}")

        # Check the file size to make sure it's reasonable
        file_size = os.path.getsize(video_path)
        print(f"Video file size: {file_size} bytes")

        if file_size < 1000:
            print("Warning: The video file size is very small, which might indicate a problem.")
    else:
        print("Error: Failed to create video.")

    if gif_path:
        print(f"GIF created at {gif_path}")

        # Check the file size
        file_size = os.path.getsize(gif_path)
        print(f"GIF file size: {file_size} bytes")
    else:
        print("Error: Failed to create GIF.")
