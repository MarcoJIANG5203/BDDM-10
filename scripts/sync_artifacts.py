"""Versioned team bundles: Git metadata, GitHub Release bytes, SHA256 checks."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tempfile
import zipfile


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def relative_name(value):
    name = PurePosixPath(str(value).replace('\\', '/'))
    if name.is_absolute() or '..' in name.parts or not name.parts or ':' in str(name):
        raise ValueError('Expected a project-relative path: ' + str(value))
    if any(part.endswith((' ', '.')) for part in name.parts):
        raise ValueError('Trailing dots/spaces are not portable paths: ' + str(value))
    return name


def reject_local_links(root, name):
    current = root
    for part in name.parts:
        current = current / part
        if current.is_symlink() or current.is_junction():
            raise ValueError('Local links/junctions cannot redirect a delivery: ' + str(current))


def create_bundle(project_root, paths, destination):
    root = Path(project_root).resolve()
    roots = [relative_name(value).as_posix() for value in paths]
    files = {}
    portable_names = set()
    for name in roots:
        reject_local_links(root, relative_name(name))
        source = root / name
        if not source.resolve().is_relative_to(root):
            raise ValueError('Input escapes project root')
        if not source.exists():
            raise FileNotFoundError(source)
        candidates = [source] if source.is_file() else sorted(source.rglob('*'))
        for path in candidates:
            if path.is_symlink() or path.is_junction():
                raise ValueError('Bundle inputs cannot contain symbolic links')
            if path.is_file():
                relative = relative_name(path.relative_to(root).as_posix()).as_posix()
                key = relative.casefold()
                if key in portable_names and relative not in files:
                    raise ValueError('Case-insensitive path collision: ' + relative)
                portable_names.add(key)
                files[relative] = path
    if not files:
        raise ValueError('Cannot create an empty delivery')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for name, path in sorted(files.items()):
            bundle.write(path, name)
    return dict(sha256=sha256(destination), bytes=destination.stat().st_size,
                roots=roots, files=len(files))


def extract_bundle(archive, project_root, allowed_roots, expected_sha, replace=False):
    if sha256(archive) != expected_sha:
        raise ValueError('SHA256 mismatch; nothing extracted')
    root = Path(project_root).resolve()
    allowed = [relative_name(value) for value in allowed_roots]
    pending = []
    with zipfile.ZipFile(archive) as bundle:
        seen = set()
        # Preflight the entire archive before writing a single file.
        for entry in bundle.infolist():
            name = relative_name(entry.filename)
            if not any(name == base or base in name.parents for base in allowed):
                raise ValueError('Archive path outside declared roots: ' + str(name))
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError('Archive cannot contain symbolic links')
            target = root.joinpath(*name.parts)
            reject_local_links(root, name)
            if not target.resolve().is_relative_to(root):
                raise ValueError('Archive path escapes project root')
            if entry.is_dir():
                continue
            key = name.as_posix().casefold()
            if key in seen:
                raise ValueError('Duplicate archive path: ' + str(name))
            seen.add(key)
            if target.exists():
                if not target.is_file():
                    raise FileExistsError(target)
                with bundle.open(entry) as stream:
                    incoming = hashlib.file_digest(stream, 'sha256').hexdigest()
                if sha256(target) == incoming:
                    continue
                if not replace:
                    raise FileExistsError('Different local version: ' + str(target))
            pending.append((entry, target))
        for entry, target in pending:
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(entry) as source, target.open('wb') as output:
                shutil.copyfileobj(source, output)


def gh(*arguments, check=True):
    if shutil.which('gh') is None:
        raise RuntimeError('Install GitHub CLI and run gh auth login first')
    return subprocess.run(['gh', *arguments], check=check, capture_output=True, text=True,
                          encoding='utf-8')


def restore_git_fallback(project_root, entry, replace=False):
    name = entry.get('git_fallback')
    if not name:
        return False
    archive = Path(project_root) / relative_name(name).as_posix()
    if not archive.is_file():
        return False
    extract_bundle(archive, project_root, entry['roots'], entry['sha256'], replace)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=Path(__file__).resolve().parents[1])
    actions = parser.add_subparsers(dest='action', required=True)
    actions.add_parser('list')
    pack = actions.add_parser('pack')
    pack.add_argument('id')
    pack.add_argument('--paths', nargs='+', required=True)
    pack.add_argument('--tag', required=True)
    pack.add_argument('--kind', choices=['synthetic', 'data', 'clinical_results'], required=True)
    publish = actions.add_parser('publish')
    publish.add_argument('id')
    fetch = actions.add_parser('fetch')
    fetch.add_argument('id')
    fetch.add_argument('--replace', action='store_true', help='Explicitly replace differing local files')
    args = parser.parse_args()
    root = args.project_root.resolve()
    registry_path = root / 'artifacts/registry.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    repository = registry['repository']
    if args.action == 'list':
        for identifier, entry in registry['bundles'].items():
            print(identifier, entry['status'], entry['kind'], entry['tag'])
        return
    identifier = relative_name(args.id).as_posix()
    if '/' in identifier:
        raise ValueError('Bundle ID must be a single filename-safe component')
    if args.action == 'pack':
        if identifier in registry['bundles']:
            raise ValueError('Bundle ID already registered; use a new version')
        asset = identifier + '.zip'
        local = Path('dist/artifacts') / asset
        metadata = create_bundle(root, args.paths, root / local)
        registry['bundles'][identifier] = dict(status='prepared', kind=args.kind,
            tag=args.tag, asset=asset, archive=local.as_posix(), **metadata)
    else:
        entry = registry['bundles'][identifier]
        if args.action == 'publish':
            archive = root / entry['archive']
            if sha256(archive) != entry['sha256']:
                raise ValueError('Local archive SHA256 mismatch')
            exists = gh('release', 'view', entry['tag'], '--repo', repository, check=False)
            if exists.returncode == 0:
                gh('release', 'upload', entry['tag'], str(archive), '--repo', repository)
            else:
                gh('release', 'create', entry['tag'], str(archive), '--repo', repository,
                   '--target', 'main', '--title', entry['tag'], '--notes',
                   'Versioned team delivery. SHA256, roots and status are tracked in artifacts/registry.json.')
            entry['status'] = 'published'
            entry['url'] = f'https://github.com/{repository}/releases/tag/{entry["tag"]}'
        else:
            if entry['status'] != 'published':
                raise ValueError('Delivery has not been published')
            if restore_git_fallback(root, entry, args.replace):
                print('Verified and synchronized from Git copy:', identifier)
                return
            with tempfile.TemporaryDirectory(prefix='ei-artifact-') as temporary:
                gh('release', 'download', entry['tag'], '--repo', repository,
                   '--pattern', entry['asset'], '--dir', temporary)
                archive = Path(temporary) / entry['asset']
                extract_bundle(archive, root, entry['roots'], entry['sha256'], args.replace)
            print('Verified and synchronized:', identifier)
            return
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(args.action, identifier, registry['bundles'][identifier]['sha256'])


if __name__ == '__main__':
    main()
