import pydicom
import matplotlib.pyplot as plt
import numpy as np
import os
import math

# --- Prerequisite Reminder ---
# This code requires special JPEG decoders. If you haven't already,
# make sure you have installed them in your environment:
# pip install pylibjpeg pylibjpeg-libjpeg
# -----------------------------

# --- Code to load your 3D volume (same as before) ---
extract_path = r'C:\Users\ADMIN\Downloads\Class-3-malocclusion\Class 3 malocclusion\DICOM'

if not os.path.isdir(extract_path):
    raise FileNotFoundError(f"The directory does not exist: {extract_path}")

slices = []
#dicom_files = [os.path.join(extract_path, f) for f in os.listdir(extract_path) if os.path.isfile(os.path.join(extract_path, f))]

dicom_files = []
for f in os.listdir(extract_path):
    file_path = os.path.join(extract_path, f)
    if os.path.isfile(file_path):
        dicom_files.append(file_path)


print(f"Found {len(dicom_files)} files, attempting to read as DICOM...")

for file_path in dicom_files:
    try:
        di = pydicom.dcmread(file_path)
        if 'PixelData' in di:
            slices.append(di)
    except pydicom.errors.InvalidDicomError:
        continue

if not slices:
    raise ValueError("No valid DICOM files with pixel data were found.")

print (slices)

slices.sort(key=lambda x: int(x.InstanceNumber))

# This line should now work correctly with pylibjpeg installed
""" 
   arrays = []
for s in slices:
    pixel_data = s.pixel_array
    arrays.append(pixel_data)

image_3d = np.stack(arrays)
"""

image_3d = np.stack([s.pixel_array for s in slices])
print(f"Successfully loaded {image_3d.shape[0]} slices into a 3D volume with shape {image_3d.shape}")
#--- End of loading code ---


# --- NEW: DIVIDE ALL SLICES INTO 15 GRID IMAGES ---

# 1. Define how many output images you want
num_output_images = 10
total_num_slices, slice_height, slice_width = image_3d.shape

# 2. Calculate how many slices will go into each output image
# Use math.ceil to ensure all slices are included, even if it doesn't divide evenly.
slices_per_image = math.ceil(total_num_slices / num_output_images)
print(f"\nDistributing {total_num_slices} slices into {num_output_images} images.")
print(f"Each output image will contain up to {slices_per_image} slices.")

# 3. Loop to create each of the 15 grid images
for i in range(num_output_images):
    # Calculate the start and end index for the current chunk of slices
    start_index = i * slices_per_image
    end_index = start_index + slices_per_image
    
    # If the start index is beyond the total number of slices, we are done.
    if start_index >= total_num_slices:
        break

    # Get the chunk of slices for this specific output image
    current_chunk = image_3d[start_index:end_index]
    num_slices_in_chunk = current_chunk.shape[0]

    # Calculate grid size for THIS CHUNK
    cols = math.ceil(math.sqrt(num_slices_in_chunk))
    rows = math.ceil(num_slices_in_chunk / cols)

    # Create a blank canvas for the current grid
    grid_image = np.zeros((rows * slice_height, cols * slice_width), dtype=current_chunk.dtype)

    # Populate the canvas with slices from the current chunk
    current_slice_in_chunk = 0
    for r in range(rows):
        for c in range(cols):
            if current_slice_in_chunk < num_slices_in_chunk:
                y_start, y_end = r * slice_height, (r + 1) * slice_height
                x_start, x_end = c * slice_width, (c + 1) * slice_width
                
                grid_image[y_start:y_end, x_start:x_end] = current_chunk[current_slice_in_chunk, :, :]
                current_slice_in_chunk += 1
    
    # Define a unique filename for each grid image.
    # The ":02d" part pads the number with a leading zero (e.g., 01, 02... 15)
    # which makes the files sort nicely in your file explorer.
    output_filename = f"dicom_grid_{i+1:02d}.png"
    
    # Save the generated grid to a file
    plt.imsave(output_filename, grid_image, cmap='gray')
    print(f"-> Saved '{output_filename}' containing {num_slices_in_chunk} slices.")

print("\nProcessing complete.")