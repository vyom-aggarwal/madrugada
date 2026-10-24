"""Printable bilingual (EN/ES) crew sheet. Every interpolated value is HTML-escaped.

Spanish text needs native-speaker review.
"""
from html import escape

import numpy as np


def _e(v) -> str:
    return escape(str(v), quote=True)


def _clock(hhmm: str, es: bool = False) -> str:
    h, m = map(int, hhmm.split(":"))
    suffix = ("a. m." if h < 12 else "p. m.") if es else ("AM" if h < 12 else "PM")
    return f"{h % 12 or 12}:{m:02d} {suffix}"


def _slot_clock(slot: int, es: bool = False) -> str:
    return _clock(f"{slot * 15 // 60:02d}:{slot * 15 % 60:02d}", es)


def _hours(x: float) -> str:
    return f"{x:g}"


def render(plan: dict) -> str:
    day, req, th = plan["day"], plan["request"], plan["thresholds"]
    m = plan["metrics"]["optimizer"]["planned"]
    temp, aqi = np.asarray(plan["forecast"]["temp_f"]), np.asarray(plan["forecast"]["aqi"])
    ti, ai = int(temp.argmax()), int(aqi.argmax())
    blocks = plan["plan"]["blocks"]
    en_blocks = "<br>".join(f"{_clock(b['start'])} &ndash; {_clock(b['end'])}" for b in blocks)
    es_blocks = "<br>".join(f"{_clock(b['start'], True)} &ndash; {_clock(b['end'], True)}" for b in blocks)
    synthetic = day["provenance"] == "synthetic"
    prov_en = ("Data: SYNTHETIC illustration, not a measurement." if synthetic
               else "Data: real station data (cached).")
    prov_es = ("Datos: ilustración SINTÉTICA, no es una medición." if synthetic
               else "Datos: datos reales de estación (en caché).")
    oracle = req["oracle"]
    oracle_row = (f"<tr class='oracle'><td>ORACLE: upper bound using the day's actual data, not a forecast.</td>"
                  f"<td>ORÁCULO: límite superior con los datos reales del día; no es un pronóstico.</td></tr>"
                  if oracle else "")
    v = {k: _e(_hours(m[k])) for k in ("hours_ge_80f", "hours_ge_95f", "hours_aqi_ge_101", "hours_aqi_ge_151",
                                        "dual_hazard_hours")}
    t = {k: _e(th[k]) for k in th}
    peak_t, peak_a = _e(f"{temp[ti]:.0f}"), _e(int(aqi[ai]))
    summary_en = (f"Forecast peak temperature {peak_t}&deg;F at {_e(_slot_clock(ti))}; forecast peak AQI {peak_a} "
                  f"at {_e(_slot_clock(ai))}. During these work blocks the forecast shows about {v['hours_ge_80f']} h "
                  f"at or above {t['heat_shade_f']}&deg;F (shade trigger), {v['hours_ge_95f']} h at or above "
                  f"{t['heat_high_f']}&deg;F (high-heat procedures), {v['hours_aqi_ge_101']} h at AQI "
                  f"{t['aqi_sensitive']}+ and {v['hours_aqi_ge_151']} h at AQI {t['aqi_smoke_rule']}+ "
                  f"(wildfire smoke rule); {v['dual_hazard_hours']} h with both heat and smoke.")
    summary_es = (f"Temperatura máxima pronosticada {peak_t}&deg;F a las {_e(_slot_clock(ti, True))}; ICA (AQI) "
                  f"máximo pronosticado {peak_a} a las {_e(_slot_clock(ai, True))}. Durante estos bloques de trabajo "
                  f"el pronóstico indica aproximadamente {v['hours_ge_80f']} h a {t['heat_shade_f']}&deg;F o más "
                  f"(umbral de sombra), {v['hours_ge_95f']} h a {t['heat_high_f']}&deg;F o más (procedimientos de "
                  f"calor extremo), {v['hours_aqi_ge_101']} h con ICA de {t['aqi_sensitive']} o más y "
                  f"{v['hours_aqi_ge_151']} h con ICA de {t['aqi_smoke_rule']} o más (norma de humo de incendios); "
                  f"{v['dual_hazard_hours']} h con calor y humo a la vez.")
    rows = [
        ("Day", _e(f"{day['date']} · {day['label']}"), "Día", _e(f"{day['date']} · {day['label']}")),
        ("Work blocks (local time)", en_blocks, "Bloques de trabajo (hora local)", es_blocks),
        ("Paid hours", _e(_hours(plan["plan"]["paid_hours"])), "Horas pagadas", _e(_hours(plan["plan"]["paid_hours"]))),
        ("Hazard summary (forecast-based estimate)", summary_en,
         "Resumen de riesgos (estimación basada en el pronóstico)", summary_es),
    ]
    body = "".join(f"<tr><td><b>{a}</b><br>{b}</td><td><b>{c}</b><br>{d}</td></tr>" for a, b, c, d in rows)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Crew sheet · Hoja de turno</title>
<style>
body{{font:14px/1.45 system-ui,sans-serif;color:#111;margin:24px auto;max-width:860px;padding:0 16px;background:#fff}}
h1{{font-size:20px;margin:0 0 8px}} table{{width:100%;border-collapse:collapse}}
td{{width:50%;vertical-align:top;border:1px solid #bbb;padding:8px}}
.prov{{font-weight:700;padding:6px 8px;border:2px solid #b45309;background:#fef3c7;color:#7c2d12}}
.prov.real{{border-color:#1d4ed8;background:#dbeafe;color:#1e3a8a}} .oracle td{{background:#fde2e2;font-weight:700}}
.note{{color:#555;font-size:12px}} @media print{{button{{display:none}}}}
</style></head><body>
<button onclick="window.print()">Print / Imprimir</button>
<h1>Crew shift sheet · Hoja de turno</h1>
<p class="prov{'' if synthetic else ' real'}">{prov_en} &nbsp;|&nbsp; {prov_es}</p>
<table>{oracle_row}{body}
<tr><td><b>Disclaimer</b><br>Advisory planning aid only; it reduces modeled exposure-hours. It does not replace
the employer's written Cal/OSHA Heat Illness Prevention Plan. Water, shade and rest requirements still apply.</td>
<td><b>Aviso</b><br>Solo es una herramienta de planificación orientativa; reduce las horas de exposición modeladas.
No reemplaza el plan escrito de prevención de enfermedades por calor de Cal/OSHA del empleador. Los requisitos de
agua, sombra y descanso siguen vigentes.</td></tr>
</table>
<p class="note">Spanish text needs native-speaker review. Mode: {_e(plan['mode'])}.
Station-level data, modeled exposure-hours only. Not a compliance tool and not a health prediction.</p>
</body></html>"""
