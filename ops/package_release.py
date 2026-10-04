"""Package a committed report, source tree and full Git ancestry; no census."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package():
    if git('status', '--porcelain', '--untracked-files=no').strip():
        raise RuntimeError('Commit all tracked changes before packaging')
    commit = git('rev-parse', 'HEAD').decode().strip()
    branch = git('symbolic-ref', '--short', 'HEAD').decode().strip()
    required = ['output/pdf/P12_Chris_Miki.pdf', 'reports/P12_build_record.json',
                'LICENSE', 'LICENSE-REPORT.txt', 'LICENSING.md', '.zenodo.json',
                'data/sources/REVIEW_VAULT_S1_L001.md', 'CITATION.cff']
    for name in required:
        if git('show', f'{commit}:{name}') != (ROOT/name).read_bytes():
            raise RuntimeError('Required release artifact is not committed: '+name)
    build = json.loads((ROOT/'reports/P12_build_record.json').read_text())
    pdf = ROOT/'output/pdf/P12_Chris_Miki.pdf'
    if build['pdf_sha256'] != sha(pdf) or not build['visual_review'].startswith('passed:'):
        raise RuntimeError('Report must pass final visual review before packaging')
    directory = ROOT/'output/release'/commit[:12]
    directory.mkdir(parents=True, exist_ok=True)
    bundle = directory/'history.bundle'
    source = directory/'source.zip'
    if bundle.exists() or source.exists():
        raise RuntimeError('This commit already has a package; retain the existing artifacts')
    git('bundle', 'create', str(bundle), branch)
    subprocess.run(['git', '-C', str(ROOT), 'bundle', 'verify', str(bundle)], check=True)
    git('archive', '--format=zip', '--output='+str(source), commit)
    names = git('ls-tree', '-r', '--name-only', commit).decode().splitlines()
    with zipfile.ZipFile(source) as archive:
        assert archive.testzip() is None
        for name in names:
            assert archive.read(name) == (ROOT/name).read_bytes(), name
    manifest = {
        'commit': commit, 'branch': branch,
        'history_commit_count': int(git('rev-list', '--count', commit)),
        'tracked_file_count': len(names),
        'publication_status': 'not checked by this packaging tool',
        'note': 'Prepared locally; public repository and DOI must be verified separately.',
        'files': {p.name: {'sha256': sha(p), 'bytes': p.stat().st_size}
                  for p in (bundle, source, pdf)},
        'prediction_sha256': build['prediction_sha256'],
        'region_1_review_sha256': build['region_1_review_sha256'],
    }
    instructions = (
        'P12 reproducibility package - Chris Miki\n\n'
        'The report is CC BY 4.0; original code is MIT. See LICENSING.md\n'
        'in source.zip for third-party exceptions. SHA-256 values are in MANIFEST.json.\n\n'
        'To restore the full source tree AND the original Git ancestry:\n'
        '  git clone history.bundle mersenne-factor-laws\n'
        '  cd mersenne-factor-laws\n'
        '  python -m ops.vault_report\n\n'
        'Python 3.10+ and Git are required for this saved-artifact audit.\n'
        'The audit refreshes output timestamps but does not enumerate factors.\n'
        'source.zip is a convenience copy without history and is insufficient\n'
        'on its own for the Git provenance audit. See README.md for full replay.\n'
    )
    output = directory/'mersenne-factor-laws-reproducibility.zip'
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in (bundle, source, pdf):
            archive.write(path, path.name)
        archive.writestr('MANIFEST.json', json.dumps(manifest, sort_keys=True, indent=2)+'\n')
        archive.writestr('REPRODUCE.txt', instructions)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
    package_hash = sha(output)
    (directory/'SHA256SUMS.txt').write_bytes((package_hash+'  '+output.name+'\n').encode())
    print(json.dumps({'package':str(output), 'sha256':package_hash, 'manifest':manifest}, indent=2))


if __name__ == '__main__':
    package()
