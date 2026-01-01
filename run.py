import argparse
import logging

# Program entry point: run with `python3 run.py`
if __name__ == "__main__":
    # Parse verbosity arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v, -vv, -vvv)",
    )
    args = parser.parse_args()

    # Levels not actually used for error checking
    level = logging.CRITICAL
    if args.verbose == 1:
        level = logging.WARNING  # Print agent calls
    elif args.verbose == 2:
        level = logging.INFO  # Print all agent functions
    elif args.verbose >= 3:
        level = logging.DEBUG  # Print all agent functions and prompts

    logging.basicConfig(level=level, format="%(message)s")
    from interfaces.cli import main

    main()
