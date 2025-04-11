from os import listdir
import re
from ase import Atoms
from ase.calculators.singlepoint import SinglePointCalculator
from ase.io import write

def extract_orca_data(out_file_path, xyz_file_path):
    with open(out_file_path, 'r+') as f:
        text_lines = f.readlines()
    f.close()

    symbols = []
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
                symbols.append(coord_string.split()[0])
                coord_lst = []
                for item in coord_string.split()[1:]:
                    coord_lst.append(float(item))
                positions.append(tuple(coord_lst))
            
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
            Energy = float(text.split()[-1]) * 27.2114079527 # hartree to eV

        elif "CARTESIAN GRADIENT" in text:
            gradient_start_index = index + 3
            for jdx, text2 in enumerate(text_lines[index:]):
                if "Difference to translation invariance" in text2:
                    gradient_stop_index = index + jdx - 1
                    break

            gradient_list = text_lines[gradient_start_index:gradient_stop_index]

            for gradient_string in gradient_list:
                grad_lst = []
                for item in gradient_string.split()[-3:]:
                    grad_lst.append(float(item) * 51.42208976) # hartree/bohr to eV/A
                forces.append(tuple(grad_lst))

            
    atoms = Atoms(symbols=symbols,
                  positions=positions)
    
    calc = SinglePointCalculator(atoms, 
                                 energy=Energy, forces=forces, charges=charges)
    
    atoms.calc = calc

    write(xyz_file_path, atoms)


directory = "./"  # Provide the absolute path of the directory with ORCA output files
files_dir = listdir(directory)

files_list = []

for names in files_dir:
    if names.endswith(".out"):
        files_list.append(names)

new_files_list = sorted(files_list)

for file in new_files_list:
    orca_output_file_path = file
    ase_output_xyz_path = re.sub(".out", ".xyz", file)

    extract_orca_data(orca_output_file_path, ase_output_xyz_path)