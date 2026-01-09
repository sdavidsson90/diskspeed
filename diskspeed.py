import argparse
import os
import shutil
import statistics
import time
from pathlib import Path


class DiskSpeed:
    UNITS = {"B": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}

    def __init__(self, block_size: str = "500M", iterations: int = 10, path: str = ""):
        self.block_size = self.as_bytes(block_size)
        self.iterations = iterations
        self.path = path

    @staticmethod
    def as_bytes(size: str):
        """
        Strip unit from number and multiply by factor: 100M -> 100 * 1024**2 = 104857600
        """
        for unit, factor in DiskSpeed.UNITS.items():
            if str(size).endswith(unit):
                return int(size[:-1]) * factor

    @property
    def which_disk(self):
        path = Path(self.path).resolve()
        while not path.is_mount():
            path = path.parent
        return path

    def check_space(self):
        """
        Check if there's sufficient space to write the test_file in the specified size.
        """
        wd = self.path
        free_space = shutil.disk_usage(wd).free

        if self.block_size >= free_space:
            raise RuntimeError("Not enough free space!")

    def spread():
        print("▁▂▃▄▅▆▇█")
        raise NotImplementedError

    def test_diskspeed(self):
        tmp_file = Path("diskspeed.tmp")

        self.check_space()

        # file_content = b"\0" * self.block_size # Null bytes
        file_content = os.urandom(self.block_size)  # Randomness


        print(f"Test parameters:")
        print(f"  Mount point: {self.which_disk}")
        print(f"  Block_size: {self.block_size}")
        print(f"  Iterations: {self.iterations}")
        print()

        try:

            # -------------------------------------
            gbps_measurements = []
            mbps_measurements = []
            print("Write speed:")
            with open(tmp_file, "wb") as f:
                time_start = time.perf_counter()
                for i in range(self.iterations):
                    progress_pct = (i / self.iterations) * 100
                    time_lap_start = time.perf_counter()
                    f.write(file_content)
                    time_lap_duration = time.perf_counter() - time_lap_start
                    try:
                        gbps = (self.block_size / self.UNITS["G"]) / time_lap_duration
                        mbps = (self.block_size / self.UNITS["M"]) / time_lap_duration
                    except:
                        # In case time_lap_duration is 0
                        pass
                    print(
                        f"\r{progress_pct:.2f} %: {gbps:.3f} GB/s ({mbps:.0f} MB/s)",
                        end="",
                        flush=True,
                    )
                    gbps_measurements.append(gbps)
                    mbps_measurements.append(mbps)
                    f.seek(0)

            gbps_mean = statistics.mean(gbps_measurements)
            gbps_min = min(gbps_measurements)
            gbps_max = max(gbps_measurements)

            mbps_mean = statistics.mean(mbps_measurements)
            mbps_min = min(mbps_measurements)
            mbps_max = max(mbps_measurements)


            print("", end="\r", flush=True)
            print(f"  mean: {gbps_mean:.3f} gb/s ({mbps_mean:.0f} mb/s)")
            print(f"  min: {gbps_min:.3f} gb/s ({mbps_min:.0f} mb/s)")
            print(f"  max: {gbps_max:.3f} gb/s ({mbps_max:.0f} mb/s)")
            try:
                gbps_stdev = statistics.stdev(gbps_measurements)
                mbps_stdev = statistics.stdev(mbps_measurements)
                print(
                    f"  standard deviation: {gbps_stdev:.3f} gb/s ({mbps_stdev:.0f} mb/s)"
                )
            except:
                pass

            # -------------------------------------
            print()
            gbps_measurements = []
            mbps_measurements = []
            print("Read speed:")
            with open(tmp_file, "rb") as f:
                time_start = time.perf_counter()
                # for i in range(self.iterations):
                for i in range(self.iterations):
                    progress_pct = (i / self.iterations) * 100
                    time_lap_start = time.perf_counter()
                    f.read()
                    time_lap_duration = time.perf_counter() - time_lap_start
                    gbps = (self.block_size / self.UNITS["G"]) / time_lap_duration
                    mbps = (self.block_size / self.UNITS["M"]) / time_lap_duration
                    print(
                        f"\r{progress_pct:.2f} %: {gbps:.3f} GB/s ({mbps:.0f} MB/s)",
                        end="",
                        flush=True,
                    )
                    gbps_measurements.append(gbps)
                    mbps_measurements.append(mbps)

            gbps_mean = statistics.mean(gbps_measurements)
            gbps_min = min(gbps_measurements)
            gbps_max = max(gbps_measurements)

            mbps_mean = statistics.mean(mbps_measurements)
            mbps_min = min(mbps_measurements)
            mbps_max = max(mbps_measurements)

            print("\r", end="", flush=True)
            print(f"  mean: {gbps_mean:.3f} gb/s ({mbps_mean:.0f} mb/s)")
            print(f"  min: {gbps_min:.3f} gb/s ({mbps_min:.0f} mb/s)")
            print(f"  max: {gbps_max:.3f} gb/s ({mbps_max:.0f} mb/s)")
            try:
                gbps_stdev = statistics.stdev(gbps_measurements)
                mbps_stdev = statistics.stdev(mbps_measurements)
                print(
                    f"  standard deviation: {gbps_stdev:.3f} gb/s ({mbps_stdev:.0f} mb/s)"
                )
            except:
                pass
            # -------------------------------------

        except KeyboardInterrupt:
            pass

        finally:
            if tmp_file.exists():
                tmp_file.unlink()


def main():
    # Move argparse to class
    description = "Measure read/write speed on disk."

    parser = argparse.ArgumentParser(description="Measure read/write speed on disk.")

    parser.add_argument(
        "-c",
        "--block-size",
        type=str,
        default="100M",
        help="Test size of the test file",
    )
    parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default="100",
        help="How many times to perform the test",
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        default=os.getcwd(),
        help="Path to the target disk to measure (default is the current directory)",
    )

    args = parser.parse_args()
    diskspeed = DiskSpeed(
        path=args.path, block_size=args.block_size, iterations=args.iterations
    )
    diskspeed.test_diskspeed()


if __name__ == "__main__":
    main()
