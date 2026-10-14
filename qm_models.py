"""Opetusmallien numeeriset laskut; atomiyksiköt ellei muuta ilmoiteta."""
import math

import numpy as np
from numba import njit
from scipy import linalg
from scipy.fft import dst, idst
from scipy.integrate import simpson
from scipy.optimize import brentq, minimize_scalar
from scipy.signal import find_peaks
from scipy.special import eval_genlaguerre, gammaln


def spatial_grid(length, requested_spacing):
    if length <= 0 or requested_spacing <= 0:
        raise ValueError("Laskenta-alueen leveyden ja hilavälin tulee olla positiivisia.")
    intervals = max(8, int(np.ceil(length / requested_spacing)))
    if intervals > 6000:
        raise ValueError("Hila on liian suuri. Kasvata hilaväliä tai pienennä laskenta-aluetta.")
    return np.linspace(-length/2, length/2, intervals + 1)


def solve_schrodinger_1d(x, potential, mass, nstates):
    """Kolmidiagonaalinen differenssi-Hamiltoni ja tarkat Dirichlet-reunat."""
    x, potential = np.asarray(x), np.asarray(potential)
    if mass <= 0 or len(x) < 4 or potential.shape != x.shape:
        raise ValueError("Tarkista massa, hila ja potentiaali.")
    dx = x[1] - x[0]
    if not np.allclose(np.diff(x), dx) or not np.all(np.isfinite(potential)):
        raise ValueError("Hilan tulee olla tasavälinen ja potentiaalin äärellinen.")
    kinetic = 1 / (2 * mass * dx**2)
    count = min(int(nstates), len(x)-2)
    energies, inner = linalg.eigh_tridiagonal(
        2*kinetic + potential[1:-1], np.full(len(x)-3, -kinetic),
        select="i", select_range=(0, count-1), lapack_driver="stebz", tol=1e-12,
    )
    states = np.zeros((len(x), count))
    states[1:-1] = inner / np.sqrt(dx)
    return energies, states


def solve_morse_analytical(x, depth, alpha, mass, requested_states):
    if min(depth, alpha, mass) <= 0:
        raise ValueError("Morse-parametrien ja massan tulee olla positiivisia.")
    lam = np.sqrt(2 * mass * depth) / alpha
    count = max(0, min(int(requested_states), int(np.ceil(lam - .5))))
    values, states = [], []
    z = 2 * lam * np.exp(-alpha * np.asarray(x))
    for n in range(count):
        q = lam - n - .5
        if q <= 16*np.finfo(float).eps * max(lam, 1.):
            continue
        normalizer = .5*(np.log(alpha * 2*q) + gammaln(n+1) - gammaln(2*lam-n))
        psi = np.zeros(len(x))
        mask = (z > 0) & (z < max(3000., 8*lam+8*n))
        zz = z[mask]
        polynomial = eval_genlaguerre(n, 2*q, zz)
        nonzero = polynomial != 0
        local = np.zeros(len(zz))
        local[nonzero] = np.sign(polynomial[nonzero]) * np.exp(
            normalizer + q*np.log(zz[nonzero]) - zz[nonzero]/2 + np.log(np.abs(polynomial[nonzero])))
        psi[mask] = local
        values.append(alpha*np.sqrt(2*depth/mass)*(n+.5) - alpha**2/(2*mass)*(n+.5)**2)
        states.append(psi)
    return np.asarray(values), np.column_stack(states) if states else np.zeros((len(x), 0))


