"""Mini-Instanz-Tests je Einheit (DEMO-PLAYBOOK §1b): alles von Hand gerechnet, Auszahlungen 5/3/1/0."""

import random

import numpy as np
import pytest

import rkn_algorithm as A
import rkn_constants as C
from rkn_scenario import Memory1, make_strategies, stage_payoff

S = make_strategies(1 / 3)
CC, CD, DC, DD = (0, 0), (0, 1), (1, 0), (1, 1)


def test_stage_payoffs():
    assert stage_payoff(0, 0) == 3 and stage_payoff(0, 1) == 0 and stage_payoff(1, 0) == 5 and stage_payoff(1, 1) == 1


def test_strategy_tables_and_validation():
    assert S["TFT"].after == (1.0, 0.0, 1.0, 0.0)
    assert S["PAVLOV"].after == (1.0, 0.0, 0.0, 1.0)
    assert S["GTFT"].after == (1.0, 1 / 3, 1.0, 1 / 3)
    assert all(s.description for s in S.values())
    with pytest.raises(ValueError):
        make_strategies(1.5)


def test_executed_cooperation():
    assert A.executed_cooperation(1.0, 0.1) == pytest.approx(0.9)
    assert A.executed_cooperation(0.0, 0.1) == pytest.approx(0.1)
    assert A.executed_cooperation(0.5, 0.3) == pytest.approx(0.5)
    assert A.executed_cooperation(1.0, 0.0) == 1.0


def test_transition_rows_sum_to_one_and_tft_by_hand():
    mat = A.transition_matrix(S["TFT"], S["TFT"], 0.0)
    assert np.allclose(mat.sum(axis=1), 1.0)
    # aus (C,C) bleibt es (C,C); aus (C,D) wird (D,C); aus (D,C) wird (C,D); aus (D,D) bleibt (D,D)
    assert mat[A.STATE_INDEX[CC], A.STATE_INDEX[CC]] == 1.0
    assert mat[A.STATE_INDEX[CD], A.STATE_INDEX[DC]] == 1.0
    assert mat[A.STATE_INDEX[DC], A.STATE_INDEX[CD]] == 1.0
    assert mat[A.STATE_INDEX[DD], A.STATE_INDEX[DD]] == 1.0


def test_pavlov_transitions_by_hand():
    mat = A.transition_matrix(S["PAVLOV"], S["PAVLOV"], 0.0)
    assert mat[A.STATE_INDEX[DC], A.STATE_INDEX[DD]] == 1.0       # (D,C): beide wechseln auf D
    assert mat[A.STATE_INDEX[DD], A.STATE_INDEX[CC]] == 1.0       # (D,D): beide wechseln auf C
    assert mat[A.STATE_INDEX[CD], A.STATE_INDEX[DD]] == 1.0


def test_noise_spreads_the_transition_by_the_expected_amounts():
    mat = A.transition_matrix(S["TFT"], S["TFT"], 0.1)
    # aus (C,C): jeder bleibt mit 0,9 bei C ⇒ (C,C) 0,81 ; (C,D) 0,09 ; (D,C) 0,09 ; (D,D) 0,01
    assert mat[0] == pytest.approx([0.81, 0.09, 0.09, 0.01])


def test_first_round_distribution():
    assert A.first_round(S["TFT"], S["TFT"], 0.0) == pytest.approx([1, 0, 0, 0])
    assert A.first_round(S["ALLD"], S["ALLC"], 0.0) == pytest.approx([0, 0, 1, 0])
    assert A.first_round(S["TFT"], S["TFT"], 0.1) == pytest.approx([0.81, 0.09, 0.09, 0.01])


def test_tft_pair_has_the_uniform_stationary_distribution_for_every_noise():
    for eps in (0.01, 0.05, 0.2, 0.5):
        pi = A.stationary(A.transition_matrix(S["TFT"], S["TFT"], eps))
        assert pi == pytest.approx([0.25] * 4, abs=1e-9), eps
        assert A.average_payoff(S["TFT"], S["TFT"], eps)[0] == pytest.approx((C.T + C.R + C.P + C.S) / 4)


