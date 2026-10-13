"""Small, explicit closed-shell RHF solver using genuine PySCF integrals.

All coordinates, integrals, energies, and cube-grid coordinates use atomic units.
PySCF supplies the STO-3G basis, libcint integrals, and AO evaluation; the SCF
iteration is kept here so students can inspect density mixing and convergence.
"""
from __future__ import annotations

import io

import numpy as np
from scipy import linalg
from rdkit import Chem
from rdkit.Chem import AllChem
from pyscf import gto, lib
from pyscf.scf.diis import CDIIS

BOHR_ANGSTROM = 0.52917721092
SUPPORTED_ATOMS = {1, 6, 7, 8}
MAX_BASIS_FUNCTIONS = 64
# Tiny teaching systems are faster with one integral-library thread per request.
lib.num_threads(1)


def geometry_from_smiles(smiles: str) -> dict:
    """Return a reproducible MMFF/UFF geometry without shared temporary files."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Virheellinen SMILES-merkkijono.")
    mol = Chem.AddHs(mol)
    atoms = np.array([atom.GetAtomicNum() for atom in mol.GetAtoms()], dtype=int)
    if not len(atoms) or not set(atoms).issubset(SUPPORTED_ATOMS):
        raise ValueError("Tämä opetusmoduuli tukee alkuaineita H, C, N ja O.")
    if sum(1 if z == 1 else 5 for z in atoms) > MAX_BASIS_FUNCTIONS:
        raise ValueError("Valitse pienempi molekyyli: enintään 64 STO-3G-kantafunktiota.")
    params = AllChem.ETKDG()
    params.randomSeed = 17
    if AllChem.EmbedMolecule(mol, params) != 0:
        raise ValueError("Molekyylin 3D-rakenteen luominen epäonnistui.")
    if AllChem.MMFFHasAllMoleculeParams(mol):
        method = "MMFF"
        status = AllChem.MMFFOptimizeMolecule(mol, maxIters=1000)
    elif AllChem.UFFHasAllMoleculeParams(mol):
        method = "UFF"
        status = AllChem.UFFOptimizeMolecule(mol, maxIters=1000)
    else:
        raise ValueError("Molekyylille ei löytynyt geometrian voimakenttäparametreja.")
    if status != 0:
        raise ValueError("Geometrian minimointi ei suppene; kokeile pienempää molekyyliä.")
    coords = np.asarray(mol.GetConformer().GetPositions(), dtype=float)
    return {
        "atoms": atoms,
        "coords": coords / BOHR_ANGSTROM,
        "xyz": Chem.MolToXYZBlock(mol),
        "formal_charge": int(Chem.GetFormalCharge(mol)),
        "geometry_method": method,
    }


def build_molecule(atoms, coords, charge=0):
    """Build the complete STO-3G basis and validate the closed-shell scope."""
    atoms = np.asarray(atoms)
    coords = np.asarray(coords, dtype=float)
    if atoms.ndim != 1 or not len(atoms) or coords.shape != (len(atoms), 3):
        raise ValueError("Atomien ja koordinaattien mitat eivät täsmää.")
    if not np.all(np.isfinite(coords)) or not np.all(atoms == atoms.astype(int)):
        raise ValueError("Atomien järjestyslukujen ja koordinaattien tulee olla kelvollisia.")
    atoms = atoms.astype(int)
    if not set(atoms).issubset(SUPPORTED_ATOMS):
        raise ValueError("Tämä opetusmoduuli tukee alkuaineita H, C, N ja O.")
    if int(charge) != charge:
        raise ValueError("Molekyylin varauksen tulee olla kokonaisluku.")
    nelec = int(atoms.sum()) - int(charge)
    if nelec <= 0 or nelec % 2:
        raise ValueError(
            "RHF-moduuli vaatii positiivisen, parillisen elektronimäärän "
            "ja olettaa suljetun kuoren singletin. Radikaaleille tarvitaan avoimen kuoren menetelmä."
        )
    nao = sum(1 if z == 1 else 5 for z in atoms)
    if nao > MAX_BASIS_FUNCTIONS:
        raise ValueError("Valitse pienempi molekyyli: enintään 64 STO-3G-kantafunktiota.")
    if nelec > 2 * nao:
        raise ValueError("Elektroneja on enemmän kuin valittu kantajoukko voi sisältää.")
    if len(atoms) > 1:
        distances = np.linalg.norm(coords[:, None] - coords[None, :], axis=-1)
        np.fill_diagonal(distances, np.inf)
        if distances.min() < 1e-6:
            raise ValueError("Kaksi atomiydintä ei voi olla samassa pisteessä.")
    return gto.M(
        atom=[(int(z), coord) for z, coord in zip(atoms, coords)],
        unit="Bohr", basis="sto-3g", charge=int(charge), spin=0, verbose=0,
    )


def fock_matrix(core, eri, density):
    coulomb = np.einsum("kl,ijkl->ij", density, eri, optimize=True)
    exchange = np.einsum("kl,ikjl->ij", density, eri, optimize=True)
    return core + coulomb - 0.5 * exchange


def electronic_energy(core, fock, density):
    return float(0.5 * np.einsum("ij,ji", density, core + fock))


def run_rhf(atoms, coords, charge=0, max_iter=100, mix=0.5, use_diis=True):
    """Run an explicit, number-conserving SCF with energy and density checks.

    Results retain the last mixed density and its physical Fock eigenvectors.
    `converged` is true only when energy, fixed-point density, and commutator
    criteria all pass. Failed runs remain available as iteration demonstrations.
    """
    if not 0.0 < mix <= 1.0:
        raise ValueError("Tiheyden sekoituksen tulee olla välillä 0 < mix ≤ 1.")
    if int(max_iter) != max_iter or not 1 <= max_iter <= 500:
        raise ValueError("Iteraatioiden määrän tulee olla kokonaisluku väliltä 1–500.")
    mol = build_molecule(atoms, coords, charge)
    overlap = mol.intor("int1e_ovlp")
    core = mol.intor("int1e_kin") + mol.intor("int1e_nuc")
    eri = mol.intor("int2e", aosym="s1")
    nuclear = float(mol.energy_nuc())
    nocc = mol.nelectron // 2
    w, u = linalg.eigh(overlap)
    if w.min() < 1e-8:
        raise ValueError("Kantajoukko on lähes lineaarisesti riippuva; tarkista geometria.")
    orth = (u * (1 / np.sqrt(w))) @ u.T
    sqrt_overlap = (u * np.sqrt(w)) @ u.T

    def occupied_density(coeffs):
        occ = coeffs[:, :nocc]
        return 2 * occ @ occ.T

    def density_rms(delta):
        return float(np.sqrt(np.mean((sqrt_overlap @ delta @ sqrt_overlap) ** 2)))

    _, coeffs = linalg.eigh(core, overlap)
    density = occupied_density(coeffs)
    fock = fock_matrix(core, eri, density)
    previous_energy = electronic_energy(core, fock, density) + nuclear
    history = [{"cycle": 0, "energy": previous_energy, "delta_energy": None,
                "density_rms": None, "residual_rms": None,
                "electron_count": float(np.einsum("ij,ji", density, overlap))}]
    diis = CDIIS(Corth=orth) if use_diis else None
    if diis is not None:
        diis.incore = True
        diis.verbose = 0
        diis.space = 8
    converged = False
    energy_tol, density_tol, residual_tol = 1e-9, 1e-7, 1e-7
    for cycle in range(1, int(max_iter) + 1):
        fock = fock_matrix(core, eri, density)
        iter_fock = diis.update(overlap, density, fock) if diis is not None else fock
        _, coeffs = linalg.eigh(iter_fock, overlap)
        target = occupied_density(coeffs)
        density = (1 - mix) * density + mix * target
        fock = fock_matrix(core, eri, density)
        energy = electronic_energy(core, fock, density) + nuclear
        orbital_energies, coeffs = linalg.eigh(fock, overlap)
        physical_target = occupied_density(coeffs)
        fixed_point = density_rms(physical_target - density)
        commutator = orth.T @ (fock @ density @ overlap - overlap @ density @ fock) @ orth
        residual = float(np.sqrt(np.mean(commutator ** 2)))
        delta_energy = energy - previous_energy
        electron_count = float(np.einsum("ij,ji", density, overlap))
        if not np.isfinite(energy) or not np.all(np.isfinite(density)):
            raise ValueError("SCF muuttui numeerisesti epävakaaksi; kokeile pienempää mix-arvoa.")
        history.append({"cycle": cycle, "energy": energy, "delta_energy": delta_energy,
                        "density_rms": fixed_point, "residual_rms": residual,
                        "electron_count": electron_count})
        previous_energy = energy
        if abs(delta_energy) < energy_tol and fixed_point < density_tol and residual < residual_tol:
            converged = True
            break
    return {
        "converged": converged, "iterations": cycle, "energy": energy,
        "electronic_energy": energy - nuclear, "nuclear_energy": nuclear,
        "evals": orbital_energies, "C": coeffs, "P": density,
        "N_elec": mol.nelectron, "n_basis": mol.nao_nr(),
        "atoms": np.asarray(atoms, dtype=int), "coords": np.asarray(coords, dtype=float),
        "charge": int(charge), "history": history, "mol_dump": mol.dumps(),
        "ao_labels": mol.ao_labels(), "homo_idx": nocc - 1,
        "lumo_idx": nocc if nocc < mol.nao_nr() else None,
        "thresholds": {"energy": energy_tol, "density": density_tol, "residual": residual_tol},
    }


def orbital_cube(result, orbital_index, grid_size=50, margin=4.0):
    """Evaluate the same normalized AO basis used in SCF and return a cube string."""
    if not 0 <= orbital_index < result["n_basis"]:
        raise ValueError("Virheellinen orbitaalin indeksi.")
    mol = gto.loads(result["mol_dump"])
    coords = mol.atom_coords()
    lower = coords.min(axis=0) - margin
    upper = coords.max(axis=0) + margin
    step = (upper - lower) / (grid_size - 1)
    axes = [np.linspace(lo, hi, grid_size) for lo, hi in zip(lower, upper)]
    grid = np.column_stack([v.ravel() for v in np.meshgrid(*axes, indexing="ij")])
    mo_coeffs = result["C"][:, orbital_index]
    values = np.empty(len(grid))
    for start in range(0, len(grid), 20000):
        stop = min(start + 20000, len(grid))
        values[start:stop] = mol.eval_gto("GTOval_sph", grid[start:stop]) @ mo_coeffs
    stream = io.StringIO()
    stream.write("Turku CompChem: RHF/STO-3G molecular orbital\n")
    stream.write("Coordinates and steps in bohr; signed wavefunction amplitude\n")
    stream.write(f"{mol.natm:5d} {lower[0]:12.6f} {lower[1]:12.6f} {lower[2]:12.6f}\n")
    for axis in range(3):
        vector = np.zeros(3); vector[axis] = step[axis]
        stream.write(f"{grid_size:5d} {vector[0]:12.6f} {vector[1]:12.6f} {vector[2]:12.6f}\n")
    for atom, coord in zip(mol.atom_charges(), coords):
        stream.write(f"{atom:5d} {float(atom):12.6f} {coord[0]:12.6f} {coord[1]:12.6f} {coord[2]:12.6f}\n")
    for start in range(0, len(values), 6):
        stream.write(" ".join(f"{value:13.5E}" for value in values[start:start + 6]) + "\n")
    return stream.getvalue()
