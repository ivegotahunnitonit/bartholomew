import sys
import os

src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from btp_guard.cli import main

if __name__ == "__main__":
    main()
