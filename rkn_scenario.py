"""Szenario: das Gefangenendilemma 5/3/1/0 und die fünf Strategien als Memory-1-Tabellen.

Eine Memory-1-Strategie ist durch die Wahrscheinlichkeit, in der ersten Runde zu kooperieren, und durch je eine Kooperationswahrscheinlichkeit
nach den vier möglichen Ergebnissen der letzten Runde gegeben (aus Sicht des Spielers: eigene Aktion, Aktion des Gegners):
(C,C), (C,D), (D,C), (D,D). Alle fünf Strategien sind reaktiv oder Pavlov, also vollständig so beschreibbar."""

from dataclasses import dataclass

import rkn_constants as C


def stage_payoff(own: int, other: int) -> float:
    """Auszahlung einer Runde für die eigene Aktion gegen die des anderen (0 = C, 1 = D)."""
    if own == C.COOPERATE:
        return C.R if other == C.COOPERATE else C.S
    return C.T if other == C.COOPERATE else C.P


@dataclass(frozen=True)
class Memory1:
    key: str
    label: str
    first: float                                  # P(kooperieren) in Runde 1
    after: tuple[float, float, float, float]      # P(kooperieren) nach (C,C), (C,D), (D,C), (D,D) aus eigener Sicht
    description: str


def make_strategies(q: float = C.DEFAULT_Q) -> dict[str, Memory1]:
    """Die fünf Strategien; `q` ist die Vergebungswahrscheinlichkeit des großzügigen Tit-for-Tat."""
    if not 0.0 <= q <= 1.0:
        raise ValueError("q muss eine Wahrscheinlichkeit sein")
    items = [
        Memory1("ALLC", "Immer kooperieren", 1.0, (1.0, 1.0, 1.0, 1.0),
                "Bietet jede Woche eine Rückladung an, egal was passiert."),
        Memory1("ALLD", "Immer defektieren", 0.0, (0.0, 0.0, 0.0, 0.0),
                "Nutzt nur, bietet nie an."),
        Memory1("TFT", "Tit-for-Tat", 1.0, (1.0, 0.0, 1.0, 0.0),
                "Beginnt mit Kooperation und spielt danach die letzte Aktion des Gegners nach."),
        Memory1("GTFT", "Großzügiges Tit-for-Tat", 1.0, (1.0, q, 1.0, q),
                f"Wie Tit-for-Tat, vergibt aber eine Defektion des Gegners mit Wahrscheinlichkeit q (hier {q:.2f}).".replace(".", ",")),
        Memory1("PAVLOV", "Pavlov (Win-Stay-Lose-Shift)", 1.0, (1.0, 0.0, 0.0, 1.0),
                "Kooperiert, wenn beide in der letzten Runde dasselbe getan haben, sonst defektiert es: bleibt nach einem Gewinn, wechselt nach einem Verlust."),
    ]
    return {s.key: s for s in items}