def state_moments(x, psi):
    """Jatkuvan sini-interpolantin paikka- ja liikemäärämomentit.

    Sini-interpolantti täyttää laatikon reunaehdot. Liikemäärän neliö saadaan
    sen analyyttisistä aaltoluvuista, joten peräkkäisiä derivointieroja vältetään.
    Tiheämpi kvadratuurihila tarkentaa sijaintimomentit muuttamatta tilaa.
    """
    x = np.asarray(x)
    dx = x[1] - x[0]
    interior = np.asarray(psi)[1:-1]
    norm = float(dx * np.sum(np.abs(interior)**2))
    if norm <= 0:
        raise ValueError("Aaltofunktion normi on nolla.")
    coefficients = dst(interior/np.sqrt(norm), type=1, norm="ortho") * np.sqrt(dx)
    n = np.arange(1, len(coefficients)+1)
    length = x[-1]-x[0]
    p2 = float(np.sum(np.abs(coefficients)**2 * (np.pi*n/length)**2))
    fine_count = max(4*(len(x)-1)-1, 1023)
    fine_dx = length/(fine_count+1)
    padded = np.zeros(fine_count)
    padded[:len(coefficients)] = coefficients / np.sqrt(fine_dx)
    fine_psi = idst(padded, type=1, norm="ortho")
    fine_x = x[0] + np.arange(1, fine_count+1)*fine_dx
    probability = fine_psi**2 * fine_dx
    mean_x = float(np.sum(probability*fine_x))
    mean_x2 = float(np.sum(probability*fine_x**2))
    variance = mean_x2 - mean_x**2
    if variance < -1e-10:
        raise ValueError("Paikan varianssi on negatiivinen; tarkista numeerinen tarkkuus.")
    return mean_x, mean_x2, 0., p2


