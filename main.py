"""Copy the front page this repository holds to /output/entry.png.

Deterministic by construction: the image is a fixed file in the repository, so
two runs write identical bytes. No network, no clock, no randomness.
"""
from pathlib import Path
import os
import shutil

HERE = Path(__file__).resolve().parent
OUTDIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    source = HERE / "entry.png"
    target = OUTDIR / "entry.png"
    shutil.copyfile(source, target)
    print("wrote %s (%d bytes)" % (target, target.stat().st_size))


if __name__ == "__main__":
    main()
