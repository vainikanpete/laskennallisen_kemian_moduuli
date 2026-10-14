"""Opetusmallien fysiikan regressiot; suorita unittest-komennolla."""
import sys
import unittest
from pathlib import Path

import numpy as np
from scipy.integrate import simpson

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qm_models import (CLEMENTI_ZEFF, barrier_potential, calc_1d_diatomic,
                       calc_1d_monatomic, calc_2d_square, radial_orbitals,
                       resolve_resonances, solve_morse_analytical,
                       solve_schrodinger_1d, spatial_grid, state_moments,
                       transmission, valence_eht)
from plot_style import orbital_energy_figure


class OneDimensionalTests(unittest.TestCase):
    def test_box_spectrum_normalization_and_boundary_conditions(self):
        x = spatial_grid(10.13, .025)
        self.assertLessEqual(x[1]-x[0], .025)
        energies, states = solve_schrodinger_1d(x, np.zeros_like(x), 2., 4)
        exact = (np.pi*np.arange(1, 5)/10.13)**2/4
        np.testing.assert_allclose(energies, exact, rtol=1e-4)
        np.testing.assert_array_equal(states[[0, -1]], 0.)
        np.testing.assert_allclose((x[1]-x[0])*states.T@states, np.eye(4), atol=1e-10)

    def test_harmonic_spectrum_and_uncertainty(self):
        x = spatial_grid(10., .01)
        energies, states = solve_schrodinger_1d(x, 5*x*x, 2., 4)
        np.testing.assert_allclose(energies, np.sqrt(5)*(np.arange(4)+.5), atol=.001)
        mean, mean2, momentum, momentum2 = state_moments(x, states[:, 0])
        product = np.sqrt((mean2-mean**2)*momentum2)
        self.assertAlmostEqual(mean, 0., places=9)
        self.assertEqual(momentum, 0.)
        self.assertGreaterEqual(product, .5-1e-9)
        self.assertAlmostEqual(product, .5, places=6)

    def test_morse_threshold_is_not_a_bound_state(self):
        x = np.linspace(-8., 40., 10001)
        energies, states = solve_morse_analytical(x, 3.0625, 1., 2., 12)
        # lambda = 3.5: n=3 is exactly at dissociation and is not normalizable.
        np.testing.assert_allclose(energies, [.8125, 2.0625, 2.8125])
        np.testing.assert_allclose(simpson(states**2, x=x, axis=0), 1., atol=1e-8)
        none, empty = solve_morse_analytical(x, .05, 3., .1, 10)
        self.assertEqual(len(none), 0)
        self.assertEqual(empty.shape, (len(x), 0))

    def test_numerical_morse_approaches_analytical_bound_levels(self):
        errors = []
        for spacing in [.04, .02]:
            x = spatial_grid(16., spacing)
            exact, _ = solve_morse_analytical(x, 5., 1., 2., 3)
            computed, _ = solve_schrodinger_1d(x, 5*np.expm1(-x)**2, 2., 3)
            errors.append(np.max(np.abs(exact-computed)))
        self.assertLess(errors[1], errors[0]/3)
        self.assertLess(errors[1], .001)


class RadialTests(unittest.TestCase):
    def test_all_elements_normalized_and_same_l_orthogonal(self):
        for z in range(1, 19):
            for orthogonal in [False, True]:
                with self.subTest(z=z, orthogonal=orthogonal):
                    r, orbitals = radial_orbitals(z, orthogonal)
                    for label, function in orbitals.items():
                        self.assertAlmostEqual(simpson(r*r*function**2, x=r), 1., places=8)
                        if orthogonal:
                            for other, previous in orbitals.items():
                                if other != label and other[1] == label[1]:
                                    self.assertAlmostEqual(simpson(r*r*function*previous, x=r), 0., places=8)

    def test_hydrogen_radial_probability_and_clementi_parameters(self):
        r, orbitals = radial_orbitals(1)
        function = orbitals['1s']
        np.testing.assert_allclose(function, 2*np.exp(-r), atol=1e-9)
        probability = r*r*function**2
        self.assertEqual(probability[0], 0.)
        self.assertAlmostEqual(r[np.argmax(probability)], 1., places=2)
        self.assertEqual(CLEMENTI_ZEFF[11]['2p'], 6.8018)
        self.assertEqual(CLEMENTI_ZEFF[18]['3s'], 7.7568)
        self.assertEqual(CLEMENTI_ZEFF[18]['3p'], 6.7641)