# Clementi–Raimondi (1963), taulukko I: Z_eff = n*zeta.
# https://doi.org/10.1063/1.1733573
CLEMENTI_ZEFF = {
    1: {'1s': 1.}, 2: {'1s': 1.6875},
    3: {'1s': 2.6906, '2s': 1.2792}, 4: {'1s': 3.6848, '2s': 1.9120},
    5: {'1s': 4.6795, '2s': 2.5762, '2p': 2.4214},
    6: {'1s': 5.6727, '2s': 3.2166, '2p': 3.1358},
    7: {'1s': 6.6651, '2s': 3.8474, '2p': 3.8340},
    8: {'1s': 7.6579, '2s': 4.4916, '2p': 4.4532},
    9: {'1s': 8.6501, '2s': 5.1276, '2p': 5.1000},
    10: {'1s': 9.6421, '2s': 5.7584, '2p': 5.7584},
    11: {'1s': 10.6259, '2s': 6.5714, '2p': 6.8018, '3s': 2.5074},
    12: {'1s': 11.6089, '2s': 7.3920, '2p': 7.8258, '3s': 3.3075},
    13: {'1s': 12.5910, '2s': 8.2136, '2p': 8.9634, '3s': 4.1172, '3p': 4.0656},
    14: {'1s': 13.5745, '2s': 9.0200, '2p': 9.9450, '3s': 4.9032, '3p': 4.2852},
    15: {'1s': 14.5578, '2s': 9.8250, '2p': 10.9612, '3s': 5.6418, '3p': 4.8864},
    16: {'1s': 15.5409, '2s': 10.6288, '2p': 11.9770, '3s': 6.3669, '3p': 5.4819},
    17: {'1s': 16.5239, '2s': 11.4304, '2p': 12.9932, '3s': 7.0683, '3p': 6.1161},
    18: {'1s': 17.5075, '2s': 12.2304, '2p': 14.0082, '3s': 7.7568, '3p': 6.7641},
}
ELEMENTS = {i+1: symbol for i, symbol in enumerate(
    ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar'])}


def radial_orbitals(atomic_number, orthogonal=True):
    """Kiinteä integraatioalue; kuvaajan rajaus ei muuta funktioita."""
    r = np.r_[0., np.geomspace(1e-6, 60., 8000)]
    raw = {}
    for label, zeff in CLEMENTI_ZEFF[int(atomic_number)].items():
        n = int(label[0]); zeta = zeff/n
        normalizer = np.exp((n+.5)*np.log(2*zeta)-.5*gammaln(2*n+1))
        raw[label] = normalizer * r**(n-1)*np.exp(-zeta*r)
    if not orthogonal:
        return r, raw
    result = {}
    for kind in ['s', 'p', 'd']:
        previous = []
        for label in sorted(name for name in raw if name[1] == kind):
            function = raw[label].copy()
            for old in previous:
                function -= simpson(function*old*r**2, x=r)*old
            norm = simpson(function**2*r**2, x=r)
            if norm <= 0:
                raise ValueError("Radiaalisen funktion ortogonalisointi epäonnistui.")
            function /= np.sqrt(norm)
            result[label] = function
            previous.append(function)
    return r, result


def barrier_potential(x, shape, count, height, width, separation):
    positions = [0.] if count == 1 else [-separation/2, separation/2] if count == 2 else [-separation, 0., separation]
    value = np.zeros_like(x)
    for centre in positions:
        u = (x-centre)/(width/2)
        if shape == "Suorakulmainen":
            value += np.where(np.abs(u) <= 1., height, 0.)
        elif shape == "Gaussin käyrä":
            value += height*np.exp(-u*u)
        elif shape == "Lorentz-muoto":
            value += height/(1+u*u)
        else:
            raise ValueError("Tuntematon esteen muoto.")
    return value


@njit(cache=True)
def transmission(energies, potential, dx, mass):
    """Stabiili sirontamatriisien ketjutus, vapaa tulo- ja lähtöalue V=0.

    Jokainen solu on vakioeste, jonka sin(q*dx)/q-raja käsitellään myös q=0:ssa.
    Ketjutus käyttää sironta-amplitudeja, joten paksujen esteiden kasvavia
    siirtomatriisieksponentteja ei muodosteta.
    """
    output = np.zeros(len(energies))
    for j in range(len(energies)):
        energy = energies[j]
        if energy <= 0:
            continue
        k0 = np.sqrt(2*mass*energy)
        total_r, total_t = 0.+0.j, 1.+0.j
        for index in range(len(potential)-1, -1, -1):
            q2 = 2*mass*(energy-potential[index])
            q = np.sqrt(q2+0.j)
            sinc = dx+0.j if abs(q*dx) < 1e-10 else np.sin(q*dx)/q
            denominator = np.cos(q*dx)-1j*(k0*k0+q2)/(2*k0)*sinc
            t = 1/denominator
            r = -1j*(k0*k0-q2)/(2*k0)*sinc/denominator
            coupling = 1-r*total_r
            total_t = t*total_t/coupling
            total_r = r+t*t*total_r/coupling
        value = total_t.real**2+total_t.imag**2
        output[j] = min(1., max(0., value))
    return output


def resolve_resonances(energies, values, potential, dx, mass):
    """Tarkenna yleiskuvasta löytyvät resonanssihuiput ja niiden puoliarvoleveys."""
    candidates, _ = find_peaks(values, height=1e-7)
    candidates = [i for i in candidates if energies[i] < np.max(potential)][:12]
    result = []
    evaluate = lambda energy: float(transmission(np.array([energy]), potential, dx, mass)[0])
    for index in candidates:
        left, right = float(energies[index-1]), float(energies[index+1])
        peak = minimize_scalar(lambda energy: -evaluate(energy), bounds=(left, right),
                               method="bounded", options={"xatol": 1e-12})
        centre, height = float(peak.x), evaluate(float(peak.x))
        if height < values[index] or height < 1e-6:
            continue
        half = height/2
        try:
            lower = brentq(lambda e: evaluate(e)-half, left, centre, xtol=1e-12)
            upper = brentq(lambda e: evaluate(e)-half, centre, right, xtol=1e-12)
            width = upper-lower
        except ValueError:
            width = right-left
        result.append({"energy": centre, "height": height, "width": float(width)})
    return result


VOIP = {1: [-13.6], 6: [-21.4, -11.4, -11.4, -11.4],
        7: [-26., -13.4, -13.4, -13.4], 8: [-32.3, -14.8, -14.8, -14.8]}


def valence_eht(atoms, coords, constant=1.75):
    """EHT valenssi-2s/2p-kannassa, normalisoitu STO-3G-sovitus; energiat eV."""
    from pyscf import gto, lib
    lib.num_threads(1)
    atoms = np.asarray(atoms, dtype=int)
    if not set(atoms).issubset(VOIP):
        raise ValueError("Walsh-malli tukee alkuaineita H, C, N ja O.")
    if sum(1 if z == 1 else 5 for z in atoms) > 64:
        raise ValueError("Valitse pienempi molekyyli Walsh-tarkasteluun.")
    mol = gto.M(atom=[(int(z), xyz) for z, xyz in zip(atoms, coords)], unit="Bohr",
                basis="sto-3g", spin=int(atoms.sum()) % 2, verbose=0)
    keep, onsite = [], []
    for atom_index, z in enumerate(atoms):
        start, end = mol.aoslice_by_atom()[atom_index, 2:4]
        indices = list(range(int(start), int(end)))
        keep.extend(indices if z == 1 else indices[1:])
        onsite.extend(VOIP[int(z)])
    overlap = mol.intor("int1e_ovlp")[np.ix_(keep, keep)]
    norm = np.sqrt(np.diag(overlap))
    overlap = overlap / norm[:, None] / norm[None, :]
    onsite = np.asarray(onsite)
    hamiltonian = constant * overlap * (onsite[:, None]+onsite[None, :])/2
    np.fill_diagonal(hamiltonian, onsite)
    if np.linalg.eigvalsh(overlap).min() < 1e-8:
        raise ValueError("Valenssikanta on lähes lineaarisesti riippuva tässä geometriassa.")
    energies, coeffs = linalg.eigh(hamiltonian, overlap)
    return energies, coeffs, overlap


def calc_1d_monatomic(alpha, beta, n_k=500, a=1.0):
    k = np.linspace(-np.pi / a, np.pi / a, n_k)
    E = alpha + 2 * beta * np.cos(k * a)
    k_dos = np.linspace(-np.pi / a, np.pi / a, 50000)
    E_dos = alpha + 2 * beta * np.cos(k_dos * a)
    hist, bin_edges = np.histogram(E_dos, bins=200, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    return (k, E, bin_centers, hist)

def calc_1d_diatomic(alpha1, alpha2, beta1, beta2, n_k=500, a=1.0):
    k = np.linspace(-np.pi / a, np.pi / a, n_k)
    delta_alpha = (alpha1 - alpha2) / 2
    mean_alpha = (alpha1 + alpha2) / 2
    off_diag_sq = beta1 ** 2 + beta2 ** 2 + 2 * beta1 * beta2 * np.cos(k * a)
    E_upper = mean_alpha + np.sqrt(delta_alpha ** 2 + off_diag_sq)
    E_lower = mean_alpha - np.sqrt(delta_alpha ** 2 + off_diag_sq)
    k_dos = np.linspace(-np.pi / a, np.pi / a, 50000)
    off_diag_sq_dos = beta1 ** 2 + beta2 ** 2 + 2 * beta1 * beta2 * np.cos(k_dos * a)
    E_upper_dos = mean_alpha + np.sqrt(delta_alpha ** 2 + off_diag_sq_dos)
    E_lower_dos = mean_alpha - np.sqrt(delta_alpha ** 2 + off_diag_sq_dos)
    E_dos_all = np.concatenate([E_lower_dos, E_upper_dos])
    hist, bin_edges = np.histogram(E_dos_all, bins=300, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    return (k, E_lower, E_upper, bin_centers, hist)

def calc_2d_square(alpha, beta, n_k=200, a=1.0):
    k_Gamma_X_x = np.linspace(0, np.pi / a, n_k)
    k_Gamma_X_y = np.zeros(n_k)
    k_X_M_x = np.ones(n_k) * np.pi / a
    k_X_M_y = np.linspace(0, np.pi / a, n_k)
    k_M_Gamma_x = np.linspace(np.pi / a, 0, n_k)
    k_M_Gamma_y = np.linspace(np.pi / a, 0, n_k)
    kx_path = np.concatenate([k_Gamma_X_x, k_X_M_x, k_M_Gamma_x])
    ky_path = np.concatenate([k_Gamma_X_y, k_X_M_y, k_M_Gamma_y])
    path_len = np.zeros(len(kx_path))
    for i in range(1, len(kx_path)):
        dk = np.sqrt((kx_path[i] - kx_path[i - 1]) ** 2 + (ky_path[i] - ky_path[i - 1]) ** 2)
        path_len[i] = path_len[i - 1] + dk
    E_path = alpha + 2 * beta * (np.cos(kx_path * a) + np.cos(ky_path * a))
    ticks = [0, path_len[n_k - 1], path_len[2 * n_k - 1], path_len[-1]]
    tick_labels = ['Gamma', 'X', 'M', 'Gamma']
    kx_grid = np.linspace(-np.pi / a, np.pi / a, 500)
    ky_grid = np.linspace(-np.pi / a, np.pi / a, 500)
    KX, KY = np.meshgrid(kx_grid, ky_grid)
    E_dos = alpha + 2 * beta * (np.cos(KX * a) + np.cos(KY * a))
    hist, bin_edges = np.histogram(E_dos.flatten(), bins=200, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    return (path_len, E_path, ticks, tick_labels, bin_centers, hist)
