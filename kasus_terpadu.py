"""Kasus terpadu RAW + WAR + WAW (tambahan, opsional).

Jalankan: python kasus_terpadu.py   -> gambar masuk ke folder graphs_terpadu/
"""
import os

from ilp.models import Instruction
from ilp.dependencies import detect_dependencies, show_dependencies
from ilp.scheduler import sequential_execution, parallel_execution
from ilp.graph import draw_graph

OUT_DIR = "graphs_terpadu"

CASE = [
    Instruction("I1", "R1",  ["R2", "R3"]),    # tulis R1, baca R2
    Instruction("I2", "R4",  ["R1", "R5"]),    # RAW: baca R1 dari I1
    Instruction("I3", "R2",  ["R6", "R7"]),    # WAR: tulis R2 yang dibaca I1
    Instruction("I4", "R1",  ["R8", "R9"]),    # WAW: tulis ulang R1 (I1); WAR: R1 dibaca I2
    Instruction("I5", "R10", ["R4", "R1"]),    # RAW: R4 dari I2, R1 dari I4
    Instruction("I6", "R11", ["R12", "R13"]),  # independen
]
CASE_TITLE = "Kasus Terpadu RAW + WAR + WAW"

def schedule_only(instructions, deps, kinds):
    """Jadwal ASAP yang hanya memperhitungkan dependensi jenis `kinds`."""
    active = [d for d in deps if d.kind in kinds]
    cyc = {}
    for inst in instructions:
        preds = [cyc[d.src] for d in active if d.dst == inst.name]
        cyc[inst.name] = (max(preds) + 1) if preds else 1
    return active, cyc

def run_case(instructions=CASE, title=CASE_TITLE):
    print("Instruction Set:")
    for i in instructions: print(" ", i)

    deps = detect_dependencies(instructions)
    show_dependencies(instructions, deps)
    seq = sequential_execution(instructions)
    ilp, cyc_all = parallel_execution(instructions, deps, renaming=False)
    ilp_rn, _    = parallel_execution(instructions, deps, renaming=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    paths = {}
    # Satu graph per implementasi hazard
    for kind, label in [("RAW", "RAW (True Dependency)"),
                        ("WAR", "WAR (Anti Dependency)"),
                        ("WAW", "WAW (Output Dependency)")]:
        active, cyc = schedule_only(instructions, deps, {kind})
        p = os.path.join(OUT_DIR, f"kasus_terpadu_{kind.lower()}.png")
        draw_graph(instructions, active, cyc, f"{title} - hanya {label}", p)
        paths[kind] = p
        print(f"[{kind}] {len(active)} dependensi -> {p}")
    # Graph gabungan
    p = os.path.join(OUT_DIR, "kasus_terpadu_gabungan.png")
    draw_graph(instructions, deps, cyc_all, f"{title} - Gabungan", p)
    paths["GABUNGAN"] = p

    print("\n" + "=" * 50); print("PERFORMANCE COMPARISON"); print("=" * 50)
    print(f"Sequential Cycles        : {seq}")
    print(f"ILP Cycles (no renaming) : {ilp}   Speedup {seq/ilp:.2f}x  IPC {len(instructions)/ilp:.2f}")
    print(f"ILP Cycles (renaming)    : {ilp_rn}   Speedup {seq/ilp_rn:.2f}x  IPC {len(instructions)/ilp_rn:.2f}")
    return deps, paths

if __name__ == "__main__":
    run_case()
