import pydicom
import numpy as np
import os
import imageio # Library to create GIFs

# --- Code to load your 3D volume (same as before) ---
extract_path = r'C:\Users\ADMIN\Downloads\Class-3-malocclusion\Class 3 malocclusion\DICOM'
# ... (paste the same loading code from Option 1 here) ...
if not os.path.isdir(extract_path):
    raise FileNotFoundError(f"The directory does not exist: {extract_path}")

slices = []
dicom_files = [os.path.join(extract_path, f) for f in os.listdir(extract_path) if os.path.isfile(os.path.join(extract_path, f))]

for file_path in dicom_files:
    try:
        slices.append(pydicom.dcmread(file_path))
    except pydicom.errors.InvalidDicomError:
        continue

if not slices:
    raise ValueError("No valid DICOM files were found.")

slices.sort(key=lambda x: int(x.InstanceNumber))
image_3d = np.stack([s.pixel_array for s in slices])
# --- End of loading code ---


# --- NEW: SAVE THE ENTIRE 3D SCAN AS A GIF ---

# 1. Normalize the pixel data to 8-bit (0-255) for the GIF
#    This converts the high-bit medical data to a standard image format.
image_3d_normalized = (image_3d - np.min(image_3d)) / (np.max(image_3d) - np.min(image_3d))
image_3d_uint8 = (image_3d_normalized * 255).astype(np.uint8)

# 2. Define the output filename
output_filename = "dicom_scan.gif"

# 3. Save the stack of images as a GIF
imageio.mimsave(output_filename, image_3d_uint8, duration=50, loop = 0) # duration is in milliseconds per frame

print(f"Successfully saved the full scan to '{output_filename}'")
