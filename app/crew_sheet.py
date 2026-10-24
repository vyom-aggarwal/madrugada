"""Printable bilingual (EN/ES) crew sheet. Every interpolated value is HTML-escaped.

Spanish text needs native-speaker review.
"""
from html import escape

import numpy as np

# The Madrugada mark (same artwork as static/index.html), inline so the sheet works offline.
MARK = ('<svg class="mark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" aria-hidden="true"><defs><linearGradient id="cs-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#141a3d"/><stop offset="1" stop-color="#2f2c6b"/></linearGradient><linearGradient id="cs-sun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf6a"/><stop offset=".55" stop-color="#f7904d"/><stop offset="1" stop-color="#e5584d"/></linearGradient><linearGradient id="cs-haze" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a996f5" stop-opacity="0"/><stop offset=".18" stop-color="#a996f5" stop-opacity=".9"/><stop offset=".82" stop-color="#a996f5" stop-opacity=".9"/><stop offset="1" stop-color="#a996f5" stop-opacity="0"/></linearGradient><linearGradient id="cs-field" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d1f4a"/><stop offset="1" stop-color="#0d1030"/></linearGradient><linearGradient id="cs-rows" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3a53f" stop-opacity="0"/><stop offset=".35" stop-color="#f3a53f" stop-opacity=".55"/><stop offset="1" stop-color="#f6b25a"/></linearGradient><clipPath id="cs-clip"><rect width="64" height="64" rx="14"/></clipPath></defs><g clip-path="url(#cs-clip)"><rect width="64" height="64" fill="url(#cs-sky)"/><path d="M13 41a19 19 0 0 1 38 0z" fill="url(#cs-sun)"/><rect y="36.5" width="64" height="5.5" fill="url(#cs-haze)"/><rect y="42" width="64" height="22" fill="url(#cs-field)"/><path d="M32 42-12 64H-1ZM32 42 9 64H18ZM32 42 27.5 64H36.5ZM32 42 46 64H55ZM32 42 65 64H76Z" fill="url(#cs-rows)"/><path d="M0 42.2h64" stroke="#ffd8a0" stroke-width="1" opacity=".45"/></g></svg>')


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


def render(plan: dict, unfix: dict | None = None) -> str:
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
    if unfix:
        h = _e(_hours(unfix["hours_ge_95f"]["planned"]))
        fl_en, fl_es = _e(_clock(unfix["first_light_start"])), _e(_clock(unfix["first_light_start"], True))
        rows.append(("Hours scheduling can't fix (forecast-based estimate)",
                     f"Starting no earlier than first light ({fl_en}), the best plan still has about {h} h at or above "
                     f"{t['heat_high_f']}&deg;F. {_e(unfix['line'])}",
                     "Horas que el horario no puede evitar (estimación basada en el pronóstico)",
                     f"Empezando no antes del amanecer ({fl_es}), el mejor plan aún tiene unas {h} h a "
                     f"{t['heat_high_f']}&deg;F o más. {_e(unfix['line_es'])}"))
    body = "".join(f"<tr><td><h3>{a}</h3>{b}</td><td lang='es'><h3>{c}</h3>{d}</td></tr>" for a, b, c, d in rows[2:])
    times = "".join(f"<tr><td class='time'>{_clock(b['start'])} &ndash; {_clock(b['end'])}</td>"
                    f"<td class='time' lang='es'>{_clock(b['start'], True)} &ndash; {_clock(b['end'], True)}</td></tr>"
                    for b in blocks)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Crew sheet · Hoja de turno</title>
