import os
import subprocess
from pathlib import Path

SOURCE = Path("/usr/share/man/man1/")
DESTINATION = Path("./man_pages/")

def init():
    DESTINATION.mkdir(parents=True, exist_ok=True)

def convert_man_file(source, destination: Path):
    try:
        with destination.open("w") as out:
            print("Hi")
            subprocess.run(
                ["man", "-l", str(source)],
                stdout=out,
                check=True,
                stderr=subprocess.DEVNULL,
                env={**os.environ, "COLUMNS": "1024"},
            )
    except Exception as e:
        print(f"FAILED: {source} -> {e}")

def main():
    init()

    man_files = [
        f for f in os.listdir(str(SOURCE)) if os.path.isfile(SOURCE / f)
    ]

    idx = 0
    for file in man_files:
      idx += 1
      print(f"Current = {idx}", end="\n")
      convert_man_file(SOURCE / file, (DESTINATION / file).with_suffix(".txt"))


if __name__ == "__main__":
    main()