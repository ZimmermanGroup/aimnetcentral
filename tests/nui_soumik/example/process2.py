from aimnet.data import SizeGroupedDataset
import numpy as np
import os

def read_trj(fname):
    coords, numbers = [], []
    forces, charges = [], []
    energies = []

    with open(fname) as f:
        while True:
            line = f.readline()
            if not line:
                break
            if line.strip() == '':
                continue

            num_atoms = int(line.strip())
            comment = f.readline().strip()

            # Extract energy from comment line
            energy = None
            if 'energy=' in comment:
                try:
                    energy = float(comment.split('energy=')[1].split()[0])
                except Exception:
                    energy = None
            energies.append(energy)

            tc, tn, tf, tq = [], [], [], []
            for _ in range(num_atoms):
                row = f.readline().split()
                tn.append(int(row[0]))
                tc.append([float(row[1]), float(row[2]), float(row[3])])
                tf.append([float(row[4]), float(row[5]), float(row[6])])
                tq.append(float(row[7]))

            coords.append(tc)
            numbers.append(tn)
            forces.append(tf)
            charges.append(tq)

    return (
        np.array(coords),
        np.array(numbers),
        np.array(forces),
        np.array(charges),
        np.array(energies),
    )


if __name__ == '__main__':
    prefix = 'strucs/'
    xyzs = sorted(os.listdir(prefix))

    for xyz in xyzs:
        coord, numbers, forces, charges, energies = read_trj(prefix + xyz)
        charge = np.zeros(len(coord))  # net charge for each molecule

        d = dict(
            coord=coord,
            numbers=numbers,
            forces=forces,
            charges=charges,
            energy=energies,
            charge=charge,
        )

        dd = {coord.shape[1]: d}

        if 'ds' not in locals():
            ds = SizeGroupedDataset(dd)
        else:
            tds = SizeGroupedDataset(dd)
            ds.merge(tds)
            del tds

    print('Total number of systems:', len(ds))
    ds.save_h5('train_with_energy_forces_charges.h5')

    # Load to verify
    ds_loaded = SizeGroupedDataset('train_with_energy_forces_charges.h5')
    print('Loaded dataset:', len(ds_loaded))

    # Inspect
    print('#######EXAMPLE OF HOW TO EXAMINE THE DS##########')
    for key, val in ds.items():
        print(key, val.keys())
        print('coord shape:', val['coord'].shape)
        print('forces shape:', val['forces'].shape)
        print('charges shape:', val['charges'].shape)
        print('energy shape:', val['energy'].shape)

