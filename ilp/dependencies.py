"""Deteksi dependensi RAW, WAR, WAW (Anggota 1)."""
from .models import Dependency


def detect_dependencies(instructions):
    """
    Mengembalikan list Dependency (src -> dst, src lebih awal di program).

    RAW: j MEMBACA register yang terakhir DITULIS i        (i.dest in j.sources)
    WAR: j MENULIS register yang sebelumnya DIBACA i       (j.dest in i.sources)
    WAW: j MENULIS register yang sebelumnya DITULIS i      (j.dest == i.dest)

    Pencarian mundur berhenti di penulis terdekat, sehingga tidak ada
    dependensi palsu yang melewati penulisan ulang register.
    """
    deps = []
    for j, inst in enumerate(instructions):
        # --- RAW: cari penulis terakhir untuk tiap source ---
        for reg in dict.fromkeys(inst.sources):
            for i in range(j - 1, -1, -1):
                if instructions[i].destination == reg:
                    deps.append(Dependency(instructions[i].name, inst.name, "RAW", reg))
                    break

        # --- WAR & WAW: lihat siapa yang memakai register tujuan sebelumnya ---
        reg = inst.destination
        for i in range(j - 1, -1, -1):
            prev = instructions[i]
            if prev.destination == reg:
                deps.append(Dependency(prev.name, inst.name, "WAW", reg))
                break  # penulis sebelumnya sudah menjadi batas
            if reg in prev.sources:
                deps.append(Dependency(prev.name, inst.name, "WAR", reg))
    return deps


def show_dependencies(instructions, deps):
    print("\n" + "=" * 50)
    print("DEPENDENCY ANALYSIS")
    print("=" * 50)
    if not deps:
        print("No dependencies found.")
        return
    for d in deps:
        print(f"{d.dst} depends on {d.src}  [{d.kind}] (Register: {d.reg})")
