"""Jede Zahl aus README und App wird hier über die echten Auswertungsfunktionen nachgerechnet (DEMO-PLAYBOOK §4)."""

import pytest

import rkn_algorithm as A
import rkn_constants as C
import rkn_evaluation as E
from rkn_scenario import make_strategies

S = make_strategies(C.DEFAULT_Q)
DC = (1, 0)


def test_tft_pair_pays_2_25_for_every_positive_noise_and_3_without():
    for eps in (0.01, 0.05, 0.1, 0.2):
        assert A.average_payoff(S["TFT"], S["TFT"], eps)[0] == pytest.approx(2.25)
    assert A.average_payoff(S["TFT"], S["TFT"], 0.0)[0] == pytest.approx(3.0)


def test_tft_over_200_rounds_at_one_percent_noise():
    assert A.finite_payoff(S["TFT"], S["TFT"], 0.01, 200)[0] == pytest.approx(2.46, abs=0.01)
    assert A.finite_payoff(S["TFT"], S["TFT"], 0.01, 20)[0] == pytest.approx(2.90, abs=0.01)


def test_symmetric_long_run_payoffs_at_five_percent():
    vals = {k: A.average_payoff(S[k], S[k], 0.05)[0] for k in C.STRATEGY_KEYS}
    assert vals["ALLC"] == pytest.approx(2.947, abs=0.002)
    assert vals["ALLD"] == pytest.approx(1.147, abs=0.002)
    assert vals["TFT"] == pytest.approx(2.250, abs=0.001)
    assert vals["GTFT"] == pytest.approx(2.858, abs=0.002)
    assert vals["PAVLOV"] == pytest.approx(2.776, abs=0.002)


def test_recovery_times():
    assert A.recovery_time(S["PAVLOV"], S["PAVLOV"], 0.0, DC) == pytest.approx(2.0)
    assert A.recovery_time(S["GTFT"], S["GTFT"], 0.0, DC) == pytest.approx(1 / 0.33)
    assert A.recovery_time(S["TFT"], S["TFT"], 0.0, DC) == float("inf")
    assert A.recovery_time(S["TFT"], S["TFT"], 0.01, DC) == pytest.approx(150.5, abs=0.1)
    assert A.recovery_time(S["TFT"], S["TFT"], 0.05, DC) == pytest.approx(30.5, abs=0.1)
    assert A.recovery_time(S["PAVLOV"], S["PAVLOV"], 0.05, DC) == pytest.approx(2.33, abs=0.01)
    assert A.recovery_time(S["GTFT"], S["GTFT"], 0.05, DC) == pytest.approx(3.14, abs=0.01)


def test_the_exploiter_cost_at_five_percent():
    cross = E.cross_table(0.05, C.DEFAULT_Q)
    k = list(C.STRATEGY_KEYS)

    def cell(row, col):
        return cross[k.index(row)][k.index(col)]

    assert cell("TFT", "ALLD") == pytest.approx(1.100, abs=0.002)
    assert cell("GTFT", "ALLD") == pytest.approx(0.804, abs=0.002)
    assert cell("PAVLOV", "ALLD") == pytest.approx(0.675, abs=0.002)
    assert cell("PAVLOV", "ALLC") == pytest.approx(3.825, abs=0.002)      # Pavlov beutet Immer-Kooperieren aus
    assert cell("ALLC", "PAVLOV") == pytest.approx(1.575, abs=0.002)


def test_generosity_trade_off_between_a_gtft_pair_and_exploitation():
    pair, vs_alld = [], []
    for q in (0.05, 1 / 3, 0.8):
        s = make_strategies(q)
        pair.append(A.average_payoff(s["GTFT"], s["GTFT"], 0.05)[0])
        vs_alld.append(A.average_payoff(s["GTFT"], s["ALLD"], 0.05)[0])
    assert pair == pytest.approx([2.536, 2.859, 2.935], abs=0.002)
    assert vs_alld == pytest.approx([1.055, 0.801, 0.382], abs=0.002)
    assert pair[0] < pair[1] < pair[2] and vs_alld[0] > vs_alld[1] > vs_alld[2]


def test_strategy_overview_traces_by_hand():
    rows = {r["key"]: r for r in E.strategy_overview()}
    assert rows["TFT"]["trace_a"] == "C C D C D C D C D C D C"
    assert rows["TFT"]["trace_b"] == "C C C D C D C D C D C D"
    assert rows["PAVLOV"]["trace_a"] == "C C D D C C C C C C C C"
    assert rows["PAVLOV"]["trace_b"] == "C C C D C C C C C C C C"
    assert rows["ALLD"]["trace_a"] == "D D C D D D D D D D D D"      # die erzwungene Verwechslung gilt für jede Strategie
    assert rows["ALLC"]["trace_a"] == "C C D C C C C C C C C C"      # A verwechselt in Runde 3, danach sofort wieder C
    assert len(rows) == 5 and all(r["description"] for r in rows.values())


def test_verdict_levels():
    no_noise = E.Settings(eps=0.0)
    level, text = E.verdict(E.analyse(no_noise), no_noise)
    assert level == "warning" and "nie" in text
    pav = E.Settings(a="PAVLOV", b="PAVLOV")
    level, text = E.verdict(E.analyse(pav), pav)
    assert level == "success" and "Runden" in text


def test_analysis_trace_shows_the_forced_error():
    an = E.analyse(E.Settings(eps=0.0))
    assert an.trace[C.FORCED_ROUND - 1] == (C.DEFECT, C.COOPERATE)
    assert an.trace_recovery_round is None            # Tit-for-Tat ohne Rauschen kehrt nie zurück
    pav = E.analyse(E.Settings(a="PAVLOV", b="PAVLOV", eps=0.0))
    assert pav.trace_recovery_round == C.FORCED_ROUND + 2
