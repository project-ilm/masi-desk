# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Command line. Local rehearsal. Does not mint and does not push."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .desk import Desk


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="masi")
    parser.add_argument("--venue", default="venue", type=Path)
    sub = parser.add_subparsers(dest="cmd", required=True)
    launch = sub.add_parser("launch")
    launch.add_argument("kind", choices=["journal", "conference", "book"])
    launch.add_argument("title")
    sub.add_parser("index")
    sub.add_parser("recover")
    args = parser.parse_args(argv)
    desk = Desk(args.venue)
    if args.cmd == "launch":
        event = desk.launch(args.kind, args.title, "cli")
        print(json.dumps({"event_id": event["event_id"], "kind": args.kind}))
    elif args.cmd == "index":
        print(json.dumps(desk.rebuild_index()))
    else:
        print(json.dumps(desk.recover()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
