"""Physics regressions for the explicit RHF loop; run with unittest discovery."""
import sys
import unittest
from pathlib import Path

import numpy as np
from pyscf import gto, lib, scf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hf_engine import (BOHR_ANGSTROM, build_molecule, geometry_from_smiles,
                       orbital_cube, run_rhf)


class RHFPhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lib.num_threads(1)
        # Some hosted test environments omit /proc/PID/statm. This affects only
        # PySCF memory bookkeeping, not integral evaluation or the SCF equations.
        try:
            lib.current_memory()
        except FileNotFoundError:
            lib.current_memory = lambda: (0., 0.)
        angle = np.deg2rad(104.5)
        bond = .9584 / BOHR_ANGSTROM
        cls.water_atoms = np.array([8, 1, 1])
        cls.water_coords = np.array([
            [0., 0., 0.],
            [bond*np.sin(angle/2), 0., bond*np.cos(angle/2)],
            [-bond*np.sin(angle/2), 0., bond*np.cos(angle/2)],
        ])

    def reference(self, atoms, coords, charge=0):
        mol = build_molecule(atoms, coords, charge)
        reference = scf.RHF(mol)
        reference.chkfile = None
        reference.conv_tol = 1e-11
        reference.kernel()
        self.assertTrue(reference.converged)
        return reference

    def test_h2_bonding_and_reference_energy(self):
        atoms = np.array([1, 1])
        coords = np.array([[0., 0., -.7], [0., 0., .7]])
        result = run_rhf(atoms, coords)
        self.assertTrue(result['converged'])
        self.assertAlmostEqual(result['energy'], -1.11671432506255, places=8)
        self.assertGreater(np.prod(result['C'][:, result['homo_idx']]), 0.)
        reference = self.reference(atoms, coords)
        np.testing.assert_allclose(result['evals'], reference.mo_energy, atol=1e-7)

    def test_water_symmetry_and_rigid_rotation(self):
        result = run_rhf(self.water_atoms, self.water_coords)
        theta = .63
        rotation = np.array([[np.cos(theta), 0., -np.sin(theta)], [0., 1., 0.],
                             [np.sin(theta), 0., np.cos(theta)]])
        rotated = run_rhf(self.water_atoms, self.water_coords @ rotation)
        self.assertTrue(result['converged'] and rotated['converged'])
        self.assertEqual(result['n_basis'], 7)
        self.assertAlmostEqual(result['energy'], rotated['energy'], places=9)
        np.testing.assert_allclose(result['evals'], rotated['evals'], atol=1e-7)
        py_index = next(i for i, label in enumerate(result['ao_labels']) if '2py' in label)
        self.assertGreater(abs(result['C'][py_index, result['homo_idx']]), .999)
        reference = self.reference(self.water_atoms, self.water_coords)
        self.assertAlmostEqual(result['energy'], reference.e_tot, places=8)

    def test_teaching_molecules_match_independent_scf_driver(self):
        gaps = []
        for smiles in ['O', 'CCO', 'COC', 'C=C', 'C=CC=C', 'C=CC=CC=C']:
            with self.subTest(smiles=smiles):
                geometry = geometry_from_smiles(smiles)
                result = run_rhf(geometry['atoms'], geometry['coords'])
                reference = self.reference(geometry['atoms'], geometry['coords'])
                self.assertTrue(result['converged'])
                self.assertLess(abs(result['energy'] - reference.e_tot), 2e-8)
                np.testing.assert_allclose(result['evals'], reference.mo_energy, atol=5e-6)
                if smiles in ['C=C', 'C=CC=C', 'C=CC=CC=C']:
                    gaps.append(result['evals'][result['lumo_idx']] - result['evals'][result['homo_idx']])
        self.assertTrue(gaps[0] > gaps[1] > gaps[2])

    def test_density_mixing_conserves_electrons_and_common_limit(self):
        geometry = geometry_from_smiles('O')
        counts, energies = [], []
        for mix in [1., .5, .1]:
            result = run_rhf(geometry['atoms'], geometry['coords'], mix=mix,
                             max_iter=300, use_diis=False)
            self.assertTrue(result['converged'])
            counts.append(result['iterations'])
            energies.append(result['energy'])
            for step in result['history']:
                self.assertAlmostEqual(step['electron_count'], 10., places=9)
        self.assertTrue(counts[0] < counts[1] < counts[2])
        self.assertLess(max(energies) - min(energies), 2e-8)

    def test_failed_scf_is_not_reported_as_converged(self):
        result = run_rhf(self.water_atoms, self.water_coords, max_iter=1, mix=.1, use_diis=False)
        self.assertFalse(result['converged'])
        self.assertEqual(result['iterations'], 1)
        reference = scf.RHF(build_molecule(self.water_atoms, self.water_coords))
        self.assertAlmostEqual(result['energy'], reference.energy_tot(dm=result['P']), places=10)
        self.assertAlmostEqual(result['history'][-1]['electron_count'], 10., places=9)

    def test_geometry_is_reproducible_and_charge_is_preserved(self):
        first = geometry_from_smiles('CCO')
        second = geometry_from_smiles('CCO')
        np.testing.assert_allclose(first['coords'], second['coords'], atol=1e-12)
        self.assertEqual(geometry_from_smiles('[NH4+]')['formal_charge'], 1)

    def test_scope_checks_and_no_virtual_orbitals(self):
        with self.assertRaises(ValueError):
            run_rhf(self.water_atoms, self.water_coords, charge=1)
        with self.assertRaises(ValueError):
            run_rhf([17], [[0., 0., 0.]], charge=1)
        with self.assertRaises(ValueError):
            run_rhf([1, 1], [[0., 0., 0.], [0., 0., 0.]])
        with self.assertRaises(ValueError):
            geometry_from_smiles('not a molecule')
        full = run_rhf([1, 1], [[0., 0., -.7], [0., 0., .7]], charge=-2)
        self.assertIsNone(full['lumo_idx'])

    def test_cube_uses_same_basis_and_coefficients(self):
        result = run_rhf(self.water_atoms, self.water_coords)
        cube = orbital_cube(result, result['homo_idx'], grid_size=10)
        lines = cube.splitlines()
        origin = np.array(list(map(float, lines[2].split()[1:])))
        steps = np.array([list(map(float, line.split()[1:])) for line in lines[3:6]])
        self.assertEqual(int(lines[2].split()[0]), 3)
        self.assertEqual([int(line.split()[0]) for line in lines[3:6]], [10, 10, 10])
        values = np.array([float(value) for line in lines[9:] for value in line.split()])
        self.assertEqual(len(values), 1000)
        grid_indices = np.column_stack([v.ravel() for v in np.meshgrid(
            np.arange(10), np.arange(10), np.arange(10), indexing='ij')])
        grid = origin + grid_indices @ steps
        mol = gto.loads(result['mol_dump'])
        expected = mol.eval_gto('GTOval_sph', grid) @ result['C'][:, result['homo_idx']]
        np.testing.assert_allclose(values, expected, atol=3e-6)
        self.assertLess(values.min(), 0.)
        self.assertGreater(values.max(), 0.)


if __name__ == '__main__':
    unittest.main()
