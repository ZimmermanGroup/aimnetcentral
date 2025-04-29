import h5py
import shutil
import sys
import os
import numpy as np

def merge_datasets(src, dst, dst_name):
    """
    Append data from a source dataset to a destination dataset.

    Args:
        src: Source dataset (h5py.Dataset).
        dst: Destination group or file where the dataset should be appended.
        dst_name: The name of the dataset in the destination group.
    """
    src_data = src[()]

    if dst_name in dst:
        dst_data = dst[dst_name]
        combined_data = np.concatenate((dst_data[()], src_data), axis=0)
        del dst[dst_name]  # Remove old dataset to replace with combined one
        dst.create_dataset(dst_name, data=combined_data)
    else:
        dst.create_dataset(dst_name, data=src_data)

def copy_and_merge_datasets(src, dst, dst_group_path='/'):
    """
    Recursively copy and merge datasets from one HDF5 group to another.

    Args:
        src: Source group or file to copy datasets from.
        dst: Destination group or file to copy datasets to.
        dst_group_path: The path to the destination group within dst.
    """
    for name, item in src.items():
        dst_path = dst_group_path + name
        if isinstance(item, h5py.Dataset):
            merge_datasets(item, dst, dst_path)
        elif isinstance(item, h5py.Group):
            if dst_path not in dst:
                dst.create_group(dst_path)
            copy_and_merge_datasets(item, dst, dst_path + '/')

def merge_hdf5_files(file1, file2, output_file):
    """
    Merge two HDF5 files into an output HDF5 file.

    Args:
        file1: The path to the first HDF5 file.
        file2: The path to the second HDF5 file.
        output_file: The path to the output HDF5 file.
    """
    # Copy the first file to the output
    shutil.copyfile(file1, output_file)

    with h5py.File(output_file, 'a') as dst, h5py.File(file2, 'r') as src:
        copy_and_merge_datasets(src, dst)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python merge_hdf5.py <file1> <file2> <output_file>")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    output_file = sys.argv[3]

    if not os.path.exists(file1):
        print(f"Error: {file1} does not exist.")
        sys.exit(1)

    if not os.path.exists(file2):
        print(f"Error: {file2} does not exist.")
        sys.exit(1)

    merge_hdf5_files(file1, file2, output_file)
    print(f"Merged {file1} and {file2} into {output_file}")