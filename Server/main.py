import config
import TestRunner


def main() -> None:
    config.read_in_configs("Rivanna3s")

    TestRunner.run_tests()


if __name__ == "__main__":
    main()
