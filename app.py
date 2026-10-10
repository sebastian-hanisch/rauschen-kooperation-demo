"""Fehler und Vergebung: Rauschen, großzügiges Tit-for-Tat und Pavlov - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Drittes Stück der Wiederholte-Spiele-Linie: Was passiert mit der Kooperation, wenn Aktionen verwechselt werden? Exakt als Markov-Kette über die vier
Ergebnisse der letzten Runde: Dauerverteilung, erwartete Erholungszeit, Auszahlung über das Rauschen.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import rkn_constants as C
import rkn_evaluation as E
from rkn_evaluation import FINITE_HORIZON, Settings, fmt
from rkn_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from rkn_scenario import make_strategies
from rkn_visualization import build_cross, build_eps_curves, build_recovery, build_trace

st.set_page_config(page_title="Fehler und Vergebung: Rauschen, Vergebung und Pavlov – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return E.analyse(settings)


@st.cache_data(show_spinner=False)
def _curves(q):
    return E.eps_curves(q)


@st.cache_data(show_spinner=False)
def _recovery(eps, q):
    return E.recovery_table(eps, q)


@st.cache_data(show_spinner=False)
def _cross(eps, q):
    return E.cross_table(eps, q)


@st.cache_data(show_spinner=False)
def _overview(q):
    return E.strategy_overview(q)


st.title("🩹 Fehler und Vergebung: Rauschen, großzügiges Tit-for-Tat und Pavlov")
st.markdown(
    """
Zwei Spediteure tauschen jede Woche Rückladungen. Manchmal wird eine Aktion **verwechselt**: eine Rückladung kommt nicht an, ein Auftrag geht
unter. Für Tit-for-Tat ist das fatal, denn ein einzelner Fehler löst ein **Echo** aus: A sieht eine Defektion und vergilt, B sieht die Vergeltung
und vergilt zurück, und so geht es weiter, bis ein zweiter Fehler das Echo zufällig beendet. Diese Demo rechnet das **exakt** (als Markov-Kette
über die vier Ergebnisse der letzten Runde) und zeigt zwei Auswege: **Vergebung** (großzügiges Tit-for-Tat) und **Pavlov**, das einen Fehler nach
zwei Runden selbst korrigiert.

