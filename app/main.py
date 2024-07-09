import re
import sys

from P4 import P4, P4Exception

p4 = P4()


class P4PasswordException(P4Exception):
    pass


def main(*paths) -> None:
    init()
    if any(path for path in paths if not path.startswith("//")):
        print(
            "Only depot paths are supported (starting with //).\nSelect from the depot view."
        )
        return

    print(f"Checking paths: {', '.join(paths)}")

    exclusive_files = []
    opened_files = []
    for path in paths:
        opened_files = p4.run_opened("-a", path)
        exclusive_files += [
            file for file in opened_files if is_exclusive_checkout(file)
        ]

    exclusive_files = sorted(exclusive_files, key=lambda x: x["clientFile"])

    print(f"\nFound {len(exclusive_files)} exclusive checkout files:")
    if not exclusive_files:
        return

    max_username_len = max(len(file["user"]) for file in exclusive_files)
    print(f"\n{'User'.ljust(max_username_len)} | Depot File")
    for file in exclusive_files:
        print(f"{file['user'].ljust(max_username_len)} | {file['depotFile']}")

    input("\nPress Enter to revert exclusive checkout... (Close window to cancel)")

    for file in exclusive_files:
        print(".", end="", flush=True)
        p4.run_revert("-C", file["client"], file["depotFile"])

    print("\nReverted all exclusive checkout files.")


def get_opened_files(path: str) -> list:
    files = p4.run_opened("-a", path)
    print(files)
    return files


def is_exclusive_checkout(file: dict) -> bool:
    return bool(re.search(r"\+.*l", file["type"]))


def disconnect() -> None:
    if p4.connected():
        p4.disconnect()


def init(username=None, port=None, password=None):
    if port and p4.port != port:
        disconnect()
        p4.port = port or p4.port
    p4.user = username or p4.user
    if not p4.connected():
        p4.connect()
    try:
        p4.run_login("-s")
    except P4Exception as e:
        if not password:
            raise e
        # If not logged in already, try with the password.
        p4.password = password
        try:
            p4.run_login()
        except P4Exception as e:
            if "invalid or unset" in e.errors[0]:
                raise e
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: p4-revert-exclusive-checkout <depot_path>")
        sys.exit(1)
    main(*sys.argv[1:])
    disconnect()
