import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["server", "static"], default="server")
    parser.add_argument("--noclean", action="store_true")
    parser.add_argument("--size", type=int, default=100)

    args = parser.parse_args()

    if args.mode == "server":
        from server import app

        app.run()

    elif args.mode == "static":
        from static import store_feeds, clean

        store_feeds(args.size)
        if not args.noclean:
            clean()
