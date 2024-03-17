class STlinkException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidInputException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)