"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Permalink-Begrenzen/Einrasten."""

import pytest

import rkn_constants as C
import rkn_evaluation as ev
import rkn_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, preset in C.PRESETS.items():
        assert C.EPS_MIN <= preset["eps"] <= C.EPS_MAX, name
        assert C.Q_MIN <= preset["q"] <= C.Q_MAX, name
        assert preset["a"] in C.STRATEGY_KEYS and preset["b"] in C.STRATEGY_KEYS, name


def test_default_preset_equals_the_default_settings():
    first = next(iter(C.PRESETS.values()))
    assert ev.Settings(a=first["a"], b=first["b"], eps=first["eps"], q=first["q"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) <= set(P.SETTING_SPECS)


def test_clamp_limits_numbers_and_snaps_choices():
    eps = P.SETTING_SPECS["eps_slider"]
    assert P.clamp(eps, 0.9) == C.EPS_MAX and P.clamp(eps, -1.0) == C.EPS_MIN
    choice = P.SETTING_SPECS["a_select"]
    assert P.clamp(choice, "PAVLOV") == "PAVLOV" and P.clamp(choice, "gibt-es-nicht") == C.DEFAULT_A


def test_presets_make_their_story_true():
    """Die Presets behaupten etwas über Echo, Vergebung und Pavlov; hier steht, dass es stimmt."""
    tft = ev.analyse(ev.Settings(a="TFT", b="TFT", eps=0.05))
    gtft = ev.analyse(ev.Settings(a="GTFT", b="GTFT", eps=0.05))
    pav = ev.analyse(ev.Settings(a="PAVLOV", b="PAVLOV", eps=0.05))
    assert tft.recovery > 10 > gtft.recovery and gtft.recovery > pav.recovery
    pavd = ev.analyse(ev.Settings(a="PAVLOV", b="ALLD", eps=0.05))
    tftd = ev.analyse(ev.Settings(a="TFT", b="ALLD", eps=0.05))
    assert pavd.long_a < tftd.long_a
    assert ev.analyse(ev.Settings(a="TFT", b="TFT", eps=0.0)).long_a == pytest.approx(3.0)
