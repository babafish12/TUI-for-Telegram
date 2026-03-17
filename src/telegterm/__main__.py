"""Entry point for telegterm."""

from telegterm.app import TelegtermApp


def main() -> None:
    app = TelegtermApp()
    app.run()


if __name__ == "__main__":
    main()
