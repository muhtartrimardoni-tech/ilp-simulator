"""Eksekusi sequential & ILP (Anggota 2)."""


def sequential_execution(instructions, verbose=True):
    if verbose:
        print("\n" + "=" * 50)
        print("SEQUENTIAL EXECUTION")
        print("=" * 50)
        for c, inst in enumerate(instructions, 1):
            print(f"Cycle {c}: Executing {inst}")
        print(f"\nTotal Sequential Cycles: {len(instructions)}")
    return len(instructions)


def schedule(instructions, deps, renaming=False):
    """
    Penjadwalan ASAP: instruksi dijalankan di cycle setelah SEMUA
    dependensinya selesai.

    renaming=False : RAW, WAR, WAW semuanya menjadi batasan urutan.
    renaming=True  : WAR & WAW (name dependency) hilang karena register
                     di-rename; hanya RAW (true dependency) yang tersisa.
    """
    active = [d for d in deps if (not renaming or d.kind == "RAW")]
    cycle_of = {}
    for inst in instructions:  # urutan program sudah topologis
        preds = [cycle_of[d.src] for d in active if d.dst == inst.name]
        cycle_of[inst.name] = (max(preds) + 1) if preds else 1
    return cycle_of


def parallel_execution(instructions, deps, renaming=False, verbose=True):
    cycle_of = schedule(instructions, deps, renaming)
    total = max(cycle_of.values())
    if verbose:
        label = "DENGAN REGISTER RENAMING" if renaming else "TANPA RENAMING"
        print("\n" + "=" * 50)
        print(f"INSTRUCTION-LEVEL PARALLEL EXECUTION ({label})")
        print("=" * 50)
        for c in range(1, total + 1):
            print(f"\nCycle {c}:")
            for inst in instructions:
                if cycle_of[inst.name] == c:
                    print(f"  -> {inst}")
        print(f"\nTotal ILP Cycles: {total}")
    return total, cycle_of