class ScatteringTests(unittest.TestCase):
    def test_free_motion_and_rectangular_barrier_including_threshold(self):
        energies = np.array([.25, 1., 2., 4., 5., 6., 7.5])
        np.testing.assert_allclose(transmission(energies, np.zeros(300), .01, 1.), 1., atol=1e-12)
        height, width, mass = 5., 1., 1.
        expected = []
        for energy in energies:
            if energy < height:
                factor = np.sinh(np.sqrt(2*mass*(height-energy))*width)**2/(height-energy)
            elif energy > height:
                factor = np.sin(np.sqrt(2*mass*(energy-height))*width)**2/(energy-height)
            else:
                factor = 2*mass*width**2
            expected.append(1/(1+height**2*factor/(4*energy)))
        values = transmission(energies, np.full(100, height), .01, mass)
        np.testing.assert_allclose(values, expected, rtol=1e-11, atol=1e-13)

    def test_thick_barrier_stays_finite(self):
        values = transmission(np.array([.1, 1., 14., 15., 20.]), np.full(2000, 15.), .005, 20.)
        self.assertTrue(np.all(np.isfinite(values)))
        self.assertTrue(np.all((values >= 0) & (values <= 1)))
        self.assertLess(values[0], 1e-100)

    def test_double_barrier_refinement_recovers_full_transmission(self):
        dx = .01
        x = -12+(np.arange(2400)+.5)*dx
        potential = barrier_potential(x, 'Suorakulmainen', 2, 5., 1., 3.)
        energies = np.linspace(.01, 7.5, 800)
        values = transmission(energies, potential, dx, 1.)
        peaks = resolve_resonances(energies, values, potential, dx, 1.)
        self.assertGreaterEqual(len(peaks), 2)
        for peak in peaks:
            self.assertGreater(peak['height'], .999999)
            self.assertGreater(peak['width'], 0.)
        self.assertLess(peaks[0]['width'], energies[1]-energies[0])


class ValenceAndBandTests(unittest.TestCase):
    def test_valence_basis_size_normalization_and_rotation(self):
        atoms = [8, 1, 1]
        coords = np.array([[0., 0., 0.], [1.4, 0., 1.1], [-1.4, 0., 1.1]])
        energies, coefficients, overlap = valence_eht(atoms, coords)
        self.assertEqual(len(energies), 6)  # O: 2s+3*2p; two H: 1s.
        np.testing.assert_allclose(np.diag(overlap), 1., atol=1e-12)
        np.testing.assert_allclose(coefficients.T@overlap@coefficients, np.eye(6), atol=1e-12)
        angle = .71
        rotation = np.array([[np.cos(angle), -np.sin(angle), 0.],
                             [np.sin(angle), np.cos(angle), 0.], [0., 0., 1.]])
        rotated, _, _ = valence_eht(atoms, coords@rotation)
        np.testing.assert_allclose(energies, rotated, atol=1e-10)
        carbon_dioxide, _, _ = valence_eht([8, 6, 8], [[-2.2, 0., 0.], [0., 0., 0.], [2.2, 0., 0.]])
        self.assertEqual(len(carbon_dioxide), 12)

    def test_band_gaps_match_alternating_chain_solution(self):
        for a1, a2, b1, b2 in [(-5., -5., -2., -2.), (-5., -5., -2., -1.5), (-5., -7., -2., -2.)]:
            _, lower, upper, _, _ = calc_1d_diatomic(a1, a2, b1, b2)
            expected = 2*np.sqrt(((a1-a2)/2)**2+(abs(b1)-abs(b2))**2)
            self.assertAlmostEqual(upper[0]-lower[0], expected, places=12)
        _, band, _, _ = calc_1d_monatomic(-5., -2.)
        self.assertAlmostEqual(band[0], -1., places=12)
        self.assertLess(abs(band.min()+9.), .0001)

    def test_square_lattice_singularity_is_at_band_centre(self):
        _, band, _, _, energy, dos = calc_2d_square(-5., -2.)
        centre = np.abs(energy+5) < .15
        edges = (energy < -12) | (energy > 2)
        self.assertGreater(dos[centre].mean(), dos[edges].mean()*2)
        self.assertLess(abs(energy[np.argmax(dos)]+5), .15)
        self.assertAlmostEqual(band.min(), -13., places=8)
        self.assertAlmostEqual(band.max(), 3., places=8)

    def test_energy_diagram_points_keep_orbital_identity(self):
        result = {'homo_idx': 4, 'lumo_idx': 5, 'n_basis': 7,
                  'evals': np.array([-20., -1.2, -.6, -.5, -.4, .6, .8])}
        figure = orbital_energy_figure(result, 5)
        selected = next(trace for trace in figure.data if trace.name == 'Valittu orbitaali')
        self.assertEqual(selected.customdata[0][0], 5)
        self.assertEqual(selected.customdata[0][2], 0)
        self.assertEqual(selected.x[0], 6)
        self.assertAlmostEqual(selected.y[0], .6)
        all_levels = orbital_energy_figure(result, 0, include_core=True)
        indices = [int(data[0]) for trace in all_levels.data for data in trace.customdata]
        self.assertEqual(sorted(indices), list(range(7)))


if __name__ == '__main__':
    unittest.main()
