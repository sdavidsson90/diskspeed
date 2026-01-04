import argparse
import os
import shutil
import statistics
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

    @property
    def identify_disk(self):
        path = os.path.abspath(self.test_path)
        while not os.path.ismount(path):
            path = os.path.dirname(path)
        return path

    def check_space(self):
        """
        Check if there's sufficient space to write the test_file in the specified size.
        """
        wd = self.test_path
        free_space = shutil.disk_usage(wd).free

        if self.test_size >= free_space:
            raise RuntimeError("Not enough free space!")

    def test_diskspeed(self):
        file_name = "diskspeed.tmp"

        self.check_space()

        chunks = int(self.test_size / self.chunk_size)

        # file_content = b"\0" * self.chunk_size # Null bytes
        file_content = os.urandom(self.chunk_size)  # Randomness

        try:
            print(f"Target: {self.identify_disk}", end="\n\n")

            # -------------------------------------
            gbps_measurements = []
            mbps_measurements = []
            print("Write speed:")
            with open(file_name, "wb") as f:
                time_start = time.perf_counter()
                for i in range(chunks):
                    progress_pct = (i / chunks) * 100
                    time_lap_start = time.perf_counter()
                    f.write(file_content)
                    time_lap_duration = time.perf_counter() - time_lap_start
                    gbps = (self.test_size / self.UNITS["G"]) / time_lap_duration
                    mbps = (self.test_size / self.UNITS["M"]) / time_lap_duration
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

            print("\r", end = "", flush = True)
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
            print("Read speed:")
            with open(file_name, "rb") as f:
                time_start = time.perf_counter()
                for i in range(chunks):
                    progress_pct = (i / chunks) * 100
                    time_lap_start = time.perf_counter()
                    f.read()
                    time_lap_duration = time.perf_counter() - time_lap_start
                    gbps = (self.test_size / self.UNITS["G"]) / time_lap_duration
                    mbps = (self.test_size / self.UNITS["M"]) / time_lap_duration
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

            print("\r", end = "", flush = True)
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
            if os.path.exists(file_name):
                os.remove(file_name)


def main():
    parser = argparse.ArgumentParser(description="Measure read/write speed on disk.")

    parser.add_argument(
        "-p",
        "--path",
        type=str,
        default=os.getcwd(),
        help="Path to the target disk to perform measurement on",
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
    parser.add_argument(
        "-r",
        "--repeat",
        type=int,
        default="100",
        help="How many times to repeat the test",
    )

    args = parser.parse_args()
    diskspeed = DiskSpeed(
        test_path=args.path, test_size=args.test_size, chunk_size=args.chunk_size
    )
    diskspeed.test_diskspeed()


if __name__ == "__main__":
    main()
