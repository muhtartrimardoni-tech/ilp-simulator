"""Program utama: jalankan simulator untuk RAW, WAR, WAW, dan MIXED."""
import os

from ilp.models import SCENARIOS, SCENARIO_TITLES
from ilp.dependencies import detect_dependencies, show_dependencies
from ilp.scheduler import sequential_execution, parallel_execution
from ilp.graph import draw_graph

OUT_DIR = "graphs"


def run(name):
    instructions = SCENARIOS[name]
    print("\n" + "*" * 60)
    print(f"  SKENARIO {SCENARIO_TITLES[name]}")
    print("*" * 60)
    print("\nInstruction Set:")
    for inst in instructions:
        print(inst)

    deps = detect_dependencies(instructions)
    show_dependencies(instructions, deps)

    seq = sequential_execution(instructions)
    ilp, cycle_of = parallel_execution(instructions, deps, renaming=False)
    ilp_rn, _ = parallel_execution(instructions, deps, renaming=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"dependency_graph_{name.lower()}.png")
    draw_graph(instructions, deps, cycle_of, f"Dependency Graph - {SCENARIO_TITLES[name]}", path)

    print("\n" + "=" * 50)
    print("PERFORMANCE COMPARISON")
    print("=" * 50)
    print(f"Sequential Cycles        : {seq}")
    print(f"ILP Cycles (no renaming) : {ilp}   Speedup {seq / ilp:.2f}x  IPC {len(instructions) / ilp:.2f}")
    print(f"ILP Cycles (renaming)    : {ilp_rn}   Speedup {seq / ilp_rn:.2f}x  IPC {len(instructions) / ilp_rn:.2f}")
    print(f"Graph disimpan di        : {path}")
    return dict(name=name, instructions=instructions, deps=deps, seq=seq, ilp=ilp, ilp_rn=ilp_rn, graph=path)


if __name__ == "__main__":
    for s in SCENARIOS:
        run(s)
