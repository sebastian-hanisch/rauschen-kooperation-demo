"""Kern der Demo (numpy): das wiederholte Gefangenendilemma mit Rauschen als exakte Markov-Kette.

Der Zustand ist das Ergebnis der letzten Runde (x, y) = (Aktion von A, Aktion von B), vier Zustände. A kooperiert in der nächsten Runde mit
`after[(x, y)]`, B mit `after[(y, x)]` (seine Sicht). Rauschen ε vertauscht jede beabsichtigte Aktion unabhängig mit Wahrscheinlichkeit ε;
beide sehen die ausgeführte Aktion. Einheiten (DEMO-PLAYBOOK §1b):

- `executed_cooperation`  P(ausgeführt = C) bei beabsichtigter Kooperationswahrscheinlichkeit p
- `transition_matrix`     4×4-Übergangsmatrix des Paares
- `first_round`           Verteilung über die Zustände nach Runde 1
- `stationary`            Dauerverteilung (nur für ε > 0 eindeutig)
- `finite_payoff`         exakte erwartete mittlere Auszahlung über die ersten `rounds` Runden
- `average_payoff`        langfristig: Dauerverteilung bei ε > 0, sonst Mittel über `horizon` Runden
- `recovery_time`         erwartete Zahl der Runden bis wieder (C,C) gespielt wird, ausgehend von einem Zustand
- `simulate`              eine konkrete Spur"""

import random

import numpy as np

import rkn_constants as C
from rkn_scenario import Memory1, stage_payoff

STATES = ((0, 0), (0, 1), (1, 0), (1, 1))        # (Aktion von A, Aktion von B); 0 = C
STATE_INDEX = {s: i for i, s in enumerate(STATES)}
CC = STATE_INDEX[(0, 0)]


def executed_cooperation(p: float, eps: float) -> float:
    """Wahrscheinlichkeit, dass tatsächlich kooperiert wird: (1 − ε)·p + ε·(1 − p)."""
    return (1.0 - eps) * p + eps * (1.0 - p)


def _view(state: tuple[int, int], own_is_a: bool) -> int:
    """Index in `after` aus der Sicht des Spielers: 0 = (C,C), 1 = (C,D), 2 = (D,C), 3 = (D,D)."""
    x, y = state if own_is_a else (state[1], state[0])
    return x * 2 + y


def transition_matrix(a: Memory1, b: Memory1, eps: float) -> np.ndarray:
    """P[i, j] = Wahrscheinlichkeit, dass nach Zustand i der Zustand j gespielt wird."""
    mat = np.zeros((4, 4))
    for i, state in enumerate(STATES):
        ca = executed_cooperation(a.after[_view(state, True)], eps)
        cb = executed_cooperation(b.after[_view(state, False)], eps)
        for j, (x, y) in enumerate(STATES):
            mat[i, j] = (ca if x == C.COOPERATE else 1.0 - ca) * (cb if y == C.COOPERATE else 1.0 - cb)
    return mat


def first_round(a: Memory1, b: Memory1, eps: float) -> np.ndarray:
    ca, cb = executed_cooperation(a.first, eps), executed_cooperation(b.first, eps)
    return np.array([(ca if x == C.COOPERATE else 1.0 - ca) * (cb if y == C.COOPERATE else 1.0 - cb) for x, y in STATES])


def stationary(mat: np.ndarray) -> np.ndarray:
    """Dauerverteilung π mit π P = π, Σπ = 1. Eindeutig, wenn die Kette irreduzibel ist (ε in (0, 1) bei Wahrscheinlichkeiten in (0, 1))."""
    n = mat.shape[0]
    system = np.vstack([mat.T - np.eye(n), np.ones((1, n))])
    rhs = np.zeros(n + 1)
    rhs[-1] = 1.0
    sol, *_ = np.linalg.lstsq(system, rhs, rcond=None)
    return sol


def payoff_vector(a_side: bool = True) -> np.ndarray:
    """Auszahlung je Zustand für A (a_side) bzw. B."""
    return np.array([stage_payoff(x, y) if a_side else stage_payoff(y, x) for x, y in STATES])


