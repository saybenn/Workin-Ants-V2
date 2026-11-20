"""Refresh only the new unapproved Restore resource V2 author package."""
from pathlib import Path
import hashlib
import json

TASK = Path(__file__).resolve().parent
ROOT = TASK / 'workinants-correction-pass'
ARCHIVE = ROOT / 'context/reconciliation/local-f0-operation-sources/restore-physical-resource-mount-v2'
VALIDATION = ROOT / 'context/reconciliation/local-f0-restore-resource-mount-v2-source-validation.json'
PRIOR = ROOT / 'context/reconciliation/local-f0-restore-safety-sql-v1-source-validation.json'
BEFORE = TASK / 'restore-resource-mount-v2-before-author-20261119'
FILES = ('execute_local_f0_restore_20261119_resource_mount_v2.py',
         'local_f0_restore_operation_steps_resource_mount_v2.py',
         'prepare_local_f0_restore_plan_resource_mount_v2.py',
         'check_local_f0_restore_operation_resource_mount_v2.py',
         'pin_local_f0_restore_plan_20261119_resource_mount_v2.py')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert ARCHIVE.resolve() == ROOT.resolve() / 'context/reconciliation/local-f0-operation-sources/restore-physical-resource-mount-v2'
    assert VALIDATION.resolve() == ROOT.resolve() / 'context/reconciliation/local-f0-restore-resource-mount-v2-source-validation.json'
    preservation = json.loads((BEFORE / 'manifest.json').read_bytes())
    for name, wanted in preservation['top_immutable_files_sha256'].items():
        assert sha(TASK / name) == wanted
    for name, wanted in preservation['pinned_current_Root_files_sha256'].items():
        assert sha(ROOT / name) == wanted
    expected_before = set(preservation['exclusive_copy_files_sha256']) | {'manifest.json'}
    actual_before = {p.relative_to(BEFORE).as_posix() for p in BEFORE.rglob('*') if p.is_file()}
    assert actual_before == expected_before
    assert not any(p.is_symlink() for p in BEFORE.rglob('*'))
    for name, wanted in preservation['exclusive_copy_files_sha256'].items():
        assert sha(BEFORE / name) == wanted
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for path in BEFORE.rglob('*'):
        if path.is_file():
            target = ARCHIVE / 'preserved' / path.relative_to(BEFORE)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
    reviews = ARCHIVE / 'reviews'
    reviews.mkdir(exist_ok=True)
    original_review = BEFORE / 'accepted-prior-archive/reviews/independent-source-final.json'
    assert sha(original_review) == 'b4a71e7877cae5696821ff3369cf4d83521623a0175ca49b0db5c52d981435b1'
    (reviews / 'independent-source-final.json').write_bytes(original_review.read_bytes())
    for name in FILES:
        (ARCHIVE / (name + '.txt')).write_bytes((TASK / name).read_bytes())
    for name in ('restore_resource_mount_v2_source_plan_20261119.json',
                 'restore_resource_mount_v2_independent_root_plan_review_20261119.json',
                 'restore_resource_mount_v2_inspection.py.txt',
                 'check_restore_resource_mount_v2_resources_20261119.py',
                 'check_restore_resource_mount_v2_source_gates_20261119.py',
                 'check_restore_resource_mount_v2_safety_composed_20261119.py',
                 'run_restore_resource_mount_v2_author_checks_20261119.py',
                 'restore_resource_mount_v2_author_checks_run1_20261119.json',
                 'restore_resource_mount_v2_author_source_gate_recheck_run2_20261119.json',
                 'restore_resource_mount_v2_author_preservation_and_scope_20261119.json',
                 'restore_resource_mount_v2_source_author_review_20261119.json',
                 'refresh_restore_resource_mount_v2_author_archive_20261119.py'):
        path = TASK / name
        if path.exists():
            (reviews / name).write_bytes(path.read_bytes())
    value = json.loads(PRIOR.read_bytes())
    four = {name: sha(TASK / name) for name in FILES[:4]}
    five = {name: sha(TASK / name) for name in FILES}
    value.update(status='RESOURCE_MOUNT_V2_SOURCE_PREPARED_PENDING_INDEPENDENT_REVIEW',
                 source_version='resource-mount-v2', source_root=ARCHIVE.relative_to(ROOT).as_posix(),
                 operator_sources_sha256=four, all_five_sources_sha256=five)
    value['base_source_validation'] = {'path': PRIOR.relative_to(ROOT).as_posix(), 'sha256': sha(PRIOR),
        'approval_scope': 'HISTORICAL_EXACT_SAFETY_SQL_V1_ONLY_RESOURCE_ORACLE_HELD'}
    value['independent_source_review']['qualification'] = 'HISTORICAL_RESTORE_LAYER_ONLY_NEW_RESOURCE_FIVE_NOT_APPROVED'
    value['independent_safety_sql_review'] = {'decision': 'PENDING_ROOT_AND_INDEPENDENT_REVIEW',
        'scope': 'NEW_RESOURCE_MOUNT_V2_FIVE_NOT_APPROVED'}
    value['independent_resource_mount_review'] = {'decision': 'PENDING_ROOT_AND_INDEPENDENT_REVIEW'}
    author_review = reviews / 'restore_resource_mount_v2_source_author_review_20261119.json'
    if author_review.exists():
        value['author_source_review'] = {'path': author_review.relative_to(ROOT).as_posix(), 'sha256': sha(author_review)}
    value['execution_hold'] = 'New source review/publication/fresh full packet and independent literal required; all prior literals remain held.'
    value['archive_files_sha256'] = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(ARCHIVE.rglob('*')) if p.is_file()}
    value['archive_files_aggregate_sha256'] = hashlib.sha256(''.join(n + '\0' + h + '\n'
        for n, h in sorted(value['archive_files_sha256'].items())).encode()).hexdigest()
    VALIDATION.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PENDING_SOURCE_AUTHOR_PACKAGE_ONLY', 'validation_sha256': sha(VALIDATION),
        'archive_files': len(value['archive_files_sha256']), 'all_five_sources_sha256': five}))


if __name__ == '__main__':
    main()
