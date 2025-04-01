import os
import numpy as np
import cv2
from pathlib import Path

def create_video_from_npy(npy_file_path, fps=8):
    """
    Create an MP4 video from a NumPy array file (.npy)
    Handles both grayscale and RGB data with different dimensions

    Args:
        npy_file_path: Path to the .npy file
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

    # Determine the target size based on the input shape
    if len(data.shape) == 4:
        _, height, width, channels = data.shape

        # Check if it's the 16x16x1 grayscale data
        if height == 16 and width == 16 and channels == 1:
            target_size = (256, 256)  # 16x16 -> 256x256 (scale factor: 16)
            print(f"Detected 16x16 grayscale data, resizing to {target_size}")

        # Check if it's the 64x96x3 RGB data
        elif height == 64 and width == 96 and channels == 3:
            target_size = (384, 256)  # 96x64 -> 384x256 (maintaining aspect ratio)
            print(f"Detected 64x96 RGB data, resizing to {target_size}")

        # For other shapes, maintain aspect ratio with width = 256
        else:
            scale_factor = 256 / width
            target_size = (256, int(height * scale_factor))
            print(f"Detected {width}x{height} data, resizing to {target_size}")
    else:
        raise ValueError(f"Unsupported array shape: {data.shape}")

    # Define the output path
    output_path = results_dir / f"{base_name}_{target_size[0]}x{target_size[1]}.mp4"

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
        codec_path = results_dir / f"{base_name}_{target_size[0]}x{target_size[1]}.{ext}"
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
            # For grayscale data without channel dimension, convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif len(frame.shape) == 3 and frame.shape[2] == 1:
            # For grayscale data with channel dimension, convert to RGB
            frame = frame.squeeze()  # Remove the channel dimension
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif len(frame.shape) == 3 and frame.shape[2] == 3:
            # For RGB data, use as is but convert from RGB to BGR (OpenCV uses BGR)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
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

def process_all_npy_files():
    """
    Process all .npy files in the npy directory
    """
    npy_dir = Path("source/npy")
    if not npy_dir.exists():
        print(f"Error: Directory {npy_dir} does not exist")
        return

    # Get all .npy files in the directory
    npy_files = list(npy_dir.glob("*.npy"))

    if not npy_files:
        print(f"No .npy files found in {npy_dir}")
        return

    print(f"Found {len(npy_files)} .npy files")

    # Process each file
    for npy_file in npy_files:
        try:
            print(f"\nProcessing {npy_file}...")
            output_path = create_video_from_npy(npy_file)

            if output_path:
                print(f"Successfully created video: {output_path}")

                # Check the file size
                file_size = os.path.getsize(output_path)
                print(f"File size: {file_size} bytes")

                if file_size < 1000:
                    print("Warning: The file size is very small, which might indicate a problem.")
            else:
                print(f"Failed to create video for {npy_file}")
        except Exception as e:
            print(f"Error processing {npy_file}: {e}")

if __name__ == "__main__":
    # Process all .npy files in the npy directory
    process_all_npy_files()
