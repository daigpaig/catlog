from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA_GEN = ROOT / "data_gen"

def data_file(name: str) -> Path:
    return DATA / name

def data_gen_file(*parts: str) -> Path:
    return DATA_GEN.joinpath(*parts)


