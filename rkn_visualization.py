"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import rkn_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=380, legend=True):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="rgba(0,0,0,0)", showlegend=legend,
                      legend=dict(orientation="h", y=-0.25))
    return lock_axes(fig)


def build_trace(trace, forced_round, label_a, label_b):
    """Aktionsspur: grün = kooperiert, rot = defektiert; die erzwungene Verwechslung von A ist markiert."""
    n = len(trace)
    rounds = list(range(1, n + 1))
    fig = go.Figure()
    for name, idx in ((f"A: {label_a}", 0), (f"B: {label_b}", 1)):
        colors = [C.COLOR_COOP if t[idx] == C.COOPERATE else C.COLOR_DEFECT for t in trace]
        texts = ["kooperiert" if t[idx] == C.COOPERATE else "defektiert" for t in trace]
        fig.add_trace(go.Scatter(x=rounds, y=[name] * n, mode="markers", marker=dict(symbol="square", size=18, color=colors),
                                 text=texts, hovertemplate="Runde %{x}: %{text}<extra>%{y}</extra>", showlegend=False))
    fig.add_vline(x=forced_round, line=dict(color="rgba(60,60,60,0.7)", width=1.5, dash="dot"),
                  annotation_text="Verwechslung von A", annotation_position="top")
    fig.update_xaxes(title_text="Runde (Woche)", dtick=2, range=[0.4, n + 0.6])
    fig.update_yaxes(autorange="reversed", type="category")
    return _base(fig, height=250, legend=False)


def build_eps_curves(curves, labels, show_tft_200=True):
    """Langfristige Auszahlung gegen sich selbst über das Rauschen; für Tit-for-Tat zusätzlich die ersten 200 Runden."""
    fig = go.Figure()
    for key in C.STRATEGY_KEYS:
        fig.add_trace(go.Scatter(x=curves["eps"], y=curves[key], mode="lines", name=labels[key],
                                 line=dict(color=C.COLOR_LINES[key], width=4 if key in ("TFT", "GTFT", "PAVLOV") else 2),
                                 hovertemplate=labels[key] + ": ε = %{x:.3f}, %{y:.2f}<extra></extra>"))
    if show_tft_200:
        fig.add_trace(go.Scatter(x=curves["eps"], y=curves["TFT_200"], mode="lines", name="Tit-for-Tat, nur 200 Runden",
                                 line=dict(color=C.COLOR_LINES["TFT"], width=2, dash="dot"),
                                 hovertemplate="Tit-for-Tat, 200 Runden: ε = %{x:.3f}, %{y:.2f}<extra></extra>"))
    fig.update_xaxes(title_text="Rauschen ε (Wahrscheinlichkeit einer Verwechslung je Aktion)")
    fig.update_yaxes(title_text="mittlere Auszahlung je Runde gegen sich selbst", range=[0.8, 3.15])
    return _base(fig, height=430)


def build_recovery(times, labels):
    """Erwartete Erholungszeit je Strategie; „nie“ wird als Balken über die Achse hinaus mit Beschriftung gezeigt."""
    keys = list(times)
    finite = [t for t in times.values() if t != float("inf")]
    cap = max(finite + [3.0]) * 1.35
    vals = [min(times[k], cap) for k in keys]
    text = ["nie" if times[k] == float("inf") else f"{times[k]:.1f}".replace(".", ",") for k in keys]
    colors = [C.COLOR_DEFECT if times[k] == float("inf") else C.COLOR_LINES[k] for k in keys]
    fig = go.Figure(go.Bar(x=[labels[k] for k in keys], y=vals, marker_color=colors, text=text, textposition="outside",
                           hovertemplate="%{x}: %{text} Runden<extra></extra>"))
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="erwartete Runden bis wieder beide kooperieren", range=[0, cap * 1.15])
    return _base(fig, height=340, legend=False)


def build_cross(table, labels):
    keys = list(C.STRATEGY_KEYS)
    names = [labels[k] for k in keys]
    fig = go.Figure(go.Heatmap(z=table, x=names, y=names, zmin=0, zmax=5, colorscale="Teal", xgap=1, ygap=1,
                               text=[[f"{v:.2f}".replace(".", ",") for v in row] for row in table], texttemplate="%{text}",
                               hovertemplate="%{y} gegen %{x}: %{z:.2f}<extra></extra>", showscale=False))
    fig.update_yaxes(autorange="reversed", type="category")
    fig.update_xaxes(type="category")
    return _base(fig, height=380, legend=False)
