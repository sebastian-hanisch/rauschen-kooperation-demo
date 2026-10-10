"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

COOPERATE, DEFECT = 0, 1

# Auszahlungen je Runde (Axelrod), fest.
T, R, P, S = 5.0, 3.0, 1.0, 0.0

EPS_MIN, EPS_MAX, DEFAULT_EPS, EPS_STEP = 0.0, 0.20, 0.05, 0.01
Q_MIN, Q_MAX, DEFAULT_Q, Q_STEP = 0.05, 0.95, 0.33, 0.01
ROUNDS_MIN, ROUNDS_MAX, DEFAULT_ROUNDS = 12, 60, 30
SEED_MAX, DEFAULT_SEED = 999999, 20263
FORCED_ROUND = 3                              # in der Spur verwechselt Spediteur A in dieser Runde (1-basiert) seine Aktion

HORIZON = 1000                                # Runden für den Mittelwert bei ε = 0 (dort gibt es keine eindeutige Dauerverteilung)
EPS_CURVE = tuple(round(0.005 * i, 3) for i in range(0, 41))   # 0 bis 0,20 in Schritten von 0,005

STRATEGY_KEYS = ("ALLC", "ALLD", "TFT", "GTFT", "PAVLOV")
DEFAULT_A, DEFAULT_B = "TFT", "TFT"

COLOR_COOP = "#2F6B65"
COLOR_DEFECT = "#B5483A"
COLOR_LINES = {"ALLC": "#9aa5b1", "ALLD": "#B5483A", "TFT": "#4c78a8", "GTFT": "#2F6B65", "PAVLOV": "#e08a2c"}
COLOR_OTHER = "rgba(150,150,150,0.55)"

PRESETS = {
    "Tit-for-Tat gegen sich selbst, 5 % Fehler": {"a": "TFT", "b": "TFT", "eps": 0.05, "q": DEFAULT_Q},
    "Großzügiges Tit-for-Tat gegen sich selbst": {"a": "GTFT", "b": "GTFT", "eps": 0.05, "q": DEFAULT_Q},
    "Pavlov gegen sich selbst": {"a": "PAVLOV", "b": "PAVLOV", "eps": 0.05, "q": DEFAULT_Q},
    "Pavlov gegen Immer-Defektieren": {"a": "PAVLOV", "b": "ALLD", "eps": 0.05, "q": DEFAULT_Q},
    "Ohne Rauschen: ein Fehler, ewiges Echo": {"a": "TFT", "b": "TFT", "eps": 0.0, "q": DEFAULT_Q},
}
PRESET_HELP = {
    "Tit-for-Tat gegen sich selbst, 5 % Fehler": "Eine Verwechslung löst bei zwei Tit-for-Tat ein Echo aus, das erst ein zweiter Fehler beendet.",
    "Großzügiges Tit-for-Tat gegen sich selbst": "Mit Vergebung q = 0,33 endet das Echo im Mittel nach etwa drei Runden.",
    "Pavlov gegen sich selbst": "Pavlov korrigiert einen Fehler nach zwei Runden von selbst.",
    "Pavlov gegen Immer-Defektieren": "Die Schwäche: Pavlov kooperiert abwechselnd mit einem Dauer-Defektierer und zahlt dafür.",
    "Ohne Rauschen: ein Fehler, ewiges Echo": "Kein weiteres Rauschen: Nach der einen Verwechslung in Runde 3 geht das Echo für immer weiter, es gibt nichts, was es beendet.",
}
