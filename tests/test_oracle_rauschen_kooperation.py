"""Orakel-Tests rauschen-kooperation-demo: der Kern wird gegen UNABHÄNGIGE Rechenwege geprüft (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §2).

Die Simulation unten ist bewusst direkt aus den Strategietabellen geschrieben und benutzt weder `transition_matrix` noch `simulate` des Kerns.

1. Dauerverteilung (lineares System) gegen Potenziteration der Übergangsmatrix und gegen die Zeitverteilung einer langen Simulation.
2. Erwartete Auszahlung über n Runden (exakte Fortschreibung) gegen den Mittelwert vieler simulierter Spiele.
3. Erwartete Erholungszeit (lineares System auf den Zuständen) gegen den Mittelwert simulierter Wartezeiten.
4. Geschlossene Formeln: Tit-for-Tat-Paar gleichverteilt, großzügiges Tit-for-Tat erholt sich ohne Rauschen in 1/q Runden."""

import itertools
import random

import numpy as np
import pytest

import rkn_algorithm as A
import rkn_constants as C
from rkn_scenario import make_strategies, stage_payoff

STRATS = make_strategies(1 / 3)


def sim_round(a, b, last, eps, rng):
    """Eine Runde direkt aus den Tabellen: Absicht, dann Rauschen, dann das Ergebnis."""
    if last is None:
        pa, pb = a.first, b.first
    else:
        x, y = last
        pa, pb = a.after[2 * x + y], b.after[2 * y + x]
    ia = 0 if rng.random() < pa else 1
    ib = 0 if rng.random() < pb else 1
    if rng.random() < eps:
        ia = 1 - ia
    if rng.random() < eps:
        ib = 1 - ib
    return ia, ib


def sim_average(a, b, eps, rounds, reps, seed):
    rng = random.Random(seed)
    tot_a = tot_b = 0.0
    for _ in range(reps):
        last = None
        for _ in range(rounds):
            last = sim_round(a, b, last, eps, rng)
            tot_a += stage_payoff(last[0], last[1])
            tot_b += stage_payoff(last[1], last[0])
    n = reps * rounds
    return tot_a / n, tot_b / n


def sim_recovery(a, b, eps, start, reps, seed, cap=20000):
    rng = random.Random(seed)
    total = 0
    for _ in range(reps):
        last, t = start, 0
        while t < cap:
            last = sim_round(a, b, last, eps, rng)
            t += 1
            if last == (0, 0):
                break
        total += t
    return total / reps


PAIRS = [("TFT", "TFT"), ("GTFT", "GTFT"), ("PAVLOV", "PAVLOV"), ("PAVLOV", "ALLD"), ("TFT", "PAVLOV"), ("GTFT", "ALLD"), ("ALLC", "PAVLOV")]


@pytest.mark.parametrize("ka,kb", PAIRS)
def test_stationary_distribution_matches_power_iteration(ka, kb):
    mat = A.transition_matrix(STRATS[ka], STRATS[kb], 0.07)
    pi = A.stationary(mat)
    dist = np.full(4, 0.25)
    for _ in range(5000):
        dist = dist @ mat
    assert pi == pytest.approx(dist, abs=1e-9)
    assert pi.sum() == pytest.approx(1.0) and (pi >= -1e-12).all()


@pytest.mark.parametrize("ka,kb", PAIRS)
def test_long_run_payoff_matches_a_long_simulation(ka, kb):
    exact = A.average_payoff(STRATS[ka], STRATS[kb], 0.1)
    got = sim_average(STRATS[ka], STRATS[kb], 0.1, rounds=2000, reps=40, seed=3)
    assert got[0] == pytest.approx(exact[0], abs=0.06), (ka, kb)
    assert got[1] == pytest.approx(exact[1], abs=0.06), (ka, kb)


@pytest.mark.parametrize("ka,kb", PAIRS)
@pytest.mark.parametrize("eps,rounds", [(0.0, 30), (0.05, 30), (0.15, 12)])
def test_finite_payoff_matches_many_simulated_games(ka, kb, eps, rounds):
    exact = A.finite_payoff(STRATS[ka], STRATS[kb], eps, rounds)
    got = sim_average(STRATS[ka], STRATS[kb], eps, rounds=rounds, reps=4000, seed=11)
    assert got[0] == pytest.approx(exact[0], abs=0.07), (ka, kb, eps)
    assert got[1] == pytest.approx(exact[1], abs=0.07), (ka, kb, eps)


@pytest.mark.parametrize("key,eps", [("TFT", 0.1), ("TFT", 0.2), ("GTFT", 0.05), ("PAVLOV", 0.1), ("ALLC", 0.1)])
def test_recovery_time_matches_simulated_waiting_times(key, eps):
    exact = A.recovery_time(STRATS[key], STRATS[key], eps, (1, 0))
    got = sim_recovery(STRATS[key], STRATS[key], eps, (1, 0), reps=6000, seed=5)
    assert got == pytest.approx(exact, rel=0.08), (key, eps, exact, got)


@pytest.mark.parametrize("q", [0.1, 0.25, 0.5, 0.9])
def test_gtft_without_noise_recovers_in_one_over_q_rounds(q):
    s = make_strategies(q)["GTFT"]
    assert A.recovery_time(s, s, 0.0, (1, 0)) == pytest.approx(1.0 / q)


def test_tft_pair_is_uniform_for_every_noise_and_pays_the_average_of_the_four_outcomes():
    for eps in np.linspace(0.005, 0.5, 25):
        pi = A.stationary(A.transition_matrix(STRATS["TFT"], STRATS["TFT"], float(eps)))
        assert pi == pytest.approx([0.25] * 4, abs=1e-9)


def test_swapping_the_players_swaps_the_payoffs():
    for ka, kb in itertools.permutations(C.STRATEGY_KEYS, 2):
        ab = A.average_payoff(STRATS[ka], STRATS[kb], 0.08)
        ba = A.average_payoff(STRATS[kb], STRATS[ka], 0.08)
        assert ab[0] == pytest.approx(ba[1], abs=1e-9) and ab[1] == pytest.approx(ba[0], abs=1e-9), (ka, kb)


def test_payoffs_stay_between_the_stage_game_extremes():
    for ka, kb in itertools.product(C.STRATEGY_KEYS, repeat=2):
        for eps in (0.0, 0.03, 0.2):
            a, b = A.average_payoff(STRATS[ka], STRATS[kb], eps)
            assert C.S - 1e-9 <= a <= C.T + 1e-9 and C.S - 1e-9 <= b <= C.T + 1e-9
            assert a + b <= 2 * C.R + 1e-9 or a + b <= C.T + C.S + 1e-9      # Gesamtgewinn höchstens max(2R, T+S)
