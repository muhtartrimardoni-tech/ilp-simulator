"""Model data & skenario instruksi (Anggota 1)."""
from dataclasses import dataclass, field


@dataclass
class Instruction:
    name: str
    destination: str
    sources: list = field(default_factory=list)

    def __str__(self):
        return f"{self.name}: {self.destination} = {' + '.join(self.sources)}"


@dataclass
class Dependency:
    src: str   # instruksi lebih awal (urutan program)
    dst: str   # instruksi lebih akhir
    kind: str  # "RAW" | "WAR" | "WAW"
    reg: str   # register penyebab dependensi


# Satu skenario murni per jenis hazard + satu skenario campuran
SCENARIOS = {
    "RAW": [
        Instruction("I1", "R1", ["R2", "R3"]),
        Instruction("I2", "R4", ["R5", "R6"]),
        Instruction("I3", "R7", ["R1", "R4"]),
        Instruction("I4", "R8", ["R9", "R10"]),
        Instruction("I5", "R11", ["R7", "R8"]),
        Instruction("I6", "R12", ["R13", "R14"]),
    ],
    "WAR": [
        Instruction("I1", "R4", ["R1", "R2"]),
        Instruction("I2", "R1", ["R5", "R6"]),    # tulis R1 yang dibaca I1
        Instruction("I3", "R7", ["R2", "R3"]),
        Instruction("I4", "R2", ["R8", "R9"]),    # tulis R2 yang dibaca I1 & I3
        Instruction("I5", "R10", ["R11", "R12"]),
    ],
    "WAW": [
        Instruction("I1", "R1", ["R2", "R3"]),
        Instruction("I2", "R1", ["R4", "R5"]),    # tulis ulang R1
        Instruction("I3", "R6", ["R7", "R8"]),
        Instruction("I4", "R1", ["R9", "R10"]),   # tulis ulang R1 lagi
        Instruction("I5", "R6", ["R11", "R12"]),  # tulis ulang R6
    ],
    "MIXED": [
        Instruction("I1", "R1", ["R2", "R3"]),
        Instruction("I2", "R4", ["R1", "R5"]),
        Instruction("I3", "R2", ["R6", "R7"]),
        Instruction("I4", "R1", ["R8", "R9"]),
        Instruction("I5", "R10", ["R4", "R1"]),
        Instruction("I6", "R11", ["R12", "R13"]),
    ],
}

SCENARIO_TITLES = {
    "RAW": "RAW (Read After Write) - True Dependency",
    "WAR": "WAR (Write After Read) - Anti Dependency",
    "WAW": "WAW (Write After Write) - Output Dependency",
    "MIXED": "Gabungan RAW + WAR + WAW",
}
