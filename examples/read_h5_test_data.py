#!/usr/bin/env python3
"""
Script to read and summarize the contents of an HDF5 test file.
"""

import h5py
import argparse
import os
import sys
import numpy as np

def summarize_h5_contents(file_path):
    """
    Read and summarize the contents of an HDF5 file.
    
    Args:
        file_path (str): Path to the HDF5 file
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
        
    try:
        with h5py.File(file_path, 'r') as h5_file:
            print(f"\nSummary of HDF5 file: {file_path}\n")
            print("=" * 80)
            
            # Start recursive exploration of the file structure
            explore_h5_group(h5_file, level=0)

            # Print a summary of molecule names found
            print("\nMolecule Names Summary:")
            print("=" * 80)
            collect_molecule_names(h5_file)

    except Exception as e:
        print(f"Error reading HDF5 file: {e}")
        sys.exit(1)
        
def explore_h5_group(group, level=0):
    """
    Recursively explore an HDF5 group and print its contents.
    """
    indent = "  " * level
    
    # Print group attributes
    if level > 0:  # Skip for root group
        print(f"{indent}Group: {group.name}")
        print_attributes(group, level)

        # Check for molecule identifiers in this group
        if "_id" in group:
            try:
                ids = group["_id"][...]
                print(f"{indent}  Molecule IDs: {ids}")
            except:
                print(f"{indent}  Molecule IDs: <Unable to display>")

    # Explore all items in the group
    for name, item in group.items():
        if isinstance(item, h5py.Group):
            # If item is a group, explore it recursively
            explore_h5_group(item, level + 1)
        elif isinstance(item, h5py.Dataset):
            # If item is a dataset, print its info
            print(f"{indent}  Dataset: {name}")
            print(f"{indent}    Shape: {item.shape}")
            print(f"{indent}    Type: {item.dtype}")
            
            # Print a sample of the data for small datasets
            if np.prod(item.shape) < 10:  # Only for small datasets
                try:
                    print(f"{indent}    Data: {item[...]}")
                except:
                    print(f"{indent}    Data: <Unable to display>")
                    
            # Print dataset attributes
            print_attributes(item, level + 1)
            
            print("")  # Empty line for readability

def collect_molecule_names(group, path=""):
    """
    Recursively collect molecule names from _id datasets in groups.
    """
    molecule_group_count = 0

    # Check if this group has _id dataset
    if "_id" in group:
        try:
            ids = group["_id"][...]
            if isinstance(ids, np.ndarray):
                if ids.size > 0:
                    molecule_group_count += 1
                    print(f"Group: {group.name}")

                    # Extract molecule names/IDs - handle different formats
                    if ids.dtype.kind == "S" or ids.dtype.kind == "U":  # String type
                        # Convert bytes to strings if necessary
                        if ids.dtype.kind == "S":
                            names = [id.decode("utf-8", "ignore") for id in ids]
                        else:
                            names = ids.tolist()

                        # Display first few and last few if there are many
                        if len(names) > 10:
                            print(f"  Molecules ({len(names)} total): {names[:5]} ... {names[-5:]}")
                        else:
                            print(f"  Molecules ({len(names)} total): {names}")
                    else:
                        # For numeric IDs
                        if ids.size > 10:
                            print(f"  Molecule IDs ({ids.size} total): {ids[:5]} ... {ids[-5:]}")
                        else:
                            print(f"  Molecule IDs ({ids.size} total): {ids}")
                    print("")
        except Exception as e:
            print(f"  Error reading _id dataset in {group.name}: {e}")

    # Recursively check subgroups
    for name, item in group.items():
        if isinstance(item, h5py.Group):
            subgroup_count = collect_molecule_names(item, path + "/" + name if path else name)
            molecule_group_count += subgroup_count

    return molecule_group_count


def print_attributes(obj, level):
    """
    Print attributes of an HDF5 object.
    """
    indent = "  " * level
    
    if len(obj.attrs) > 0:
        print(f"{indent}  Attributes:")
        for attr_name, attr_value in obj.attrs.items():
            print(f"{indent}    {attr_name}: {attr_value}")

def main():
    parser = argparse.ArgumentParser(description="Summarize the contents of an HDF5 file.")
    parser.add_argument("file_path", help="Path to the HDF5 file to analyze")
    
    args = parser.parse_args()
    
    summarize_h5_contents(args.file_path)

if __name__ == "__main__":
    main()
