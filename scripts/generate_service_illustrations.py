#!/usr/bin/env python3
# Generates the homepage service illustrations (assets/images/services/*.svg),
# referenced from _data/entity/services.yml. Edit this file and rerun; do not hand-edit the SVGs.
#   python3 scripts/generate_service_illustrations.py          # write the SVGs
#   python3 scripts/generate_service_illustrations.py --check  # exit 1 if any SVG is stale
# Canvas 640x240; keep meaningful content inside x 90-550, y 40-200 so the
# card's object-fit:cover crop (from ~2:1 on desktop to ~3.9:1 on mobile) never cuts it.
import os, sys
CHECK = '--check' in sys.argv
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'images', 'services')
STALE = []
FONT = 'system-ui,-apple-system,&quot;Segoe UI&quot;,Roboto,sans-serif'
HEAD = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 240" role="img" aria-labelledby="t"><title id="t">{title}</title>
<defs>
<radialGradient id="bg" cx=".5" cy=".45" r=".8"><stop offset="0" stop-color="#1f3d5b"/><stop offset="1" stop-color="#0b1622"/></radialGradient>
<pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#6fb4d6" fill-opacity=".14"/></pattern>
<linearGradient id="pn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#284a6b"/><stop offset="1" stop-color="#172b40"/></linearGradient>
<linearGradient id="pn2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#36658f"/><stop offset="1" stop-color="#1f3d5b"/></linearGradient>
<filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#000" flood-opacity=".45"/></filter>
<filter id="gl" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
.pn{{fill:url(#pn);stroke:#3f7aa0;stroke-width:1.5}}.pn2{{fill:url(#pn2);stroke:#6fb4d6;stroke-width:1.5}}
.ln{{fill:none;stroke:#6fb4d6;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}}
.wire{{fill:none;stroke:#376986;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}
.lb{{fill:#e6eff6;font:600 17px {font}}}.lbs{{fill:#9cc0d6;font:500 14px {font}}}
.t{{fill:#6fb4d6}}.tl{{fill:#a9d8ef}}.td{{fill:#376986}}.dk{{fill:#14263a}}.w{{fill:#e6eff6}}.r{{fill:#e04848}}
.rs{{fill:none;stroke:#e04848;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}}
.pk{{fill:#cdeaf8}}.pkr{{fill:#ff6b6b}}
{css}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.pk,.pkr{{display:none}}}}
</style>
<rect width="640" height="240" fill="url(#bg)"/><rect width="640" height="240" fill="url(#dots)"/>
{body}
</svg>
'''

def pk(path, dur, begin=0, cls='pk', r=4):
    return (f'<circle class="{cls}" r="{r}" filter="url(#gl)"><animateMotion dur="{dur}s" begin="{begin}s" '
            f'repeatCount="indefinite" path="{path}"/></circle>')

def check(x, y, s=1, cls='ln'):
    return f'<path class="{cls}" d="M{x} {y}l{5*s} {5*s} {10*s} {-11*s}"/>'

def gear(cx, cy, r=10, cls='t'):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#6fb4d6" stroke-width="{r*.55:.1f}" '
            f'stroke-dasharray="{r*.42:.1f} {r*.3:.1f}"/><circle cx="{cx}" cy="{cy}" r="{r*.62:.1f}" class="{cls}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*.25:.1f}" class="dk"/>')

def write(name, title, body, css=''):
    path, svg = os.path.join(OUT, name + '.svg'), HEAD.format(title=title, css=css, font=FONT, body=body)
    if CHECK:
        try:
            current = open(path, encoding='utf-8').read()
        except FileNotFoundError:
            current = None
        if current != svg:
            STALE.append(name)
        return
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)

# ---------------------------------------------------------------- AI (animated)
L1, L2, L3 = [(282, 84), (282, 120), (282, 156)], [(320, 70), (320, 102), (320, 138), (320, 170)], [(358, 96), (358, 144)]
edges = ''.join(f'M{a[0]} {a[1]}L{b[0]} {b[1]}' for X, Y in ((L1, L2), (L2, L3)) for a in X for b in Y)
nodes = ''.join(f'<circle class="nd" style="animation-delay:{i*.3:.1f}s" cx="{x}" cy="{y}" r="6"/>' for i, (x, y) in enumerate(L1 + L2 + L3))
p_in1, p_in2 = 'M178 100C214 100 222 110 250 110', 'M178 132C214 132 222 130 250 130'
p_out, p_exc = 'M390 88C410 88 412 86 430 86', 'M390 152C412 152 410 170 430 170'
write('ai', 'Documents flowing through an AI model inside guardrails into structured records, with one exception routed for human review', f'''
<g filter="url(#sh)"><rect class="pn" x="100" y="62" width="58" height="74" rx="6"/><rect class="pn" x="110" y="72" width="58" height="74" rx="6"/><rect class="pn2" x="120" y="82" width="58" height="74" rx="6"/></g>
<g class="w" opacity=".85"><rect x="132" y="98" width="34" height="5" rx="2"/><rect x="132" y="110" width="26" height="5" rx="2"/><rect x="132" y="122" width="30" height="5" rx="2"/><rect x="132" y="134" width="20" height="5" rx="2"/></g>
<path class="wire" d="{p_in1}"/><path class="wire" d="{p_in2}"/><path class="wire" d="{p_out}"/><path class="rs" d="{p_exc}" stroke-dasharray="5 6"/>
<rect x="240" y="40" width="160" height="160" rx="22" fill="none" stroke="#6fb4d6" stroke-opacity=".45" stroke-width="1.5" stroke-dasharray="6 6"/>
<rect class="pn2" x="250" y="50" width="140" height="140" rx="18" filter="url(#sh)"/>
<path d="{edges}" stroke="#a9d8ef" stroke-opacity=".28" stroke-width="1.5"/>
<g class="tl" filter="url(#gl)">{nodes}</g>
<g filter="url(#sh)"><rect class="pn" x="430" y="46" width="116" height="84" rx="10"/><rect class="pn" x="430" y="146" width="116" height="50" rx="10" stroke="#e04848"/></g>
<g class="t"><rect class="row" x="444" y="62" width="58" height="9" rx="3"/><rect class="row" style="animation-delay:.6s" x="444" y="83" width="46" height="9" rx="3"/><rect class="row" style="animation-delay:1.2s" x="444" y="104" width="52" height="9" rx="3"/></g>
{check(514, 67)}{check(514, 88)}{check(514, 109)}
<circle class="r" cx="454" cy="171" r="11"/><path d="M454 164v8M454 177v.5" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
<text class="lb" x="472" y="177">Review</text>
{pk(p_in1, 1.6)}{pk(p_in2, 1.6, -.8)}{pk(p_out, 1.2, -.3)}{pk(p_exc, 2.4, -1, 'pkr')}''',
'''.nd{animation:pu 2.4s ease-in-out infinite}@keyframes pu{50%{opacity:.35}}
.row{animation:rw 3.6s ease-in-out infinite}@keyframes rw{0%,15%{opacity:.25}35%,100%{opacity:1}}''')

# ------------------------------------------------------------- Cloud (animated)
arcs = ['M176 80C250 80 270 100 334 106', 'M176 122C250 122 270 126 330 128', 'M176 164C250 164 284 154 346 150']
slots = ''.join(f'<rect x="112" y="{64+i*24}" width="48" height="16" rx="3" class="dk" stroke="#3f7aa0"/><circle cx="150" cy="{72+i*24}" r="2.5" class="{"t" if i!=3 else "r led"}"/>' for i in range(5))
bars = ''.join(f'<rect class="ub" style="animation-delay:{i*.25:.2f}s" x="{352+i*18}" y="166" width="12" height="32" rx="2"/>' for i in range(9))
write('cloud', 'An aging on-premises server migrating in phases into cloud compute, storage, and security, with usage that scales up and down', f'''
<ellipse cx="136" cy="198" rx="46" ry="6" fill="#000" opacity=".3"/>
<rect class="pn" x="100" y="52" width="72" height="142" rx="7" filter="url(#sh)"/>{slots}
{''.join(f'<path class="wire" d="{a}"/>' for a in arcs)}
<g class="pn2" filter="url(#sh)" stroke="none"><circle cx="372" cy="118" r="36"/><circle cx="428" cy="94" r="46"/><circle cx="486" cy="118" r="34"/><rect x="352" y="112" width="152" height="40" rx="20"/></g>
<g class="w"><rect x="370" y="116" width="26" height="26" rx="4" fill="none" stroke="#e6eff6" stroke-width="2.5"/><rect x="377" y="123" width="12" height="12" rx="2"/>
<path d="M366 124h4M366 134h4M396 124h4M396 134h4" stroke="#e6eff6" stroke-width="2.5"/>
<ellipse cx="430" cy="114" rx="14" ry="5"/><path d="M416 114v20c0 7 28 7 28 0v-20" fill="none" stroke="#e6eff6" stroke-width="2.5"/><path d="M416 124c0 7 28 7 28 0" fill="none" stroke="#e6eff6" stroke-width="2"/>
<rect x="472" y="122" width="24" height="20" rx="3"/><path d="M477 122v-6a7 7 0 0 1 14 0v6" fill="none" stroke="#e6eff6" stroke-width="2.5"/></g>
<circle cx="484" cy="132" r="3" class="dk"/>
<path d="M346 198H520" stroke="#3f7aa0" stroke-width="1.5"/><g class="t">{bars}</g>
{''.join(pk(a, 2.2, -i*.7) for i, a in enumerate(arcs))}''',
'''.ub{transform-box:fill-box;transform-origin:bottom;animation:ub 3.2s ease-in-out infinite}
@keyframes ub{0%,100%{transform:scaleY(.3)}50%{transform:scaleY(1)}}
.led{animation:bl 1.2s steps(2) infinite}@keyframes bl{50%{opacity:.2}}''')

# ------------------------------------------------------------------------ ERP
hexpts = '320,72 361.6,96 361.6,144 320,168 278.4,144 278.4,96'
tiles = [(95, 48, 'Inventory'), (405, 48, 'Orders'), (95, 134, 'Ledger'), (405, 134, 'Production')]
icons = {
 'Inventory': lambda x, y: f'<g class="t"><rect x="{x}" y="{y+12}" width="13" height="13" rx="2"/><rect x="{x+15}" y="{y+12}" width="13" height="13" rx="2"/><rect x="{x+7}" y="{y-2}" width="13" height="13" rx="2" class="tl"/></g><path d="M{x-2} {y+28}h32" stroke="#a9d8ef" stroke-width="2.5" stroke-linecap="round"/>',
 'Orders': lambda x, y: f'<rect x="{x+2}" y="{y-2}" width="24" height="30" rx="3" class="ln"/><path d="M{x+8} {y+6}h12M{x+8} {y+13}h12M{x+8} {y+20}h7" class="ln" stroke-width="2"/>',
 'Ledger': lambda x, y: f'<rect x="{x}" y="{y-1}" width="28" height="28" rx="3" class="ln"/><path d="M{x+14} {y-1}v28M{x+4} {y+8}h6M{x+4} {y+15}h6M{x+18} {y+8}h6M{x+18} {y+15}h6" class="ln" stroke-width="2"/>',
 'Production': lambda x, y: gear(x + 14, y + 13, 11),
}
conn = ['M235 77H256L284 98', 'M405 77H384L356 98', 'M235 163H256L284 142', 'M405 163H384L356 142']
write('erp', 'One ERP system of record at the center, connected to inventory, orders, the general ledger, and production', f'''
<polygon points="320,58 373.7,89 373.7,151 320,182 266.3,151 266.3,89" fill="none" stroke="#6fb4d6" stroke-opacity=".35" stroke-width="1.5" stroke-dasharray="5 5"/>
{''.join(f'<path class="wire" d="{c}"/>' for c in conn)}
<g class="t">{''.join(f'<circle cx="{c.split("H")[0][1:].split(" ")[0]}" cy="{c.split(" ")[1].split("H")[0]}" r="4"/>' for c in conn)}</g>
<g filter="url(#sh)">{''.join(f'<rect class="pn" x="{x}" y="{y}" width="140" height="58" rx="10"/>' for x, y, _ in tiles)}</g>
{''.join(icons[n](x + 14, y + 16) + f'<text class="lb" x="{x+50}" y="{y+35}" style="font-size:16px">{n}</text>' for x, y, n in tiles)}
<polygon class="pn2" points="{hexpts}" filter="url(#sh)"/>
<text class="lb" x="320" y="127" text-anchor="middle" style="font-size:21px;font-weight:700">ERP</text>
<circle class="r" cx="320" cy="72" r="5" filter="url(#gl)"/>''')

# -------------------------------------------------------------------- Finance
rows = ''
for i, (dw, cw) in enumerate([(54, 54), (40, 40), (62, 62)]):
    y = 82 + i * 26
    rows += (f'<rect class="w" opacity=".85" x="114" y="{y}" width="{dw}" height="9" rx="3"/><rect class="w" opacity=".85" x="228" y="{y}" width="{cw}" height="9" rx="3"/>'
             f'<path d="M{114+dw+6} {y+4.5}H222" stroke="#6fb4d6" stroke-width="2" stroke-dasharray="2 4"/>' + check(306, y + 4))
cells_before = ''.join(f'<rect class="td" x="{380+i*16}" y="98" width="12" height="22" rx="2"/>' for i in range(10))
cells_after = ''.join(f'<rect x="{380+i*16}" y="152" width="12" height="22" rx="2" ' +
                      ('class="tl"/>' if i < 3 else 'class="t" opacity=".55"/>' if i < 5 else 'fill="none" stroke="#3f7aa0" stroke-width="1.5"/>') for i in range(10))
write('finance', 'A ledger reconciling debits to credits with one unmatched entry flagged, beside a month-end close shortened from about ten business days to three to five', f'''
<rect class="pn" x="95" y="42" width="250" height="156" rx="10" filter="url(#sh)"/>
<path d="M95 52a10 10 0 0 1 10-10h230a10 10 0 0 1 10 10v16H95z" class="dk"/>
<text class="lb" x="114" y="62" style="font-size:15px">Dr</text><text class="lb" x="228" y="62" style="font-size:15px">Cr</text>
{rows}
<rect x="104" y="160" width="232" height="28" rx="6" fill="#e04848" fill-opacity=".16" stroke="#e04848" stroke-width="1.5"/>
<rect class="w" opacity=".85" x="114" y="170" width="48" height="9" rx="3"/><rect class="w" opacity=".85" x="228" y="170" width="34" height="9" rx="3"/>
<path class="rs" d="M168 174.5h18M204 174.5h18"/><path class="rs" d="M190 168l10 13"/><path class="rs" d="M308 168l12 12M320 168l-12 12"/>
<text class="lb" x="380" y="64">Month-end close</text>
<text class="lbs" x="380" y="90">Before</text><text class="lbs" x="536" y="90" text-anchor="end">~10 days</text>{cells_before}
<text class="lbs" x="380" y="144">After</text><text class="lbs" x="536" y="144" text-anchor="end">3–5 days</text>{cells_after}''')

# --------------------------------------------------------------- Data (animated)
pipes = ['M152 70C196 70 200 112 236 116', 'M152 122H236', 'M152 172C196 172 200 130 236 128']
heights = [34, 48, 40, 62, 54, 70, 84]
dbars = ''.join(f'<rect class="b{" r" if i == 6 else ""}" style="animation-delay:{i*.18:.2f}s" x="{364+i*24}" y="{186-h}" width="16" height="{h}" rx="2"/>' for i, h in enumerate(heights))
write('data', 'Databases, spreadsheets, and business applications feeding a data warehouse and a dashboard whose charts refresh on their own', f'''
<g filter="url(#sh)"><path class="pn" d="M100 54v32c0 8 48 8 48 0V54"/><ellipse class="pn2" cx="124" cy="54" rx="24" ry="8"/>
<rect class="pn" x="100" y="104" width="48" height="38" rx="5"/><rect class="pn" x="100" y="154" width="48" height="38" rx="5"/></g>
<path d="M100 117h48M100 129h48M116 104v38M132 104v38" stroke="#3f7aa0" stroke-width="1.5"/>
<path d="M100 164h48" stroke="#3f7aa0" stroke-width="1.5"/><g class="t"><circle cx="107" cy="159" r="2"/><rect x="108" y="172" width="30" height="5" rx="2"/><rect x="108" y="181" width="20" height="5" rx="2" opacity=".6"/></g>
{''.join(f'<path class="wire" d="{p}"/>' for p in pipes)}<path class="wire" d="M304 122H350"/>
<g filter="url(#sh)">{''.join(f'<path class="{"pn2" if i == 0 else "pn"}" d="M236 {y}l34-14 34 14-34 14z"/>' for i, y in enumerate([150, 134, 118, 102][::-1]))}</g>
<rect class="pn" x="350" y="42" width="195" height="156" rx="10" filter="url(#sh)"/>
<path d="M350 52a10 10 0 0 1 10-10h175a10 10 0 0 1 10 10v12H350z" class="dk"/>
<path class="ln rf" d="M531 49a6 6 0 1 1-6-1" stroke-width="2"/><path d="M523 45l3 3-3 3" class="ln" stroke-width="2"/>
<circle cx="380" cy="94" r="16" fill="none" stroke="#376986" stroke-width="7"/><circle cx="380" cy="94" r="16" fill="none" stroke="#6fb4d6" stroke-width="7" stroke-dasharray="70 31" transform="rotate(-90 380 94)"/>
<path class="ln sp" d="M412 108l22-12 20 6 24-20 22 6 22-18" stroke="#e6eff6"/>
<path d="M360 186H534" stroke="#3f7aa0" stroke-width="1.5"/><g class="t">{dbars}</g>
{''.join(pk(p, 1.8, -i*.6) for i, p in enumerate(pipes))}{pk("M304 122H350", 1.2, -.4)}''',
'''.b{transform-box:fill-box;transform-origin:bottom;animation:gb 4.5s ease-in-out infinite}
@keyframes gb{0%{transform:scaleY(.15)}45%,100%{transform:scaleY(1)}}
.sp{stroke-dasharray:140;animation:dr 4.5s ease-in-out infinite}@keyframes dr{0%{stroke-dashoffset:140}55%,100%{stroke-dashoffset:0}}
.rf{transform-box:fill-box;transform-origin:center;animation:rot 4.5s linear infinite}@keyframes rot{to{transform:rotate(360deg)}}''')

# ------------------------------------------------------------------------ Dev
code = [(0, 30, 't'), (1, 56, 'tl'), (2, 40, 'w'), (2, 72, 't'), (1, 34, 'tl'), (0, 18, 't')]
code_svg = ''.join(f'<rect x="104" y="{78+i*18}" width="10" height="6" rx="2" class="td"/><rect class="{c}" x="{124+ind*16}" y="{77+i*18}" width="{w}" height="8" rx="3"/>' for i, (ind, w, c) in enumerate(code))
write('dev', 'A code editor with a reviewed change, connected through an API to a web application and a mobile app', f'''
<rect class="pn" x="95" y="42" width="215" height="156" rx="10" filter="url(#sh)"/>
<path d="M95 52a10 10 0 0 1 10-10h195a10 10 0 0 1 10 10v10H95z" class="dk"/>
<circle class="r" cx="108" cy="52" r="4"/><circle class="t" cx="121" cy="52" r="4" opacity=".6"/><circle class="t" cx="134" cy="52" r="4" opacity=".3"/>
<rect x="100" y="128" width="205" height="16" fill="#6fb4d6" fill-opacity=".14"/>
{code_svg}
<circle cx="284" cy="174" r="13" class="tl" filter="url(#gl)"/><path d="M278 174l4 4 8-9" fill="none" stroke="#14263a" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path class="wire" d="M310 120H334M380 120H404"/>
<rect class="pn2" x="334" y="98" width="46" height="44" rx="10" filter="url(#sh)"/>
<text class="lb" x="357" y="126" text-anchor="middle" style="font-size:15px;font-weight:700">API</text>
<g filter="url(#sh)"><rect class="pn" x="404" y="46" width="124" height="104" rx="8"/></g>
<path d="M404 54a8 8 0 0 1 8-8h108a8 8 0 0 1 8 8v6H404z" class="dk"/>
<rect class="t" x="416" y="70" width="100" height="18" rx="3"/><rect class="td" x="416" y="96" width="46" height="42" rx="4"/><rect class="td" x="470" y="96" width="46" height="18" rx="4"/><rect class="td" x="470" y="120" width="46" height="18" rx="4"/>
<rect class="pn2" x="488" y="104" width="56" height="94" rx="10" filter="url(#sh)"/>
<rect class="tl" x="497" y="118" width="38" height="10" rx="3"/><rect class="t" x="497" y="134" width="38" height="22" rx="3" opacity=".7"/><rect class="t" x="497" y="162" width="38" height="22" rx="3" opacity=".7"/>''')

# ------------------------------------------------------------------- Strategy
phases = ['Assess', 'Secure', 'Modernize', 'Automate']
fills = ['#2a5274', '#33658e', '#3f7aa8', '#4f8fbf']
icon_s = [
 lambda cx: f'<circle cx="{cx-3}" cy="68" r="9" class="ln"/><path class="ln" d="M{cx+4} 75l7 7"/>',
 lambda cx: f'<path class="ln" d="M{cx} 56l13 5v9c0 8-6 13-13 16-7-3-13-8-13-16v-9z"/>',
 lambda cx: f'<path class="ln" d="M{cx-14} 64l14-7 14 7-14 7z"/><path class="ln" d="M{cx-14} 72l14 7 14-7M{cx-14} 80l14 7 14-7"/>',
 lambda cx: gear(cx, 71, 11),
]
chev = ''
for i, (p, f) in enumerate(zip(phases, fills)):
    x = 95 + i * 108
    notch = f'{x+14},120' if i else f'{x},120'
    chev += (f'<polygon points="{x},98 {x+108},98 {x+122},120 {x+108},142 {x},142 {notch}" fill="{f}" stroke="#6fb4d6" stroke-opacity=".5"/>'
             f'<text class="lb" x="{x+(64 if i else 57)}" y="126" text-anchor="middle" style="font-size:15px">{p}</text>' + icon_s[i](x + (64 if i else 57)))
ticks = ''.join(f'<path d="M{x} 154v8" stroke="#6fb4d6" stroke-width="2"/><text class="lbs" x="{x}" y="182" text-anchor="{a}">{t}</text>'
                for x, t, a in [(95, 'Month 0', 'start'), (244, '6', 'middle'), (392, '12', 'middle'), (541, '18', 'end')])
write('strategy', 'A twelve-to-eighteen-month technology roadmap sequenced in four phases: assess, secure, modernize, automate', f'''
<g filter="url(#sh)">{chev}</g>
<path d="M95 158H541" stroke="#3f7aa0" stroke-width="1.5"/>{ticks}
<path class="r" d="M95 146l6 8h-12z"/>''')

# --------------------------------------------------------- Managed IT (animated)
hb = 'M108 104h60l10-26 16 54 14-40 10 12h64l10-26 16 54 14-40 10 12h18'
devices = [
 lambda x: f'<rect class="pn" x="{x}" y="164" width="38" height="24" rx="3"/><path d="M{x-6} 192h50" stroke="#6fb4d6" stroke-width="3" stroke-linecap="round"/>',
 lambda x: f'<rect class="pn" x="{x}" y="160" width="40" height="28" rx="3"/><path d="M{x+20} 188v6M{x+10} 196h20" stroke="#6fb4d6" stroke-width="3" stroke-linecap="round"/>',
 lambda x: f'<rect class="pn" x="{x+4}" y="156" width="32" height="42" rx="3"/><path d="M{x+10} 166h20M{x+10} 176h20M{x+10} 186h20" stroke="#3f7aa0" stroke-width="2"/>',
 lambda x: f'<rect class="pn" x="{x+10}" y="158" width="22" height="38" rx="4"/>',
]
dev_svg = ''.join(d(110 + i * 64) + f'<circle class="{"st" if i == 2 else "t ok"}" style="animation-delay:{i*.4:.1f}s" cx="{150+i*64}" cy="160" r="5" filter="url(#gl)"/>' for i, d in enumerate(devices))
write('managed-it', 'A monitoring screen with a live heartbeat, managed laptops, desktops, servers, and phones with their status lights, and a security shield', f'''
<rect class="pn" x="95" y="42" width="265" height="100" rx="10" filter="url(#sh)"/>
<path d="M108 72H347M108 104H347M108 128H347" stroke="#3f7aa0" stroke-opacity=".45" stroke-width="1"/>
<path class="ln" d="{hb}" stroke="#376986"/><path class="ln hb" d="{hb}" stroke="#a9d8ef"/>
{pk(hb, 3.2)}
{dev_svg}
<circle class="ring" cx="470" cy="120" r="64" fill="none" stroke="#6fb4d6" stroke-width="2"/>
<path class="pn2" filter="url(#sh)" d="M470 46l62 20v50c0 40-28 64-62 78-34-14-62-38-62-78V66z"/>
<path d="M444 120l17 17 34-36" fill="none" stroke="#a9d8ef" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" filter="url(#gl)"/>''',
'''.hb{stroke-dasharray:520;animation:hb 3.2s linear infinite}@keyframes hb{0%{stroke-dashoffset:520}100%{stroke-dashoffset:0}}
.ok{animation:bl 2.4s ease-in-out infinite}@keyframes bl{50%{opacity:.35}}
.st{fill:#e04848;animation:fx 6s ease-in-out infinite}@keyframes fx{0%,35%{fill:#e04848}50%,100%{fill:#6fb4d6}}
.ring{transform-box:fill-box;transform-origin:center;animation:rg 3s ease-out infinite}@keyframes rg{0%{transform:scale(.75);opacity:.7}100%{transform:scale(1.25);opacity:0}}''')

if CHECK:
    if STALE:
        sys.exit(f"stale service illustrations: {', '.join(STALE)} — run python3 scripts/generate_service_illustrations.py")
    print('service illustrations up to date')
