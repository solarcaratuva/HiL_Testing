import sys
import config
import TestRunner


def main() -> None:
    if not config.read_in_configs("Rivanna3s"):
        sys.exit(1)
    if not TestRunner.run_tests():
        sys.exit(1)


if __name__ == "__main__":
    main()
