"""Dependency graph (Anggota 2).

Utama: Graphviz (`dot`) -> layout rapi tanpa garis menembus node.
Cadangan: matplotlib jika `dot` tidak terpasang.
"""
import shutil
import subprocess
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

COLORS = {"RAW": "#d62728", "WAR": "#1f77b4", "WAW": "#2ca02c"}


def _layout(instructions, cycle_of):
    layers = {}
    for inst in instructions:
        layers.setdefault(cycle_of[inst.name], []).append(inst.name)
    pos = {}
    for lvl, names in layers.items():
        for k, n in enumerate(names):
            pos[n] = (lvl * 3.2, (len(names) - 1) / 2 * 1.9 - k * 1.9)
    return pos


def draw_graph_matplotlib(instructions, deps, cycle_of, title, path):
    pos = _layout(instructions, cycle_of)
    by_name = {i.name: i for i in instructions}
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]

    fig, ax = plt.subplots(figsize=(max(7, (max(xs) - min(xs)) * 1.1 + 4), max(4.5, (max(ys) - min(ys)) * 0.9 + 3)))
    ax.set_title(title, fontsize=13, fontweight="bold")
    w, h = 2.3, 1.0

    for d in deps:
        (x1, y1), (x2, y2) = pos[d.src], pos[d.dst]
        skip = cycle_of[d.dst] - cycle_of[d.src] > 1
        rad = 0.0 if not skip else (0.35 if y1 >= y2 else -0.35)
        arrow = FancyArrowPatch(
            (x1 + w / 2, y1), (x2 - w / 2, y2), connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>", mutation_scale=16, lw=2, color=COLORS[d.kind], zorder=1,
            shrinkA=0, shrinkB=2)
        ax.add_patch(arrow)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + rad * (x2 - x1) * -0.5
        ax.text(mx, my + 0.18, f"{d.kind} ({d.reg})", color=COLORS[d.kind], fontsize=8.5,
                ha="center", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9), zorder=3)

    for n, (x, y) in pos.items():
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.05",
                                    fc="#f4f4f4", ec="#333", lw=1.4, zorder=2))
        inst = by_name[n]
        ax.text(x, y + 0.2, n, ha="center", va="center", fontsize=11, fontweight="bold", zorder=4)
        ax.text(x, y - 0.2, f"{inst.destination} = {' + '.join(inst.sources)}",
                ha="center", va="center", fontsize=9, zorder=4)

    for lvl in sorted({cycle_of[n] for n in pos}):
        ax.text(lvl * 3.2, max(ys) + 1.4, f"Cycle {lvl}", ha="center", fontsize=10, color="#555")

    kinds_used = sorted({d.kind for d in deps})
    handles = [plt.Line2D([0], [0], color=COLORS[k], lw=3, label=k) for k in kinds_used]
    if handles:
        ax.legend(handles=handles, loc="lower right", title="Jenis dependensi")
    ax.set_xlim(min(xs) - 2, max(xs) + 2)
    ax.set_ylim(min(ys) - 1.5, max(ys) + 2.2)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def to_dot(instructions, deps, cycle_of, title):
    """Bangun teks DOT; node sekelas (cycle sama) diberi rank=same."""
    lines = [
        "digraph G {",
        '  rankdir=LR; nodesep=0.6; ranksep=1.3; splines=true;',
        f'  labelloc=t; fontsize=18; fontname="Helvetica-Bold"; label="{title}";',
        '  node [shape=box, style="rounded,filled", fillcolor="#f4f4f4", fontname="Helvetica", fontsize=12];',
        '  edge [fontname="Helvetica-Bold", fontsize=11, penwidth=2];',
    ]
    for inst in instructions:
        lbl = f"{inst.name}\\n{inst.destination} = {' + '.join(inst.sources)}"
        lines.append(f'  {inst.name} [label="{lbl}"];')
    for c in sorted(set(cycle_of.values())):
        names = " ".join(f"{n};" for n, v in cycle_of.items() if v == c)
        lines.append(f'  {{ rank=same; {names} }}')
    for d in deps:
        col = COLORS[d.kind]
        lines.append(f'  {d.src} -> {d.dst} [label="{d.kind} ({d.reg})", color="{col}", fontcolor="{col}"];')
    lines.append("}")
    return "\n".join(lines)


def draw_graph(instructions, deps, cycle_of, title, path):
    if shutil.which("dot"):
        dot_path = path.rsplit(".", 1)[0] + ".dot"
        with open(dot_path, "w") as f:
            f.write(to_dot(instructions, deps, cycle_of, title))
        subprocess.run(["dot", "-Tpng", "-Gdpi=160", dot_path, "-o", path], check=True)
    else:
        draw_graph_matplotlib(instructions, deps, cycle_of, title, path)