def test_average_payoff_without_noise_uses_the_horizon():
    assert A.average_payoff(S["TFT"], S["TFT"], 0.0) == pytest.approx((3.0, 3.0))
    assert A.average_payoff(S["ALLD"], S["ALLC"], 0.0) == pytest.approx((5.0, 0.0))
    assert A.average_payoff(S["ALLD"], S["ALLD"], 0.0) == pytest.approx((1.0, 1.0))


def test_finite_payoff_by_hand_tft_against_alld():
    # ohne Rauschen: Runde 1 (C,D): 0 und 5; danach (D,D): 1 und 1. Über 4 Runden: (0 + 3)/4 und (5 + 3)/4
    a, b = A.finite_payoff(S["TFT"], S["ALLD"], 0.0, 4)
    assert a == pytest.approx(0.75) and b == pytest.approx(2.0)
    with pytest.raises(ValueError):
        A.finite_payoff(S["TFT"], S["ALLD"], 0.0, 0)


def test_finite_payoff_approaches_the_stationary_payoff():
    long_run = A.average_payoff(S["TFT"], S["TFT"], 0.05)[0]
    assert abs(A.finite_payoff(S["TFT"], S["TFT"], 0.05, 20000)[0] - long_run) < 0.01
    assert A.finite_payoff(S["TFT"], S["TFT"], 0.05, 20)[0] > long_run + 0.2     # am Anfang noch nahe an 3


def test_recovery_time_by_hand():
    # A hat verwechselt: Zustand (D,C).
    assert A.recovery_time(S["ALLC"], S["ALLC"], 0.0, DC) == pytest.approx(1.0)        # ALLC kooperiert sofort wieder
    assert A.recovery_time(S["PAVLOV"], S["PAVLOV"], 0.0, DC) == pytest.approx(2.0)    # (D,C) -> (D,D) -> (C,C)
    assert A.recovery_time(S["GTFT"], S["GTFT"], 0.0, DC) == pytest.approx(3.0)        # 1/q mit q = 1/3
    assert A.recovery_time(S["TFT"], S["TFT"], 0.0, DC) == float("inf")                # das Echo (C,D),(D,C),... endet nie
    assert A.recovery_time(S["TFT"], S["TFT"], 0.1, CC) == 0.0
    assert A.recovery_time(S["ALLD"], S["ALLD"], 0.0, DC) == float("inf")              # (D,D) für immer


def test_recovery_time_of_tft_with_noise_is_finite_and_shrinks_with_noise():
    t1 = A.recovery_time(S["TFT"], S["TFT"], 0.01, DC)
    t5 = A.recovery_time(S["TFT"], S["TFT"], 0.05, DC)
    assert t1 > t5 > 5.0 and t1 < 1000


def test_simulate_forces_the_error_in_the_given_round():
    trace = A.simulate(S["TFT"], S["TFT"], 0.0, 8, random.Random(1), forced_round=3)
    # CC, CC, (A verwechselt) DC, dann Echo: B spiegelt D, A spiegelt C ...
    assert trace == [CC, CC, DC, CD, DC, CD, DC, CD]


def test_simulate_pavlov_corrects_the_forced_error_in_two_rounds():
    trace = A.simulate(S["PAVLOV"], S["PAVLOV"], 0.0, 7, random.Random(1), forced_round=3)
    assert trace == [CC, CC, DC, DD, CC, CC, CC]


def test_simulate_without_noise_or_error_is_deterministic():
    assert A.simulate(S["TFT"], S["ALLD"], 0.0, 4, random.Random(5)) == [CD, DD, DD, DD]


def test_memory1_is_a_frozen_dataclass():
    s = Memory1("X", "x", 1.0, (1.0, 1.0, 1.0, 1.0), "")
    with pytest.raises(Exception):
        s.first = 0.0
