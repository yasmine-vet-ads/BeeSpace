#!/usr/bin/env python3
"""Generate a detailed 16:9 SVG mock screenshot for the BeeSpace ESP32 simulator."""
from pathlib import Path

OUT = Path("assets/generated/esp32-s3-simulator-architecture.svg")
W, H = 1920, 1080


def esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def rect(x, y, w, h, fill, stroke="none", sw=1, rx=0, opacity=1, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}" {extra}/>'


def line(x1, y1, x2, y2, stroke, sw=3, opacity=1, dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}" stroke-linecap="round"{dash_attr}/>'


def text(x, y, s, size=24, fill="#d8e2f0", weight=500, anchor="start", family="Inter, Segoe UI, Arial, sans-serif", opacity=1):
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" opacity="{opacity}">{esc(s)}</text>'


def code_text(x, y, s, size=20, fill="#c7d2fe", weight=400):
    return text(x, y, s, size, fill, weight, family="JetBrains Mono, Fira Code, Consolas, monospace")

svg = []
svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1120"/><stop offset="1" stop-color="#111827"/></linearGradient>
    <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#182033"/><stop offset="1" stop-color="#0d1322"/></linearGradient>
    <linearGradient id="board" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1f6f76"/><stop offset="1" stop-color="#123f48"/></linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="16" stdDeviation="18" flood-color="#000" flood-opacity="0.45"/></filter>
    <filter id="glow"><feGaussianBlur stdDeviation="4" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#67e8f9"/></marker>
  </defs>''')
svg.append(rect(0, 0, W, H, "url(#bg)"))
svg.append(rect(22, 18, 1876, 58, "#0f172a", "#26334f", 1, 14, 0.96))
svg.append(text(46, 55, "BeeSpace ESP32-S3 Hive Simulator", 24, "#f8fafc", 700))
for i, c in enumerate(["#ef4444", "#f59e0b", "#22c55e"]):
    svg.append(f'<circle cx="{1740+i*28}" cy="46" r="8" fill="{c}"/>')
svg.append(text(1842, 54, "Dark Mode", 17, "#94a3b8", 500, "end"))

# Main panels
svg.append(rect(30, 92, 1120, 760, "url(#panel)", "#334155", 1.5, 18, 0.98, 'filter="url(#shadow)"'))
svg.append(rect(1170, 92, 720, 760, "url(#panel)", "#334155", 1.5, 18, 0.98, 'filter="url(#shadow)"'))
svg.append(text(60, 136, "Circuit Area", 26, "#e2e8f0", 700))
svg.append(text(1198, 136, "Code / Logic Area", 26, "#e2e8f0", 700))

# Breadboard
svg.append(rect(192, 250, 636, 382, "#eef2f7", "#cbd5e1", 2, 18))
svg.append(rect(220, 280, 580, 52, "#dbeafe", "none", rx=8, opacity=0.85))
svg.append(rect(220, 552, 580, 52, "#fee2e2", "none", rx=8, opacity=0.85))
for y in range(360, 520, 22):
    for x in range(236, 790, 24):
        svg.append(f'<circle cx="{x}" cy="{y}" r="3.1" fill="#94a3b8" opacity="0.62"/>')
svg.append(line(220, 306, 800, 306, "#2563eb", 4, 0.7))
svg.append(line(220, 578, 800, 578, "#dc2626", 4, 0.7))
svg.append(text(204, 240, "solderless breadboard", 16, "#94a3b8", 600))

# ESP32 board
svg.append(rect(408, 303, 292, 286, "url(#board)", "#5eead4", 2.5, 22, 1, 'filter="url(#shadow)"'))
svg.append(text(554, 338, "ESP32-S3", 29, "#ecfeff", 800, "middle"))
svg.append(text(554, 365, "DevKitC-1", 18, "#a7f3d0", 600, "middle"))
svg.append(rect(485, 389, 150, 80, "#0f172a", "#64748b", 2, 8))
svg.append(text(560, 435, "Wi-Fi MCU", 20, "#e2e8f0", 700, "middle"))
svg.append(rect(455, 515, 204, 34, "#111827", "#64748b", 1, 6))
svg.append(text(557, 538, "USB-C / UART", 15, "#cbd5e1", 600, "middle"))
for y in range(324, 572, 20):
    svg.append(f'<circle cx="{424}" cy="{y}" r="5" fill="#d1d5db" stroke="#0f172a" stroke-width="1"/>')
    svg.append(f'<circle cx="{684}" cy="{y}" r="5" fill="#d1d5db" stroke="#0f172a" stroke-width="1"/>')

# Module function
def module(x, y, w, h, title, subtitle, color):
    svg.append(rect(x, y, w, h, "#111827", "#475569", 1.4, 12, 0.98, 'filter="url(#shadow)"'))
    svg.append(rect(x+10, y+10, w-20, 24, color, "none", rx=7, opacity=0.88))
    svg.append(text(x+w/2, y+55, title, 20, "#f8fafc", 750, "middle"))
    svg.append(text(x+w/2, y+82, subtitle, 15, "#cbd5e1", 600, "middle"))
    for i in range(4):
        svg.append(f'<circle cx="{x+26+i*22}" cy="{y+h-18}" r="4" fill="#fbbf24"/>')

modules = [
    (72, 182, 170, 110, "BME280", "Temp/Hum/Press", "#38bdf8"),
    (830, 185, 160, 104, "BH1750", "Light", "#facc15"),
    (82, 670, 176, 112, "INMP441", "Microphone", "#a78bfa"),
    (852, 660, 166, 116, "HX711", "Load Cell", "#fb7185"),
    (868, 390, 174, 118, "TCRT5000", "IR Reflective", "#f97316"),
    (70, 410, 188, 126, "MPU6050 + GPS", "IMU / Location", "#22c55e"),
]
for m in modules:
    module(*m)

# Wires, routed as colored polylines
wires = [
    (242, 248, 424, 344, "#38bdf8"), (830, 238, 684, 345, "#fde047"),
    (258, 722, 424, 550, "#c084fc"), (852, 712, 684, 550, "#fb7185"),
    (868, 450, 684, 470, "#fb923c"), (258, 472, 424, 450, "#22c55e"),
    (236, 285, 424, 324, "#ef4444"), (800, 578, 684, 570, "#2563eb"),
]
for x1, y1, x2, y2, c in wires:
    mx = (x1+x2)/2
    svg.append(f'<path d="M{x1},{y1} C{mx},{y1-55} {mx},{y2+55} {x2},{y2}" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round" opacity="0.92" filter="url(#glow)"/>')

# Code editor
svg.append(rect(1198, 164, 662, 495, "#0b1220", "#1e293b", 1, 12))
svg.append(rect(1198, 164, 662, 36, "#111827", "none", rx=12))
svg.append(text(1222, 188, "main.cpp", 16, "#94a3b8", 700))
code = [
    ("#include <ArduinoJson.h>", "#93c5fd"),
    ("#include <WiFi.h>", "#93c5fd"),
    ("void sensorTask(void *pv) {", "#f8fafc"),
    ("  StaticJsonDocument<512> doc;", "#c4b5fd"),
    ("  doc[\"temp\"] = bme.readTemperature();", "#fde68a"),
    ("  doc[\"weight\"] = scale.get_units();", "#fde68a"),
    ("  serializeJson(doc, mqttPayload);", "#86efac"),
    ("  mqtt.publish(\"hive/telemetry\", mqttPayload);", "#86efac"),
    ("}", "#f8fafc"),
    ("xTaskCreatePinnedToCore(sensorTask, \"sensors\", 4096, NULL, 2, NULL, 1);", "#f0abfc"),
    ("xTaskCreate(networkTask, \"mqtt\", 4096, NULL, 3, NULL);", "#f0abfc"),
    ("if (batteryLow) {", "#f8fafc"),
    ("  esp_sleep_enable_timer_wakeup(15 * 60 * 1000000ULL);", "#67e8f9"),
    ("  esp_deep_sleep_start();", "#fb7185"),
    ("}", "#f8fafc"),
]
for i, (s, c) in enumerate(code):
    svg.append(text(1220, 232+i*28, f"{i+1:02d}", 14, "#475569", 500, family="JetBrains Mono, Consolas, monospace"))
    svg.append(code_text(1262, 232+i*28, s, 18, c))

# Serial monitor
svg.append(rect(1198, 682, 662, 154, "#020617", "#1e293b", 1, 12))
svg.append(text(1220, 710, "Serial Monitor", 18, "#e2e8f0", 700))
logs = [
    "[WiFi] Connected",
    "[MQTT] Publishing payload: {\"temp\":35.2, \"weight\":40.1, \"lux\":781...}",
    "[AI] anomaly_score=-0.017 explain=weight_drop+heat_spike",
    "[Power] Entering Aggressive Deep Sleep",
]
for i, s in enumerate(logs):
    svg.append(code_text(1220, 742+i*27, s, 16, "#86efac" if i < 2 else "#fbbf24" if i == 2 else "#fb7185"))

# Overlay architecture panel
svg.append(rect(235, 124, 1138, 210, "#0f172a", "#67e8f9", 1.5, 20, 0.88, 'filter="url(#shadow)"'))
svg.append(text(262, 166, "System Architecture", 27, "#e0f2fe", 800))
# flow blocks
def block(x, y, w, h, label, sub, color):
    svg.append(rect(x, y, w, h, "#111827", color, 1.8, 12, 0.96))
    svg.append(text(x+w/2, y+34, label, 18, "#f8fafc", 760, "middle"))
    svg.append(text(x+w/2, y+60, sub, 14, "#cbd5e1", 600, "middle"))
block(265, 196, 250, 78, "Instrumented Hive", "Sensors", "#22c55e")
block(605, 190, 220, 90, "ESP32-S3", "FreeRTOS  •  MQTT Payload", "#38bdf8")
block(1008, 190, 250, 90, "Cloud Gateway", "Backend / AI", "#a78bfa")
svg.append(line(520, 235, 598, 235, "#67e8f9", 4, 1, "",))
svg[-1] = svg[-1].replace('/>', ' marker-end="url(#arrow)"/>')
svg.append(line(830, 235, 1000, 235, "#67e8f9", 4, 1, "8 8"))
svg[-1] = svg[-1].replace('/>', ' marker-end="url(#arrow)"/>')
svg.append(text(905, 220, "MQTT via Wi‑Fi", 15, "#67e8f9", 700, "middle"))
for i, item in enumerate(["IA.py", "isolation_forest.pkl model", "Explainable Alert output"]):
    svg.append(rect(1022, 292 + i*28, 224, 23, "#1e293b", "#475569", 1, 6, 0.98))
    svg.append(text(1134, 308 + i*28, item, 11, "#dbeafe", 650, "middle"))

# bottom status bar
svg.append(rect(30, 878, 1860, 72, "#0f172a", "#26334f", 1, 16, 0.98))
svg.append(text(58, 922, "Simulator running  •  FreeRTOS tasks: sensors, mqtt, power  •  Hive ID: BS-ESP32S3-001", 20, "#cbd5e1", 600))
svg.append(text(1860, 922, "60 FPS  |  Wi‑Fi RSSI -54 dBm", 18, "#94a3b8", 600, "end"))

# subtle grid / highlights
for x in range(60, W, 120):
    svg.append(line(x, 92, x, 852, "#1e293b", 1, 0.18))
for y in range(120, 850, 80):
    svg.append(line(30, y, 1890, y, "#1e293b", 1, 0.15))
svg.append('</svg>')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"Wrote {OUT}")
