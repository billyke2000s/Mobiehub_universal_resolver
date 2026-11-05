"""One command to set up and start the optional local extension service."""
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--moviehub')
    parser.add_argument('--model', default='qwen3.5:9b')
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--vision', action='store_true')
    options = parser.parse_args()
    env = root / '.venv'
    python = env / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not python.exists():
        subprocess.run([sys.executable, '-m', 'venv', str(env)], check=True, timeout=120)
    subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(root / 'requirements.txt')], check=True, timeout=600)
    subprocess.run([str(python), '-m', 'playwright', 'install', 'chromium'], check=True, timeout=600)
    checkout = options.moviehub
    if not checkout:
        sibling = root.parent / 'moviehub'
        if (sibling / '.git').exists():
            checkout = str(sibling)
        else:
            checkout = input('Path to your MovieHub checkout (Enter for browser-only mode): ').strip().strip('"')
    args = [str(python), '-m', 'resolver.service', '--model', options.model]
    if checkout: args += ['--moviehub', checkout]
    if options.headless: args += ['--headless']
    if options.vision: args += ['--vision']
    return subprocess.call(args, cwd=str(root))


if __name__ == '__main__':
    try: sys.exit(main())
    except (subprocess.SubprocessError, OSError):
        sys.exit('Setup could not finish. Check Python, internet access and the selected checkout path.')
