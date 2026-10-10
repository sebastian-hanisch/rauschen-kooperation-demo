# Fehler und Vergebung: Rauschen, großzügiges Tit-for-Tat und Pavlov – Streamlit-Demo

<!-- Nach dem Deploy direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-rauschen-kooperation-demo.streamlit.app/)** -->

Drittes Stück der **Wiederholte-Spiele-Linie** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“.
Nachfolger von [axelrod-turnier-demo](https://sebastianhanisch-axelrod-turnier-demo.streamlit.app/): dort sieht man im Turnier, dass Rauschen die Rangfolge verändert;
hier wird der **Mechanismus exakt gerechnet**. Die Kante ist ein `fix`: Tit-for-Tat ist ohne Fehler stabil, aber gegen Verwechslungen unbrauchbar; großzügiges Tit-for-Tat und
Pavlov beheben das auf zwei verschiedene Weisen.

Vehikel: der Rückladungstausch aus Stück 1 mit den Auszahlungen 5/3/1/0. Eine Verwechslung ist eine Rückladung, die nicht ankommt, ein Auftrag, der untergeht. Eigennutz und
Rationalität sind Modellannahmen.

## Warum dieses Problem

Ein einzelner Fehler lässt zwei Tit-for-Tat ewig abwechselnd vergelten (ein **Echo**), bis ein zweiter Fehler es zufällig beendet. Die Frage ist, wie teuer das langfristig ist,
wie schnell sich Kooperation erholt und was Vergebung und Pavlov dafür bezahlen.

## Modell

Jede Strategie entscheidet nur nach dem Ergebnis der letzten Runde (vier Fälle): ein **Markov-Kette mit vier Zuständen** für das Paar. Rauschen ε vertauscht jede
beabsichtigte Aktion unabhängig; beide sehen die ausgeführte. Fünf Strategien: Immer kooperieren, Immer defektieren, Tit-for-Tat, großzügiges Tit-for-Tat (Vergebung q,
Voreinstellung 0,33) und Pavlov. Die App erklärt jede mit Beschreibung, Kooperationswahrscheinlichkeiten und ihrer Spur nach einer erzwungenen Verwechslung.

## Methodik

- **Langfristige Auszahlung:** Dauerverteilung der Kette (`average_payoff`, ε > 0); bei ε = 0 gibt es keine eindeutige Dauerverteilung, dort der Mittelwert der ersten 1000 Runden.
- **Endliche Länge:** `finite_payoff`: exakte Fortschreibung der Verteilung über die ersten n Runden. Die Dauerverteilung gilt erst nach etwa 1/ε Runden.
- **Erholungszeit:** `recovery_time`: erwartete Runden bis wieder (C,C), ausgehend vom Ergebnis, das eine Verwechslung von A hinterlässt: lineares System auf den übrigen
  Zuständen, unendlich, wenn (C,C) nicht sicher erreichbar ist.

## Befunde (gemessen, keine Behauptungen)

Auszahlungen 5/3/1/0, Strategien gegen sich selbst, wenn nicht anders genannt.

| Frage | Befund | Test |
|---|---|---|
| Was zahlen zwei Tit-for-Tat unter Rauschen? | Langfristig genau 2,25 = (T+R+P+S)/4 für **jedes** ε > 0 (die Dauerverteilung ist gleichverteilt), gegen 3,00 ohne Fehler. | `test_tft_pair_pays_2_25_for_every_positive_noise_and_3_without`, `test_tft_pair_is_uniform_for_every_noise_and_pays_the_average_of_the_four_outcomes` |
| Wie schnell ist das erreicht? | Erst nach etwa 1/ε Runden: über 20 Runden bei 1 % Rauschen sind es noch 2,90, über 200 Runden 2,46. | `test_tft_over_200_rounds_at_one_percent_noise` |
| Wie lange dauert die Erholung? | Tit-for-Tat: ohne Rauschen nie (das Echo ist geschlossen), bei 1 % im Mittel 150,5 Runden, bei 5 % 30,5. Großzügiges Tit-for-Tat: 1/q = 3,03 Runden ohne, 3,14 bei 5 %. Pavlov: genau 2 Runden ohne, 2,33 bei 5 %. | `test_recovery_times`, `test_gtft_without_noise_recovers_in_one_over_q_rounds` |
| Langfristig bei 5 % Rauschen? | Immer kooperieren 2,947, Immer defektieren 1,147, Tit-for-Tat 2,25, großzügiges Tit-for-Tat 2,858, Pavlov 2,777. | `test_symmetric_long_run_payoffs_at_five_percent` |
| Was kostet die Fehlertoleranz gegen einen Ausbeuter? | Gegen Immer-Defektieren (5 %): Tit-for-Tat 1,10, großzügiges Tit-for-Tat 0,80, Pavlov 0,675. Pavlov beutet Immer-Kooperieren aus (3,825 gegen 1,575). | `test_the_exploiter_cost_at_five_percent` |
| Wie wirkt die Größe der Vergebung? | Mit q = 0,05 / 1/3 / 0,8 zahlt ein großzügiges Paar 2,54 / 2,86 / 2,94 (5 %), verliert gegen Immer-Defektieren aber 1,06 / 0,80 / 0,38: mehr Vergebung hilft dem Paar und kostet gegen Ausbeuter. | `test_generosity_trade_off_between_a_gtft_pair_and_exploitation` |

### Befunde gegenüber dem Plan

Der Plan der Linie erwartete „zwei Tit-for-Tat fallen auf ca. (R+S+T+P)/4; großzügiges Tit-for-Tat und Pavlov halten Kooperation“. Das bestätigt sich exakt, mit zwei Präzisierungen:
(1) der Wert 2,25 ist eine **Dauerverteilung** und kein Wert für kurze Beziehungen (über 200 Runden bei 1 % sind es 2,46); (2) Pavlov hält Kooperation untereinander, **verliert aber
am meisten gegen einen Dauer-Defektierer**, mehr als Tit-for-Tat und großzügiges Tit-for-Tat. In der Literatur gilt Pavlov unter Rauschen mit angepassten Gegnern deshalb nicht
als robust (Wu/Axelrod 1995, nur über die Zusammenfassung gelesen).

## Ehrliche Grenzen

- **Ein Zug Gedächtnis:** Strategien mit längerem Gedächtnis (Tit-for-Two-Tats, Grim Trigger) sind keine Vier-Zustands-Ketten; für sie gilt die Rechnung nicht.
- **Beide sehen die ausgeführte Aktion:** private oder verrauschte Beobachtung ist nicht modelliert.
- **Unabhängige Fehler mit gleicher Rate**, gebündelte Fehler ändern die Zeiten.
- **Zwei feste Partner**, keine Reputation, keine Population.
- **Richtwert 1/3 für die Vergebung:** aus Sekundärquellen, nicht aus dem Volltext von Nowak/Sigmund (1992).

## Verifikation

- **Kern:** je Einheit eine Handrechnung (Übergangsmatrizen von Tit-for-Tat und Pavlov, Rauschverteilung, erste Runde, Spuren mit erzwungenem Fehler, Erholungszeiten
  1, 2, 1/q und unendlich).
- **Orakel** (`tests/test_oracle_rauschen_kooperation.py`), die Simulation dort ist direkt aus den Strategietabellen geschrieben und nutzt weder Übergangsmatrix noch
  `simulate` des Kerns: (1) die Dauerverteilung gegen Potenziteration; (2) die langfristige und die endliche Auszahlung gegen viele simulierte Spiele für sieben Paare;
  (3) die Erholungszeit gegen simulierte Wartezeiten; (4) geschlossene Formeln (Gleichverteilung bei Tit-for-Tat, 1/q bei großzügigem Tit-for-Tat) und die Symmetrie
  der Auszahlungen beim Tauschen der Spieler.
- **Claims:** jede Zahl dieses READMEs in `tests/test_claims.py`.
- **Oberfläche:** AppTest (jeder Button, jeder Regler am Minimum und Maximum, Permalink begrenzt und rastet ein, jede Strategie erklärt, Aussage „nie“ ohne Rauschen) und Footer-Test.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `rkn_algorithm.py` | Kern: Übergangsmatrix, Dauerverteilung, endliche Auszahlung, Erholungszeit, Spur |
| `rkn_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `rkn_evaluation.py` | Analyse, Kurven über ε, Erholungstabelle, Kreuztabelle, Strategieübersicht, Verdikt |
| `rkn_presets.py` | Permalink (Begrenzen und Einrasten), Presets |
| `rkn_scenario.py` | Das Spiel und die fünf Strategien als Memory-1-Tabellen |
| `rkn_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Handrechnung, Orakel, Claims, Presets, AppTest-Smoke-Test, Footer |

## Bewusst nicht umgesetzt

- **Turnier mit vielen Strategien unter Rauschen:** das zeigt [axelrod-turnier-demo](https://sebastianhanisch-axelrod-turnier-demo.streamlit.app/).
- **Evolutionäre Stabilität gegen Eindringlinge** (welche Strategie sich in einer Population hält): eigenes Verfahren.
- **Längeres Gedächtnis und Beobachtungsrauschen:** eigene Modelle, andere Aussagen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
