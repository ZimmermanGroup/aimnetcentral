import os
import re
import numpy as np
from os import listdir
from ase import Atoms
from ase.data import atomic_numbers

def write_manual_extxyz(filename, atoms, forces, charges, energy):
    Z = atoms.get_atomic_numbers()
    positions = atoms.get_positions()
    n_atoms = len(Z)

    with open(filename, 'w') as f:
        f.write(f"{n_atoms}\n")
        f.write(f"Properties=Z:I:1:pos:R:3:forces:R:3:charge:R:1 energy={energy:.12f} pbc=\"F F F\"\n")
        for i in range(n_atoms):
            z = Z[i]
            x, y, z_pos = positions[i]
            fx, fy, fz = forces[i]
            q = charges[i]
            f.write(f"{z:<2d}      {x: .8f}      {y: .8f}      {z_pos: .8f}      "
                    f"{fx: .8f}      {fy: .8f}      {fz: .8f}      {q: .8f}\n")

def extract_orca_data(out_file_path, xyz_file_path):
    with open(out_file_path, 'r+') as f:
        text_lines = f.readlines()

    symbol_to_number = {
        "H": 1,
        "B": 5,
        "C": 6,
        "N": 7,
        "O": 8
    }

    numbers = []
    positions = []
    forces = []
    charges = []

    for index, text in enumerate(text_lines):
        if "CARTESIAN COORDINATES (ANGSTROEM)" in text:
            coord_start_index = index + 2
            for jdx, text2 in enumerate(text_lines[index:]):
                if "CARTESIAN COORDINATES (A.U.)" in text2:
                    coord_stop_index = index + jdx - 2
                    break
            coords_list = text_lines[coord_start_index:coord_stop_index]

            for coord_string in coords_list:
                symbol = coord_string.split()[0]
                atomic_number = symbol_to_number.get(symbol, atomic_numbers.get(symbol))
                if atomic_number is None:
                    raise ValueError(f"Unknown atomic symbol: {symbol}")
                numbers.append(atomic_number)
                coord_lst = [float(x) for x in coord_string.split()[1:]]
                positions.append(coord_lst)

        elif "MULLIKEN ATOMIC CHARGES" in text:
            charge_start_index = index + 2
            for jdx, text2 in enumerate(text_lines[index:]):
                if "Sum of atomic charges" in text2:
                    charge_stop_index = index + jdx
                    break
            charge_list = text_lines[charge_start_index:charge_stop_index]
            for charge_string in charge_list:
                charges.append(float(charge_string.split()[-1]))

        elif "FINAL SINGLE POINT ENERGY" in text:
            Energy = float(text.split()[-1]) * 27.2114079527

        elif "CARTESIAN GRADIENT" in text:
            gradient_start_index = index + 3
            for jdx, text2 in enumerate(text_lines[index:]):
                if "Difference to translation invariance" in text2:
                    gradient_stop_index = index + jdx - 1
                    break
            gradient_list = text_lines[gradient_start_index:gradient_stop_index]
            for gradient_string in gradient_list:
                grad_lst = [float(x) * 51.42208976 for x in gradient_string.split()[-3:]]
                forces.append(grad_lst)

    atoms = Atoms(numbers=numbers, positions=positions)
    write_manual_extxyz(xyz_file_path, atoms, forces, charges, Energy)

# === File Handling ===
directory = "/export/zimmerman/taveewit/CANS/Test/counterions/HNEt3+/qchem/modified_DE_GSM2/reactant213_intermediate213/restart_002/restart2_002over/restart3_002over/foraimnet2_orca"
files_dir = listdir(directory)

files_list = [name for name in files_dir if name.endswith(".out")]
new_files_list = sorted(files_list)

for file in new_files_list:
    orca_output_file_path = os.path.join(directory, file)
    ase_output_xyz_path = os.path.join(directory, re.sub(".out", ".xyz", file))
    extract_orca_data(orca_output_file_path, ase_output_xyz_path)
    print(f"Processed: {file}")

