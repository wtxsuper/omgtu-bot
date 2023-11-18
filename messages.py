def error(msg: str) -> None:
    print(f"\033[91m{msg}\033[0m")


def success(msg: str) -> None:
    print(f"\033[92m{msg}\033[0m")