Weiter unten: **❓ Kernfrage**, drei Experimente (**🔬**), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
Vorgänger ist [axelrod-turnier-demo](https://sebastianhanisch-axelrod-turnier-demo.streamlit.app/): dort sah man im Turnier, dass Rauschen die
Rangfolge verändert, hier wird der Mechanismus berechnet.
"""
)

with st.expander("So funktioniert ein Fehler im wiederholten Dilemma", expanded=True):
    st.markdown(
        """
1. **Die Ausführung kann abweichen.** Mit Wahrscheinlichkeit ε wird die beabsichtigte Aktion vertauscht; beide sehen die **ausgeführte** Aktion.
2. **Das Gedächtnis ist eine Runde.** Jede Strategie hier entscheidet nur nach dem Ergebnis der letzten Runde (zwei Aktionen, vier Fälle), also
   ist das Paar eine Markov-Kette mit vier Zuständen: gegenseitige Kooperation, zwei Mal einseitige Defektion, gegenseitige Defektion.
3. **Zwei Zahlen sagen alles:** die **langfristige Auszahlung** (Dauerverteilung der Kette) und die **Erholungszeit** (wie viele Runden es im
   Mittel dauert, bis nach einem Fehler wieder beide kooperieren).
        """
    )

with st.expander("Die fünf Strategien: wer macht was?", expanded=True):
    st.markdown(
        "Jede Strategie entscheidet jede Runde, ob sie **kooperiert (C)** oder **defektiert (D)**, und kennt dafür das Ergebnis der letzten Runde. "
        "Die Spalten **nach (C,C) … (D,D)** geben die Wahrscheinlichkeit an, in der nächsten Runde zu kooperieren, wenn das Ergebnis aus eigener Sicht "
        "(eigene Aktion, Aktion des anderen) so war. Die letzten beiden Spalten zeigen die Spur, wenn zwei gleiche Strategien spielen und A in "
        "Runde 3 seine Aktion verwechselt: das Echo bei Tit-for-Tat, die Korrektur bei Pavlov."
    )
    head = "| Strategie | Verhalten | nach (C,C) | nach (C,D) | nach (D,C) | nach (D,D) | Spur von A | Spur von B |"
    rows_md = [head, "|---|---|---|---|---|---|---|---|"]
    for r in _overview(st.session_state.get("q_slider", C.DEFAULT_Q)):
        probs = " | ".join(fmt(p, 2) for p in r["after"])
        rows_md.append(f"| **{r['label']}** | {r['description']} | {probs} | `{r['trace_a']}` | `{r['trace_b']}` |")
    st.markdown("\n".join(rows_md))
    st.caption("Lesebeispiel: Bei Tit-for-Tat wechseln die beiden Spuren ab Runde 3 dauerhaft zwischen „C D“ und „D C“. Bei Pavlov sind beide nach zwei Runden wieder bei C.")

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
cols = st.columns(len(C.PRESETS))
for col, name in zip(cols, C.PRESETS):
    with col:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    st.markdown("**Strategien**")
    strategies_now = make_strategies(st.session_state.get("q_slider", C.DEFAULT_Q))
    a_key = st.selectbox("Spediteur A", C.STRATEGY_KEYS, key="a_select", format_func=lambda k: strategies_now[k].label,
                         help="Die Strategie von A. In der Spur verwechselt A in Runde 3 seine Aktion.")
    st.caption(f"**A:** {strategies_now[a_key].description}")
    b_key = st.selectbox("Spediteur B", C.STRATEGY_KEYS, key="b_select", format_func=lambda k: strategies_now[k].label,
                         help="Die Strategie von B.")
    st.caption(f"**B:** {strategies_now[b_key].description}")
    st.markdown("**Fehler**")
    eps = st.slider("Rauschen ε", *bounds("eps_slider"), step=C.EPS_STEP, key="eps_slider",
                    help="Wahrscheinlichkeit, dass die ausgeführte Aktion die andere ist als die beabsichtigte.")
    q = st.slider("Vergebung q des großzügigen Tit-for-Tat", *bounds("q_slider"), step=C.Q_STEP, key="q_slider",
                  help="Wahrscheinlichkeit, mit der es nach einer Defektion des anderen trotzdem kooperiert. Bei 5/3/1/0 liegt der oft genannte Richtwert bei 1/3.")
    st.markdown("**Anzeige**")
    rounds = st.slider("Gezeigte Runden", *bounds("rounds_slider"), key="rounds_slider", help="Länge der Spur. Die Zahlen sind exakt und hängen nicht davon ab.")
    seed = st.number_input("Zufalls-Seed der Spur", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Spur würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"a_select": a_key, "b_select": b_key, "eps_slider": round(float(eps), 2), "q_slider": round(float(q), 2),
                   "rounds_slider": int(rounds), "seed_input": int(seed)})

settings = Settings(a_key, b_key, round(float(eps), 2), round(float(q), 2), int(rounds), int(seed))
an = _analysis(settings)
strategies = make_strategies(settings.q)
label_a, label_b = strategies[a_key].label, strategies[b_key].label

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown(f"## 🎬 Eine Verwechslung, Runde für Runde: {label_a} gegen {label_b}")
st.plotly_chart(build_trace(an.trace, C.FORCED_ROUND, label_a, label_b), width="stretch", key="trace_chart")
if an.trace_recovery_round is None:
    st.caption(f"In dieser Spur ist bis Runde {len(an.trace)} nach der Verwechslung in Runde {C.FORCED_ROUND} keine beidseitige Kooperation zurückgekehrt.")
else:
    st.caption(f"In dieser Spur ist die beidseitige Kooperation in Runde {an.trace_recovery_round} zurück, "
               f"{an.trace_recovery_round - C.FORCED_ROUND} Runden nach der Verwechslung. Mit ε > 0 kommen weitere zufällige Fehler hinzu.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Langfristig, Auszahlung von A", fmt(an.long_a), delta=f"B: {fmt(an.long_b)}", delta_color="off")
m2.metric(f"Erste {FINITE_HORIZON} Runden, A", fmt(an.finite_a), delta=f"B: {fmt(an.finite_b)}", delta_color="off")
m3.metric("Erholungszeit nach einem Fehler", "nie" if an.recovery == float("inf") else f"{fmt(an.recovery, 1)} Runden",
          delta="bis wieder beide kooperieren", delta_color="off")
m4.metric("Runden mit beidseitiger Kooperation", f"{fmt(an.coop_share * 100, 0)} %", delta="langfristig", delta_color="off")
st.caption(
    "Langfristig heißt: die Dauerverteilung der Kette; sie gilt erst nach etwa 1/ε Runden. Ohne Rauschen gibt es keine eindeutige Dauerverteilung, dort ist der "
    f"Wert der Mittelwert der ersten {C.HORIZON} Runden."
)

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie schnell kehrt die Kooperation nach einem Fehler zurück?")
level, sentence = E.verdict(an, settings)
{"success": st.success, "warning": st.warning, "info": st.info}[level](sentence)
st.markdown("---")

# --- Experiment 1 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Was kosten Fehler langfristig?")
st.caption("Langfristige mittlere Auszahlung je Runde, wenn zwei gleiche Strategien gegeneinander spielen, für Rauschen von 0 bis 20 %. Punktiert: Tit-for-Tat über nur 200 Runden.")
labels = {k: s.label for k, s in strategies.items()}
st.plotly_chart(build_eps_curves(_curves(settings.q), labels), width="stretch", key="eps_chart")
st.info(
    "Zwei Tit-for-Tat landen für **jedes** ε > 0 langfristig bei genau (T + R + P + S) / 4 = 2,25 Punkten je Runde: die Dauerverteilung ist gleichverteilt über die vier "
    "Ergebnisse. Der Sprung gegenüber 3,00 ohne Fehler ist real, wird aber erst nach etwa 1/ε Runden erreicht; über 200 Runden bei 1 % Rauschen sind es noch "
    f"{fmt(E.A.finite_payoff(strategies['TFT'], strategies['TFT'], 0.01, FINITE_HORIZON)[0])}. Großzügiges Tit-for-Tat und Pavlov liegen bei 5 % Rauschen langfristig "
    f"bei {fmt(E.A.average_payoff(strategies['GTFT'], strategies['GTFT'], 0.05)[0])} und {fmt(E.A.average_payoff(strategies['PAVLOV'], strategies['PAVLOV'], 0.05)[0])}."
)
st.markdown("---")

# --- Experiment 2 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wie lange dauert die Erholung?")
st.caption(f"Erwartete Zahl der Runden bis wieder beide kooperieren, nachdem A einmal verwechselt hat, bei ε = {fmt(settings.eps)} (aus der Seitenleiste).")
rec = _recovery(settings.eps, settings.q)
st.plotly_chart(build_recovery(rec, labels), width="stretch", key="recovery_chart")
if rec["TFT"] == float("inf"):
    st.info("Ohne Rauschen kehrt Tit-for-Tat gegen sich selbst **nie** zur Kooperation zurück, großzügiges Tit-for-Tat braucht 1/q Runden, Pavlov genau zwei.")
else:
    st.info(
        f"Tit-for-Tat braucht im Mittel {fmt(rec['TFT'], 1)} Runden, großzügiges Tit-for-Tat {fmt(rec['GTFT'], 1)}, Pavlov {fmt(rec['PAVLOV'], 1)}. "
        "Bei Tit-for-Tat beendet erst ein weiterer Fehler das Echo; je seltener Fehler sind, desto länger dauert es."
    )
st.markdown("---")

# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Was kostet die Fehlertoleranz gegen Ausbeuter?")
st.caption(f"Langfristige Auszahlung der Zeile gegen die Spalte bei ε = {fmt(settings.eps)}.")
cross = _cross(settings.eps, settings.q)
st.plotly_chart(build_cross(cross, labels), width="stretch", key="cross_chart")
keys = list(C.STRATEGY_KEYS)
i_p, i_t, i_g, i_d = keys.index("PAVLOV"), keys.index("TFT"), keys.index("GTFT"), keys.index("ALLD")
st.warning(
    f"Gegen Immer-Defektieren erzielt Tit-for-Tat {fmt(cross[i_t][i_d])}, großzügiges Tit-for-Tat {fmt(cross[i_g][i_d])} und Pavlov nur {fmt(cross[i_p][i_d])}: "
    "Pavlov kooperiert abwechselnd mit einem Dauer-Defektierer und zahlt dafür. Die Fehlertoleranz ist kein Geschenk, sie hat einen Preis gegen Ausbeuter."
)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Gedächtnis von genau einer Runde** | Strategien mit längerem Gedächtnis (etwa Tit-for-Two-Tats oder Grim Trigger) sind keine Markov-Ketten mit vier Zuständen; die Rechnung gilt für sie nicht. | - |
| **Beide sehen die ausgeführte Aktion** | Wenn ein Spieler nur seine Absicht kennt oder die Beobachtung selbst verrauscht ist, ändert sich die Kette. Das Modell kennt nur Verwechslung bei der Ausführung. | - |
| **Fehler sind unabhängig mit gleicher Rate** | Gebündelte Fehler (ein Systemausfall hintereinander) oder Fehler nur bei einem der beiden verändern die Erholungszeiten. | - |
| **Zwei feste Partner** | Wechselnde Partner brauchen Reputation statt Gedächtnis. | - |
| **Pavlov ist hier „gut“** | Gegen Immer-Defektieren zahlt Pavlov am meisten (Experiment 3), und in Turnieren mit angepassten Gegnern gilt es in der Literatur als nicht robust. | - |
| **Dauerverteilung als Maß** | Sie gilt erst nach etwa 1/ε Runden; bei seltenen Fehlern und kurzen Beziehungen ist die Auszahlung über eine endliche Länge näher an 3,00 (Experiment 1). | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Zustand.** Das Ergebnis der letzten Runde $(x, y) \in \{C, D\}^2$: vier Zustände. Eine Strategie ist die Wahrscheinlichkeit $p_{xy}$,
nach dem Ergebnis $(x, y)$ aus eigener Sicht zu kooperieren, plus die Wahrscheinlichkeit der ersten Runde. Tit-for-Tat: $(1, 0, 1, 0)$,
großzügiges Tit-for-Tat: $(1, q, 1, q)$, Pavlov: $(1, 0, 0, 1)$ für $(C,C), (C,D), (D,C), (D,D)$.

**Rauschen.** Aus der Absicht $p$ wird die Ausführungswahrscheinlichkeit $c = (1-\varepsilon)\,p + \varepsilon\,(1-p)$. Die Übergangsmatrix
$P$ des Paares hat die Einträge $P_{(x,y),(x',y')} = c_A^{x'}\,c_B^{y'}$ mit der jeweils passenden Wahrscheinlichkeit für C beziehungsweise D.

**Langfristige Auszahlung.** Für $\varepsilon > 0$ ist die Kette irreduzibel und hat eine eindeutige Dauerverteilung $\pi$ mit $\pi P = \pi$;
die mittlere Auszahlung ist $\pi \cdot u$. Bei Tit-for-Tat gegen Tit-for-Tat ist $\pi$ gleichverteilt (die Kette ist doppelt-stochastisch),
also $(T + R + P + S)/4$ unabhängig von $\varepsilon$.

**Erholungszeit.** Mit $Q$ als Teilmatrix von $P$ auf den Zuständen ohne $(C,C)$ löst $t = (I - Q)^{-1}\mathbf{1}$ die erwartete Zahl der Runden
bis zum nächsten $(C,C)$. Nach einer Verwechslung von A ist der Startzustand $(D, C)$. Ohne Rauschen gilt: Pavlov $t = 2$, großzügiges
Tit-for-Tat $t = 1/q$, Tit-for-Tat $t = \infty$ (das Echo $(C,D) \to (D,C) \to \dots$ ist geschlossen).

**Literatur.** Molander (1985), *The optimal level of generosity in a selfish, uncertain environment*, Journal of Conflict Resolution 29,
611–618 (Tit-for-Tat bricht schon bei wenig Rauschen ein, Großzügigkeit hilft); Nowak und Sigmund (1992), *Tit for tat in heterogeneous
populations*, Nature 355, 250–253 (großzügiges Tit-for-Tat; der Richtwert 1/3 stammt aus Sekundärquellen, nicht aus dem Volltext); Nowak und
Sigmund (1993), *A strategy of win-stay, lose-shift that outperforms tit-for-tat in the Prisoner's Dilemma game*, Nature 364, 56–58 (Pavlov
korrigiert Fehler und beutet Immer-Kooperierer aus); Imhof, Fudenberg und Nowak (2007), *Tit-for-tat or win-stay, lose-shift?*, Journal of
Theoretical Biology (erwartete Auszahlung zweier Tit-for-Tat unter Rauschen $(R+S+T+P)/4$); Wu und Axelrod (1995), *How to cope with noise in
the iterated prisoner's dilemma*, Journal of Conflict Resolution (großzügiges Tit-for-Tat gegen nicht angepasste Gegner, Pavlov nicht robust).
Nur Zusammenfassungen gelesen, nicht die Volltexte.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
