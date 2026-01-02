import argparse
import os
import shutil
import time


class DiskSpeed:
    UNITS = {"B": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}

    def __init__(self, test_path: str, test_size: str = "1G", chunk_size: str = "100M"):
        self.test_path = test_path
        self.test_size = self.as_bytes(test_size)
        self.chunk_size = self.as_bytes(chunk_size)

    def as_bytes(self, size: str):
        """
        Strip unit from number and multiply by factor: 100M -> 100 * 1024**2 = 104857600
        """
        for unit, factor in DiskSpeed.UNITS.items():
            if str(size).endswith(unit):
                return int(size[:-1]) * factor

    def check_space(self):
        """
        Check if there's sufficient space to write the test_file in the specified size.
        """
        wd = self.test_path
        free_space = shutil.disk_usage(wd).free

        if self.test_size >= free_space:
            raise RuntimeError("Not enough free space!")

    def test_diskspeed(self):
        null_byte = b"\0"
        file_name = "diskspeed.tmp"

        self.check_space()

        chunks = range(int(self.test_size / self.chunk_size))

        try:
            # --
            print("Write speed:", end=" ")
            with open(file_name, "wb") as f:
                time_start = time.perf_counter()
                for _ in chunks:
                    f.write(null_byte * self.chunk_size)

            time_duration = time.perf_counter() - time_start
            gbps = (self.test_size / self.UNITS["G"]) / time_duration
            mbps = (self.test_size / self.UNITS["M"]) / time_duration
            print(f"{gbps:.3f} GB/s - ({mbps:.3f})")

            # --
            print("read speed:", end=" ")
            with open(file_name, "rb") as f:
                time_start = time.perf_counter()
                for _ in chunks:
                    f.read()
            time_duration = time.perf_counter() - time_start
            gbps = (self.test_size / self.units["g"]) / time_duration
            mbps = (self.test_size / self.units["m"]) / time_duration
            print(f"{gbps:.3f} gb/s - ({mbps:.0f} mb/s)")

        except KeyboardInterrupt:
            pass

        finally:
            if os.path.exists(file_name):
                os.remove(file_name)


def main():
    parser = argparse.ArgumentParser(description="Measure read/write speed on disk.")

    parser.add_argument(
        "-p",
        "--path",
        type=str,
        default=os.getcwd(),
        help="Path to the measure target (disk)",
    )
    parser.add_argument(
        "-t",
        "--test-size",
        type=str,
        default="1G",
        help="How large a file to write in the test size",
    )
    parser.add_argument(
        "-c",
        "--chunk-size",
        type=str,
        default="100M",
        help="Test file is written in chunks of 100M - use this option to override the default value",
    )

    args = parser.parse_args()
    diskspeed = DiskSpeed(
        test_path=args.path, test_size=args.test_size, chunk_size=args.chunk_size
    )
    diskspeed.test_diskspeed()


if __name__ == "__main__":
    main()