<style>
:root{{--ink:#141a2b;--mute:#4f5668;--line:#d9cfbf;--cream:#fbf5ea;--navy:#16213e;--amber:#f0a03c}}
*{{box-sizing:border-box}}
body{{font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:var(--ink);margin:0;background:#fff}}
.page{{max-width:880px;margin:0 auto;padding:20px 20px 28px}}
header{{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px;border-bottom:4px solid var(--amber);padding-bottom:10px}}
h1{{font:600 24px/1.15 Georgia,"Iowan Old Style","Palatino Linotype",serif;letter-spacing:-.01em;margin:0}} h3{{font-size:13px;margin:0 0 4px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute)}}
.day{{margin:4px 0 0;color:var(--mute)}}
.brand{{display:flex;align-items:center;gap:10px;-webkit-print-color-adjust:exact;print-color-adjust:exact}} .mark{{width:40px;height:40px;border-radius:22%}}
.word{{margin:0;font:600 20px/1.1 Georgia,"Iowan Old Style",serif;letter-spacing:.05em}} .tag{{margin:0;font-size:12px;color:var(--mute)}}
button{{min-height:44px;padding:0 18px;border-radius:999px;border:1px solid var(--line);background:var(--navy);color:#fff;font:700 15px inherit;cursor:pointer}}
.prov{{font-weight:700;padding:8px 10px;margin:12px 0;border:2px solid #b45309;background:#fef3c7;color:#7c2d12;border-radius:8px}}
.prov.real{{border-color:#1d4ed8;background:#dbeafe;color:#1e3a8a}}
table{{width:100%;border-collapse:separate;border-spacing:0 8px}}
td{{width:50%;vertical-align:top;padding:10px 12px;border:1px solid var(--line);background:#fff}}
td:first-child{{border-radius:8px 0 0 8px}} td:last-child{{border-radius:0 8px 8px 0;border-left:0;background:var(--cream)}}
.time{{font:700 34px/1.15 Georgia,"Iowan Old Style","Palatino Linotype",serif;letter-spacing:-.01em;line-height:1.15;font-variant-numeric:tabular-nums;color:var(--navy)}}
.oracle td{{background:#fde2e2;font-weight:700;border-width:2px;border-style:dashed}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:0}} .cols h3{{margin-top:6px}}
.note{{color:var(--mute);font-size:12px}}
@page{{size:letter;margin:12mm}}
@media print{{.prov{{background:#fff;color:#000;border:2px dashed #000}} .prov.real{{border-style:solid}} header{{border-bottom:3px double #000}} td{{background:#fff!important;border-color:#777}} .time{{color:#000}} .oracle td{{border-color:#000}} h3,.note,.day,.tag{{color:#333}} button{{display:none}} .page{{padding:0}} body{{font-size:12.5px}} .time{{font-size:28px}} td{{padding:7px 9px}} table{{break-inside:avoid}}}}
</style></head><body><div class="page">
<header><div class="brand">{MARK}<div><p class="word">Madrugada</p><p class="tag">Same hours. Smarter dawn.</p></div></div><div><h1>Crew shift sheet · Hoja de turno</h1><p class="day">{rows[0][1]}</p></div>
<button onclick="window.print()">Print / Imprimir</button></header>
<p class="prov{'' if synthetic else ' real'}">{prov_en} &nbsp;|&nbsp; {prov_es}</p>
<table><tr><td><h3>{rows[1][0]}</h3></td><td lang="es"><h3>{rows[1][2]}</h3></td></tr>{times}{oracle_row}{body}
<tr><td><h3>Disclaimer</h3>Advisory planning aid only; it aims to reduce modeled heat exposure-hours and shows smoke exposure. It does not replace
the employer's written Cal/OSHA Heat Illness Prevention Plan. Water, shade and rest requirements still apply.</td>
<td lang="es"><h3>Aviso</h3>Solo es una herramienta de planificación orientativa; busca reducir las horas de exposición al calor modeladas y muestra la exposición al humo.
No reemplaza el plan escrito de prevención de enfermedades por calor de Cal/OSHA del empleador. Los requisitos de
agua, sombra y descanso siguen vigentes.</td></tr>
</table>
<p class="note">Spanish text needs native-speaker review. Mode: {_e(plan['mode'])}.
Station-level data, modeled exposure-hours only. Not a compliance tool and not a health prediction.</p>
</div></body></html>"""
