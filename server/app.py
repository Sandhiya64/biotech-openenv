import sys
from pathlib import Path

# Ensure src is available
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from envs.biotech_env.server.app import app


def main():
    return app


if __name__ == "__main__":
    main()