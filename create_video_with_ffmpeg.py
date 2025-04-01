import os
import numpy as np
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

def create_video_from_npy(npy_file_path, target_size=(256, 256), fps=10):
    """
    Create an MP4 video from a NumPy array file (.npy) using FFmpeg

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
    output_path = results_dir / f"{base_name}_ffmpeg.mp4"

    # Create a temporary directory to store frames
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory: {temp_dir}")

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

        # Process each frame
        print(f"Processing {len(data)} frames...")
        for i, frame in enumerate(data):
            # Print debug info for the first frame
            if i == 0:
                print(f"Frame shape: {frame.shape}")
                print(f"Frame min: {frame.min()}, max: {frame.max()}, dtype: {frame.dtype}")

            # Handle different frame shapes
            if len(frame.shape) == 2:
                # For grayscale data, convert to RGB using PIL
                img = Image.fromarray(frame).convert('RGB')
            elif len(frame.shape) == 3 and frame.shape[2] == 1:
                # For grayscale data with channel dimension, convert to RGB using PIL
                img = Image.fromarray(frame.squeeze()).convert('RGB')
            else:
                img = Image.fromarray(frame)

            # Resize the image to target size using nearest neighbor interpolation
            img_resized = img.resize(target_size, Image.NEAREST)

            # Save the frame as a PNG file
            frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
            img_resized.save(frame_path)

        # Use FFmpeg to create a video from the frames
        print("Creating video with FFmpeg...")

        # Construct the FFmpeg command
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file if it exists
            '-framerate', str(fps),
            '-i', os.path.join(temp_dir, 'frame_%04d.png'),
            '-c:v', 'libx264',  # Use H.264 codec
            '-pix_fmt', 'yuv420p',  # Pixel format for better compatibility
            '-crf', '23',  # Quality (lower is better, 23 is default)
            '-preset', 'medium',  # Encoding speed/compression trade-off
            str(output_path)
        ]

        # Run the FFmpeg command
        try:
            print(f"Running command: {' '.join(ffmpeg_cmd)}")
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Video saved to {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Error running FFmpeg: {e}")
            print(f"FFmpeg stderr: {e.stderr.decode()}")
            return None

if __name__ == "__main__":
    # Path to the .npy file
    npy_file = "source/npy/tactile_output_array.npy"

    # Create video from the NumPy array
    output_path = create_video_from_npy(npy_file)

    if output_path:
        print(f"Done! Video created at {output_path}")

        # Check the file size to make sure it's reasonable
        file_size = os.path.getsize(output_path)
        print(f"File size: {file_size} bytes")

        if file_size < 1000:
            print("Warning: The file size is very small, which might indicate a problem with the video.")
    else:
        print("Error: Failed to create video.")
