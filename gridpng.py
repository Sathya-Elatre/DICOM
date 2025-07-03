import pydicom
import matplotlib.pyplot as plt
import numpy as np
import os
import math # We'll need this for calculating the grid size

# --- Code to load your 3D volume (same as before) ---
# NOTE: Make sure this path is correct for your system.
extract_path = r'C:\Users\ADMIN\Downloads\Class-3-malocclusion\Class 3 malocclusion\DICOM'

if not os.path.isdir(extract_path):
    raise FileNotFoundError(f"The directory does not exist: {extract_path}")

slices = []
dicom_files = [os.path.join(extract_path, f) for f in os.listdir(extract_path) if os.path.isfile(os.path.join(extract_path, f))]

print(f"Found {len(dicom_files)} files, attempting to read as DICOM...")

for file_path in dicom_files:
    try:
        di = pydicom.dcmread(file_path)
        # We need pixel data to continue, so we skip files without it
        if 'PixelData' in di:
            slices.append(di)
    except pydicom.errors.InvalidDicomError:
        # This will skip non-DICOM files in the directory
        continue

if not slices:
    raise ValueError("No valid DICOM files with pixel data were found.")

# Sort the slices based on their instance number (slice order)
slices.sort(key=lambda x: int(x.InstanceNumber))

# Stack the pixel arrays into a 3D numpy array
# This assumes all slices have the same dimensions, which is typical for a series.
image_3d = np.stack([s.pixel_array for s in slices])
print(f"Successfully loaded {image_3d.shape[0]} slices into a 3D volume with shape {image_3d.shape}")
# --- End of loading code ---


# --- NEW: ARRANGE ALL SLICES INTO A GRID AND SAVE AS A SINGLE PNG ---

# 1. Get the dimensions of the slices and the total number of slices
num_slices, slice_height, slice_width = image_3d.shape

# 2. Calculate the grid size (number of rows and columns)
# We want to make the grid as square as possible
cols = math.ceil(math.sqrt(num_slices))
rows = math.ceil(num_slices / cols)
print(f"Creating a grid of {rows} rows and {cols} columns.")

# 3. Create a large blank "canvas" array to hold the grid
# The canvas will be black (0 value) initially.
# We use the same data type as the original images to avoid issues.
grid_image = np.zeros((rows * slice_height, cols * slice_width), dtype=image_3d.dtype)

# 4. Loop through the slices and place each one onto the canvas
current_slice = 0
for r in range(rows):
    for c in range(cols):
        if current_slice < num_slices:
            # Calculate the position to place the current slice
            y_start = r * slice_height
            y_end = y_start + slice_height
            x_start = c * slice_width
            x_end = x_start + slice_width
            
            # Copy the slice into the canvas
            grid_image[y_start:y_end, x_start:x_end] = image_3d[current_slice, :, :]
            
            current_slice += 1

# 5. Define the output filename and save the final grid image
output_filename = "dicom_grid.png"

# Use plt.imsave to save the numpy array as an image
# cmap='gray' is essential for correct grayscale representation
plt.imsave(output_filename, grid_image, cmap='gray')

print(f"\nSuccessfully saved all {num_slices} slices as a grid in '{output_filename}'")