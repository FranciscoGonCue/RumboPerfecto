import json
from django.forms import Widget
from django.utils.safestring import mark_safe


class AvailabilityCalendarWidget(Widget):

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        widget_id = attrs.get('id', f'id_{name}')

        try:
            blocked = json.loads(value) if isinstance(value, str) else (value or [])
            if not isinstance(blocked, list):
                blocked = []
        except Exception:
            blocked = []

        blocked_json = json.dumps(blocked)

        html = f"""
<div id="avail_wrap_{widget_id}" style="font-family: sans-serif; margin-top: 6px;">

  <!-- Input oculto que Django usa para leer/escribir el valor -->
  <textarea
    name="{name}"
    id="{widget_id}"
    style="display:none"
  >{blocked_json}</textarea>

  <!-- Resumen de fechas bloqueadas -->
  <div id="avail_summary_{widget_id}" style="
    margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 6px; min-height: 26px;
  "></div>

  <!-- Controles de navegación de meses -->
  <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
    <button type="button" id="avail_prev_{widget_id}"
      style="padding: 4px 10px; border-radius: 6px; border: 1px solid #ccc;
             background: #f9fafb; cursor: pointer; font-weight: 700; font-size: 14px;">‹</button>
    <span id="avail_month_label_{widget_id}"
      style="font-weight: 800; font-size: 14px; text-transform: capitalize; min-width: 160px; text-align: center;"></span>
    <button type="button" id="avail_next_{widget_id}"
      style="padding: 4px 10px; border-radius: 6px; border: 1px solid #ccc;
             background: #f9fafb; cursor: pointer; font-weight: 700; font-size: 14px;">›</button>
  </div>

  <!-- Leyenda -->
  <div style="display: flex; gap: 14px; font-size: 11px; font-weight: 700; margin-bottom: 8px; color: #555;">
    <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#10b981;margin-right:4px;vertical-align:middle;"></span>Disponible</span>
    <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#ef4444;margin-right:4px;vertical-align:middle;"></span>No disponible</span>
    <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#d1d5db;margin-right:4px;vertical-align:middle;"></span>Fuera de rango</span>
  </div>

  <!-- Cuadrícula del calendario -->
  <div id="avail_grid_{widget_id}" style="
    display: grid; grid-template-columns: repeat(7, 38px);
    gap: 2px; user-select: none;
  "></div>

  <p style="font-size: 11px; color: #888; margin-top: 8px;">
    El rango disponible se lee automáticamente de los campos
    <strong>Disponible desde</strong> y <strong>Disponible hasta</strong> de este mismo formulario.
  </p>
</div>

<script>
(function () {{
  const WIDGET_ID  = {json.dumps(widget_id)};
  const INPUT_ID   = WIDGET_ID;

  // ── state ──
  let blocked    = {blocked_json};
  let viewYear   = new Date().getFullYear();
  let viewMonth  = new Date().getMonth(); // 0-based

  // ── helpers ──
  function fmtKey(y, m, d) {{
    return y + '-' + String(m+1).padStart(2,'0') + '-' + String(d).padStart(2,'0');
  }}

  function getRange() {{
    const f = document.getElementById('id_fecha_disponible_desde');
    const t = document.getElementById('id_fecha_disponible_hasta');
    return {{ desde: f ? f.value : '', hasta: t ? t.value : '' }};
  }}

  function isInRange(key) {{
    const r = getRange();
    return r.desde && r.hasta && key >= r.desde && key <= r.hasta;
  }}

  function toggleDate(key) {{
    if (!isInRange(key)) return;
    const idx = blocked.indexOf(key);
    if (idx === -1) blocked.push(key);
    else blocked.splice(idx, 1);
    persist();
    render();
  }}

  function persist() {{
    document.getElementById(INPUT_ID).value = JSON.stringify(blocked);
  }}

  // ── render ──
  function render() {{
    renderSummary();
    renderGrid();
    renderLabel();
  }}

  function renderLabel() {{
    const now = new Date();
    const y = (Number.isFinite(viewYear)  && viewYear  > 1900) ? viewYear  : now.getFullYear();
    const m = (Number.isFinite(viewMonth) && viewMonth >= 0)   ? viewMonth : now.getMonth();
    const d = new Date(y, m, 1);
    document.getElementById('avail_month_label_' + WIDGET_ID).textContent =
      d.toLocaleDateString('es-ES', {{ month: 'long', year: 'numeric' }});
  }}

  function renderSummary() {{
    const el = document.getElementById('avail_summary_' + WIDGET_ID);
    el.innerHTML = '';
    if (!blocked.length) {{
      el.innerHTML = '<span style="color:#aaa;font-size:12px;font-style:italic;">Sin fechas bloqueadas</span>';
      return;
    }}
    const sorted = [...blocked].sort();
    sorted.forEach(function(d) {{
      const chip = document.createElement('span');
      chip.style.cssText = 'display:inline-flex;align-items:center;gap:4px;padding:2px 8px;' +
        'background:#fee2e2;color:#dc2626;border:1px solid #fecaca;border-radius:6px;font-size:11px;font-weight:700;cursor:pointer;';
      chip.textContent = d + ' ×';
      chip.title = 'Haz clic para desbloquear';
      chip.addEventListener('click', function() {{ toggleDate(d); }});
      el.appendChild(chip);
    }});
  }}

  function renderGrid() {{
    const grid = document.getElementById('avail_grid_' + WIDGET_ID);
    grid.innerHTML = '';

    // Cabecera días
    const days = ['Lu','Ma','Mi','Ju','Vi','Sá','Do'];
    days.forEach(function(d) {{
      const cell = document.createElement('div');
      cell.style.cssText = 'text-align:center;font-size:10px;font-weight:800;' +
        'color:#9ca3af;text-transform:uppercase;padding:4px 0;';
      cell.textContent = d;
      grid.appendChild(cell);
    }});

    const now = new Date();
    const safeYear  = (Number.isFinite(viewYear)  && viewYear  > 1900) ? viewYear  : now.getFullYear();
    const safeMonth = (Number.isFinite(viewMonth) && viewMonth >= 0)   ? viewMonth : now.getMonth();
    const firstDay = new Date(safeYear, safeMonth, 1);
    const lastDay  = new Date(safeYear, safeMonth + 1, 0);
    // Semana empieza en lunes (0=Lu…6=Do)
    let startDow = firstDay.getDay(); // 0=Dom
    startDow = (startDow === 0) ? 6 : startDow - 1; // adjust to Mon=0

    // Celdas vacías
    for (let i = 0; i < startDow; i++) {{
      grid.appendChild(document.createElement('div'));
    }}

    const today = new Date().toISOString().split('T')[0];

    for (let day = 1; day <= lastDay.getDate(); day++) {{
      const key = fmtKey(safeYear, safeMonth, day);
      const inRange  = isInRange(key);
      const isBlocked = blocked.includes(key);

      const cell = document.createElement('div');
      cell.style.cssText = 'width:38px;height:38px;display:flex;align-items:center;justify-content:center;' +
        'border-radius:50%;font-size:13px;font-weight:600;transition:all .12s;';

      if (!inRange) {{
        cell.style.color = '#d1d5db';
        cell.style.cursor = 'default';
      }} else if (isBlocked) {{
        cell.style.background = 'rgba(239,68,68,0.18)';
        cell.style.color = '#dc2626';
        cell.style.cursor = 'pointer';
        cell.style.textDecoration = 'line-through';
        cell.title = 'No disponible – clic para liberar';
        cell.addEventListener('mouseenter', function() {{
          cell.style.background = 'rgba(16,185,129,0.18)'; cell.style.color = '#059669';
          cell.style.textDecoration = 'none';
        }});
        cell.addEventListener('mouseleave', function() {{
          cell.style.background = 'rgba(239,68,68,0.18)'; cell.style.color = '#dc2626';
          cell.style.textDecoration = 'line-through';
        }});
        cell.addEventListener('click', function() {{ toggleDate(key); }});
      }} else {{
        cell.style.background = 'rgba(16,185,129,0.15)';
        cell.style.color = '#059669';
        cell.style.cursor = 'pointer';
        cell.title = 'Disponible – clic para bloquear';
        cell.addEventListener('mouseenter', function() {{
          cell.style.background = 'rgba(239,68,68,0.15)'; cell.style.color = '#dc2626';
        }});
        cell.addEventListener('mouseleave', function() {{
          cell.style.background = 'rgba(16,185,129,0.15)'; cell.style.color = '#059669';
        }});
        cell.addEventListener('click', function() {{ toggleDate(key); }});
      }}

      if (key === today) {{
        cell.style.outline = '2px solid #f97316';
        cell.style.outlineOffset = '-2px';
      }}

      cell.textContent = day;
      grid.appendChild(cell);
    }}
  }}

  // ── nav ──
  document.getElementById('avail_prev_' + WIDGET_ID).addEventListener('click', function() {{
    viewMonth--;
    if (viewMonth < 0) {{ viewMonth = 11; viewYear--; }}
    render();
  }});
  document.getElementById('avail_next_' + WIDGET_ID).addEventListener('click', function() {{
    viewMonth++;
    if (viewMonth > 11) {{ viewMonth = 0; viewYear++; }}
    render();
  }});

  // Redibujar cuando cambia el rango
  function watchRange() {{
    const f = document.getElementById('id_fecha_disponible_desde');
    const t = document.getElementById('id_fecha_disponible_hasta');
    if (f) f.addEventListener('change', function() {{ render(); }});
    if (t) t.addEventListener('change', function() {{ render(); }});
  }}

  // Iniciar en el mes de fecha_disponible_desde si existe y es válida
  function initViewMonth() {{
    const r = getRange();
    if (r.desde && /^\d{{4}}-\d{{2}}-\d{{2}}$/.test(r.desde)) {{
      const parts = r.desde.split('-');
      const y = parseInt(parts[0], 10);
      const m = parseInt(parts[1], 10) - 1;
      if (!isNaN(y) && !isNaN(m)) {{
        viewYear  = y;
        viewMonth = m;
      }}
    }}
    render();
    watchRange();
  }}

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', initViewMonth);
  }} else {{
    initViewMonth();
  }}
}})();
</script>
"""
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        return data.get(name)
