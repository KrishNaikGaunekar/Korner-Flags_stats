"""Upload annotated MP4 to GitHub Releases (HOST-01, HOST-02).

Usage:
    python upload_release.py --stem 08fd33_4
    python upload_release.py --stem 08fd33_4 --output-dir output_videos

Prerequisites:
    - gh CLI installed: winget install GitHub.cli
    - gh authenticated: gh auth login
"""
import argparse
import os
import subprocess
import sys

REPO = 'KrishNaikGaunekar/Korner-Flags_stats'


def build_release_command(stem, output_dir='output_videos'):
    """Build the gh release create command list for a clip stem.

    Args:
        stem: Clip identifier, e.g. '08fd33_4'
        output_dir: Directory containing the annotated MP4

    Returns:
        List of command arguments for subprocess.run
    """
    mp4_path = f'{output_dir}/{stem}_annotated.mp4'
    tag = f'clip-{stem}'
    title = f'Clip: {stem}'
    return [
        'gh', 'release', 'create', tag,
        mp4_path,
        '--title', title,
        '--notes', f'Annotated clip {stem} — auto-uploaded by Korner Flags',
        '--clobber',
    ]


def get_cdn_url(stem):
    """Return the stable GitHub Releases CDN URL for a clip's annotated MP4.

    Args:
        stem: Clip identifier, e.g. '08fd33_4'

    Returns:
        Full URL string, e.g. https://github.com/.../releases/download/clip-08fd33_4/08fd33_4_annotated.mp4
    """
    tag = f'clip-{stem}'
    filename = f'{stem}_annotated.mp4'
    return f'https://github.com/{REPO}/releases/download/{tag}/{filename}'


def main():
    parser = argparse.ArgumentParser(description='Upload annotated MP4 to GitHub Releases')
    parser.add_argument('--stem', required=True,
                        help='Clip stem, e.g. 08fd33_4')
    parser.add_argument('--output-dir', default='output_videos',
                        help='Directory containing the annotated MP4 (default: output_videos)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print the command without executing')
    args = parser.parse_args()

    mp4_path = os.path.join(args.output_dir, f'{args.stem}_annotated.mp4')
    if not os.path.exists(mp4_path):
        print(f'Error: MP4 not found: {mp4_path}')
        sys.exit(1)

    cmd = build_release_command(args.stem, args.output_dir)

    if args.dry_run:
        print(f'[DRY RUN] Would execute: {" ".join(cmd)}')
        print(f'CDN URL: {get_cdn_url(args.stem)}')
        return

    print(f'Uploading {mp4_path} to GitHub Releases...')
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f'Error: {result.stderr}')
        print('Hint: Make sure gh CLI is installed (winget install GitHub.cli) and authenticated (gh auth login)')
        sys.exit(1)

    url = get_cdn_url(args.stem)
    print(f'Upload complete!')
    print(f'Video URL: {url}')
    print(f'Release page: {result.stdout.strip()}')


if __name__ == '__main__':
    main()
