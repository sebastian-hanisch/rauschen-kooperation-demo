"""Kennzahlen, Verdikt-Logik und Auswertungen über den Kern (die Komposition der Einheiten aus rkn_algorithm)."""

import random
from dataclasses import dataclass

import rkn_algorithm as A
import rkn_constants as C
from rkn_scenario import make_strategies

FINITE_HORIZON = 200                 # Spiellänge wie im Axelrod-Turnier-Stück der Linie


def fmt(x: float, digits: int = 2) -> str:
    """Zahl mit deutschem Dezimalkomma; unendlich als „nie“."""
    if x == float("inf"):
        return "nie"
    return f"{x:.{digits}f}".replace(".", ",")


@dataclass(frozen=True)
class Settings:
    a: str = C.DEFAULT_A
    b: str = C.DEFAULT_B
    eps: float = C.DEFAULT_EPS
    q: float = C.DEFAULT_Q
    rounds: int = C.DEFAULT_ROUNDS      # Länge der gezeigten Spur
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    long_a: float                        # langfristige mittlere Auszahlung (Dauerverteilung bzw. 1000 Runden bei ε = 0)
    long_b: float
    finite_a: float                      # exakt über die ersten 200 Runden
    finite_b: float
    recovery: float                      # erwartete Runden bis wieder (C,C), nachdem A in einer Runde verwechselt hat; inf = nie
    coop_share: float                    # Anteil der Runden mit beidseitiger Kooperation (langfristig)
    trace: tuple[tuple[int, int], ...]
    trace_recovery_round: int | None     # erste Runde nach der erzwungenen Verwechslung mit (C,C); None, wenn in der Spur nicht erreicht


def analyse(settings: Settings) -> Analysis:
    strategies = make_strategies(settings.q)
    a, b = strategies[settings.a], strategies[settings.b]
    long_a, long_b = A.average_payoff(a, b, settings.eps)
    fin_a, fin_b = A.finite_payoff(a, b, settings.eps, FINITE_HORIZON)
    mat = A.transition_matrix(a, b, settings.eps)
    if settings.eps > 0.0 and bool((mat > 1e-12).all()):
        coop = float(A.stationary(mat)[A.CC])
    else:
        dist = A.first_round(a, b, settings.eps)
        acc = 0.0
        for _ in range(C.HORIZON):
            acc += dist[A.CC]
            dist = dist @ mat
        coop = acc / C.HORIZON
    trace = A.simulate(a, b, settings.eps, settings.rounds, random.Random(settings.seed), forced_round=C.FORCED_ROUND)
    back = next((t for t in range(C.FORCED_ROUND + 1, len(trace) + 1) if trace[t - 1] == (C.COOPERATE, C.COOPERATE)), None)
    return Analysis(long_a, long_b, fin_a, fin_b, A.recovery_time(a, b, settings.eps, (C.DEFECT, C.COOPERATE)), coop, tuple(trace), back)


def eps_curves(q: float = C.DEFAULT_Q, grid=C.EPS_CURVE) -> dict:
    """Langfristige Auszahlung je ε für jede Strategie gegen sich selbst, dazu die ersten 200 Runden für Tit-for-Tat und Pavlov."""
    strategies = make_strategies(q)
    out = {"eps": list(grid)}
    for key in C.STRATEGY_KEYS:
        s = strategies[key]
        out[key] = [A.average_payoff(s, s, e)[0] for e in grid]
    out["TFT_200"] = [A.finite_payoff(strategies["TFT"], strategies["TFT"], e, FINITE_HORIZON)[0] for e in grid]
    return out


def recovery_table(eps: float, q: float = C.DEFAULT_Q) -> dict[str, float]:
    """Erwartete Erholungszeit je Strategie gegen sich selbst nach einer einzelnen Verwechslung von A (Immer-Defektieren kooperiert nie, hat also nichts zu erholen)."""
    strategies = make_strategies(q)
    return {k: A.recovery_time(strategies[k], strategies[k], eps, (C.DEFECT, C.COOPERATE)) for k in C.STRATEGY_KEYS if k != "ALLD"}


def cross_table(eps: float, q: float = C.DEFAULT_Q) -> list[list[float]]:
    """Langfristige Auszahlung der Zeile gegen die Spalte."""
    strategies = make_strategies(q)
    return [[A.average_payoff(strategies[r], strategies[c], eps)[0] for c in C.STRATEGY_KEYS] for r in C.STRATEGY_KEYS]


def action_string(actions) -> str:
    return " ".join("C" if a == C.COOPERATE else "D" for a in actions)


def strategy_overview(q: float = C.DEFAULT_Q, rounds: int = 12) -> list[dict]:
    """Je Strategie: Beschreibung, Kooperationswahrscheinlichkeiten nach den vier Ergebnissen und die Spur gegen sich selbst, wenn A in Runde 3
    seine Aktion verwechselt (ohne weiteres Rauschen, fester Seed bei den Zufalls-Strategien)."""
    strategies = make_strategies(q)
    rows = []
    for key in C.STRATEGY_KEYS:
        s = strategies[key]
        trace = A.simulate(s, s, 0.0, rounds, random.Random(1), forced_round=C.FORCED_ROUND)
        rows.append({
            "key": key, "label": s.label, "description": s.description,
            "after": s.after,
            "trace_a": action_string([x for x, _ in trace]),
            "trace_b": action_string([y for _, y in trace]),
        })
    return rows


def verdict(an: Analysis, settings: Settings) -> tuple[str, str]:
    """(Stufe, Satz) für die Kernfrage: wie schnell kehrt die Kooperation nach einer Verwechslung zurück?"""
    strategies = make_strategies(settings.q)
    la, lb = strategies[settings.a].label, strategies[settings.b].label
    pair = f"{la} gegen {lb}"
    if an.recovery == float("inf"):
        return "warning", (f"{pair}: Nach einer Verwechslung kehren beide **nie** zur gegenseitigen Kooperation zurück. Ohne einen zweiten Fehler "
                           f"läuft das Echo ewig; ihre langfristige Auszahlung liegt bei {fmt(an.long_a)}.")
    if an.recovery <= 3.5:
        return "success", (f"{pair}: Die Kooperation ist im Mittel nach **{fmt(an.recovery, 1)} Runden** wieder da. Langfristig erzielt A "
                           f"{fmt(an.long_a)} Punkte je Runde.")
    return "warning", (f"{pair}: Die Kooperation braucht im Mittel **{fmt(an.recovery, 1)} Runden**, um zurückzukehren. Langfristig erzielt A "
                       f"{fmt(an.long_a)} Punkte je Runde.")