def finite_payoff(a: Memory1, b: Memory1, eps: float, rounds: int) -> tuple[float, float]:
    """Exakte erwartete mittlere Auszahlung je Runde über die ersten `rounds` Runden (Verteilung Runde für Runde fortgeschrieben)."""
    if rounds < 1:
        raise ValueError("mindestens eine Runde")
    mat = transition_matrix(a, b, eps)
    dist = first_round(a, b, eps)
    total = np.zeros(4)
    for _ in range(rounds):
        total += dist
        dist = dist @ mat
    total /= rounds
    return float(total @ payoff_vector(True)), float(total @ payoff_vector(False))


def average_payoff(a: Memory1, b: Memory1, eps: float, horizon: int = C.HORIZON) -> tuple[float, float]:
    """Langfristige mittlere Auszahlung je Runde für (A, B).

    ε > 0 und die Kette ist irreduzibel: Dauerverteilung (gilt nach etwa 1/ε Runden). Sonst, etwa bei ε = 0 mit festen Strategien,
    gibt es keine eindeutige Dauerverteilung: dann der Mittelwert der ersten `horizon` Runden."""
    mat = transition_matrix(a, b, eps)
    if eps > 0.0 and bool((mat > 1e-12).all()):
        pi = stationary(mat)
        return float(pi @ payoff_vector(True)), float(pi @ payoff_vector(False))
    return finite_payoff(a, b, eps, horizon)


def recovery_time(a: Memory1, b: Memory1, eps: float, start: tuple[int, int]) -> float:
    """Erwartete Zahl der Runden bis zum nächsten (C,C), ausgehend vom Ergebnis `start` der letzten Runde; unendlich, wenn nie.

    Erreichbarkeit wird zuerst per Graph geprüft; erst dann gilt (I − Q) t = 1 auf den übrigen Zuständen."""
    mat = transition_matrix(a, b, eps)
    s0 = STATE_INDEX[start]
    if s0 == CC:
        return 0.0
    edges = {i: [j for j in range(4) if mat[i, j] > 1e-12] for i in range(4)}
    # Vorwärts erreichbar vom Start aus (ohne über CC hinaus zu gehen): dort wird die Zeit gemessen
    seen, stack = {s0}, [s0]
    while stack:
        i = stack.pop()
        for j in edges[i]:
            if j != CC and j not in seen:
                seen.add(j)
                stack.append(j)
    # Gibt es von dort aus keinen Weg nach CC, oder bleibt eine Falle ohne Weg nach CC erreichbar, ist die erwartete Zeit unendlich.
    can_reach = {CC}
    changed = True
    while changed:
        changed = False
        for i in range(4):
            if i not in can_reach and any(j in can_reach for j in edges[i]):
                can_reach.add(i)
                changed = True
    if any(i not in can_reach for i in seen):
        return float("inf")
    order = sorted(seen)
    q = mat[np.ix_(order, order)]
    t = np.linalg.solve(np.eye(len(order)) - q, np.ones(len(order)))
    return float(t[order.index(s0)])


def simulate(a: Memory1, b: Memory1, eps: float, rounds: int, rng: random.Random, forced_round: int | None = None) -> list[tuple[int, int]]:
    """Eine Spur aus `rounds` Runden. In `forced_round` (1-basiert) wird die Aktion von A erzwungen verwechselt (zusätzlich zum Rauschen)."""
    out: list[tuple[int, int]] = []
    last = None
    for t in range(1, rounds + 1):
        if last is None:
            pa, pb = a.first, b.first
        else:
            pa, pb = a.after[_view(last, True)], b.after[_view(last, False)]
        x = C.COOPERATE if rng.random() < pa else C.DEFECT
        y = C.COOPERATE if rng.random() < pb else C.DEFECT
        if eps > 0.0 and rng.random() < eps:
            x = 1 - x
        if eps > 0.0 and rng.random() < eps:
            y = 1 - y
        if t == forced_round:
            x = 1 - x
        out.append((x, y))
        last = (x, y)
    return out
