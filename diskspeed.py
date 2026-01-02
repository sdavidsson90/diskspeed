import os
import time
import shutil

UNITS = {"B": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}


def make_in_to_bytes(chunk_size: str | int):
    for unit, factor in UNITS.items():
        if str(chunk_size).endswith(unit):
            return int(chunk_size[:-1]) * factor


def make_human_readable(bytes: int):
    for unit, factor in UNITS.items():
        if bytes >= factor:
            value = int(bytes / factor)
            return f"{value:.2f} {unit}"

def test():
    file_name = "diskspeed.tmp"

    file_size = "1G"
    file_size = make_in_to_bytes(file_size)

    chunk_size = "1G"
    chunk_size = make_in_to_bytes(chunk_size)

    chunks = range(int(file_size / chunk_size))

    wd = os.getcwd()
    free_space = shutil.disk_usage(wd).free

    if file_size >= free_space:
        raise RuntimeError("Not enough free space!")

    # WRITE
    null_byte = b"\0"
    with open(file_name, "wb") as f:
        time_start = time.perf_counter()
        for _ in chunks:
            f.write(null_byte * chunk_size)

    time_stop = time.perf_counter() - time_start
    write_speed = (file_size / UNITS["G"]) / time_stop
    print(f"Write speed: {write_speed:.3f} GB/s")

    # READ
    with open(file_name, "rb") as f:
        time_start = time.perf_counter()
        for _ in chunks:
            f.read()

    time_stop = time.perf_counter() - time_start
    write_speed = (file_size / UNITS["G"]) / time_stop
    print(f"Read speed: {write_speed:.3f} GB/s")

    os.remove(file_name)

if __name__ == "__main__":
    test()
