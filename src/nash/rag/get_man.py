#!/usr/bin/env python3

import os
import lzma
import gzip
import tarfile
import subprocess
import tempfile
import urllib.request
import threading

from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


DESTDIR = Path("./man_pages/")
MIRROR = "https://deb.debian.org/debian/"
PKG_AMD64 = "dists/forky/main/binary-amd64/Packages.xz"

PKGLIST = DESTDIR / "packages"
PROCESSED = DESTDIR / "processed"
LOGFILE = DESTDIR / "get_man.log"

MAX_WORKERS = 18

log_lock = threading.Lock()
processed_lock = threading.Lock()
processed_set = set()


def log(message: str):
    now = datetime.now().strftime("%H:%M")
    line = f"[{now}] {message}"

    with log_lock:
        print(line)
        with LOGFILE.open("a") as f:
            f.write(line + "\n")


def init():
    DESTDIR.mkdir(parents=True, exist_ok=True)
    LOGFILE.touch(exist_ok=True)
    PROCESSED.touch(exist_ok=True)

    # Load processed into memory once
    global processed_set
    with PROCESSED.open() as f:
        processed_set = {line.strip() for line in f if line.strip()}


def mark_processed(pkgname: str):
    with processed_lock:
        if pkgname in processed_set:
            return
        processed_set.add(pkgname)
        with PROCESSED.open("a") as f:
            f.write(pkgname + "\n")


def is_processed(pkgname: str) -> bool:
    with processed_lock:
        return pkgname in processed_set


def download_package_list(url: str):
    log(f"Downloading package list: {url}")

    with urllib.request.urlopen(url) as response:
        compressed = response.read()
        decompressed = lzma.decompress(compressed).decode()

    with PKGLIST.open("w") as f:
        for line in decompressed.splitlines():
            if line.startswith("Filename:"):
                f.write(line.split(":", 1)[1].strip() + "\n")


def extract_ar_archive(ar_path: Path, extract_dir: Path):
    subprocess.run(
        ["ar", "x", str(ar_path)],
        cwd=extract_dir,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def extract_tar_archive(tmpdir: Path):
    for file in tmpdir.glob("data.tar.*"):
        if file.suffix == ".xz":
            with lzma.open(file) as f:
                with tarfile.open(fileobj=f) as tar:
                    tar.extractall(path=tmpdir, filter="data")
        else:
            with tarfile.open(file) as tar:
                tar.extractall(path=tmpdir, filter="data")


def process_package(pkg_path: str):
    pkgfile = Path(pkg_path).name
    pkgname = pkgfile.split("_")[0]

    if is_processed(pkgname):
        log(f"{pkgname}: Already processed")
        return

    try:
        log(f"{pkgname}: Downloading")

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)

            # download
            url = MIRROR + pkg_path
            pkg_local = tmpdir / pkgfile
            urllib.request.urlretrieve(url, pkg_local)

            # extract
            extract_ar_archive(pkg_local, tmpdir)
            extract_tar_archive(tmpdir)

            man_dir = tmpdir / "usr/share/man"
            if not man_dir.exists():
                log(f"{pkgname}: No man pages")
                mark_processed(pkgname)
                return

            for manfile in man_dir.rglob("*"):
                if not manfile.is_file():
                    continue

                if manfile.suffix == ".gz":
                    decompressed = manfile.with_suffix("")
                    with gzip.open(manfile, "rb") as f_in:
                        decompressed.write_bytes(f_in.read())
                    manfile.unlink()
                    manfile = decompressed

                txt_relative = manfile.relative_to(tmpdir)
                txt_path = DESTDIR / txt_relative
                txt_path = txt_path.with_suffix(txt_path.suffix + ".txt")

                txt_path.parent.mkdir(parents=True, exist_ok=True)

                with open(txt_path, "w") as out:
                    subprocess.run(
                        ["man", "-P", "cat", str(manfile)],
                        stdout=out,
                        stderr=subprocess.DEVNULL,
                        check=True,
                        env={**os.environ, "COLUMNS": "1024"},
                    )

        mark_processed(pkgname)
        log(f"{pkgname}: Done")

    except Exception as e:
        log(f"{pkgname}: FAILED -> {e}")


def main():
    init()
    log("Starting")

    download_package_list(MIRROR + PKG_AMD64)

    with PKGLIST.open() as f:
        packages = [line.strip() for line in f if line.strip()]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_package, pkg) for pkg in packages]

        for _ in as_completed(futures):
            pass


if __name__ == "__main__":
    main()