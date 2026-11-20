from pathlib import Path
import ast
TASK=Path(__file__).resolve().parent
path=TASK/'check_local_f0_scoped_reads_owned_resource_v1_operation.py'
text=path.read_text()
tree=ast.parse(text)
keep={
 'setUp','image','image_docker','resource',
 'test_import_and_help_do_not_read_helpers_or_launch_processes',
 'test_image_guard_admits_manifest_store_and_keeps_config_independent',
 'test_classic_config_store_id_also_requires_independent_manifest',
 'test_wrong_descriptor_platform_version_or_store_id_stops_without_creation',
 'test_wrong_manifest_bytes_stop_and_no_raw_text_is_retained',
 'test_shared_image_module_is_compiled_from_same_hash_checked_bytes',
 'test_exact_resource_accepts_actual_admitted_manifest_or_config_id',
 'test_resource_rejects_foreign_id_mount_labels_ports_or_namespaces',
 'test_nested_manifest_second_read_drift_stops_before_helper_or_tools',
 'test_transitive_module_drift_is_rejected_before_any_exec',
 'test_owner_packet_source_drift_stops_before_helpers',
 'test_bootstrap_and_finalizer_keep_exact_pinned_sql_reads',
 'test_no_restore_or_recovery_behavior_is_present',
 'test_pipeline_failure_stops_coordinator_and_still_attempts_cleanup',
 'test_cleanup_deletes_only_exact_created_container_volume_and_testsecret',
 'test_foreign_cleanup_identity_is_preserved_and_inventory_uncertainty_rejects',
 'setup_main','test_operational_stop_finalizer_and_persistent_save_failure_do_not_skip_finally',
 'test_scan_and_persistent_save_failure_still_attempt_cleanup_and_each_postcheck',
 'test_initial_evidence_failure_prevents_all_behavior_but_still_runs_finally',
 'test_final_save_failure_cannot_return_or_emit_pass',
 'test_stop_event_stdout_failure_cannot_skip_cleanup_or_change_primary_failure',
 'test_recovered_persistence_does_not_erase_sticky_evidence_failure',
 'test_cleanup_write_failure_after_removal_does_not_skip_volume_secret_or_absence',
 'test_cleanup_inspection_failure_and_bad_writer_still_attempt_remaining_owned_parts',
 'test_external_preservation_attempts_archives_and_snapshot_after_prior_failures',
 'test_unconfirmed_cleanup_return_cannot_pass_and_postchecks_still_run',
 'test_actual_two_mount_prestart_and_old_predicate_regression',
 'test_optional_one_exact_tmpfs_API_row_and_mode_spelling',
 'test_exact_host_tmpfs_multiset_rejects_missing_extra_duplicate_conflicting_tokens',
 'test_API_mount_missing_duplicate_unknown_or_bad_tmpfs_row_rejects',
 'kernel_model','test_real_kernel_helper_fixed_script_model_checks_fs_flags_directory_and_owner',
 'test_kernel_probe_strict_output_exit_types_timeout_and_transport_are_sanitized',
 'creation_world','test_actual_core_creation_order_kernel_before_pgpass_with_two_API_mounts',
 'test_actual_core_kernel_failure_stops_credentials_and_cleanup_survives_persistent_IO'}
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef));lines=text.splitlines(keepends=True)
remove=[n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name not in keep and n.name.replace('scoped_read','owner_read')not in keep]
for node in sorted(remove,key=lambda n:n.lineno,reverse=True):del lines[node.lineno-1:node.end_lineno]
text=''.join(lines)
text=text.replace('OWNER_COORDINATOR','SCOPED_COORDINATOR').replace('OWNER_FIXTURES','SCOPED_FIXTURES').replace('OWNER_CONTENT','SCOPED_CONTENT').replace('OWNER_PACKET','SCOPED_PACKET')
# Existing resource and persistence regressions are version-qualified derivations.
text=text[:text.index("if __name__ == '__main__':")]if "if __name__ == '__main__':"in text else text[:text.index("if __name__=='__main__':")]
child=(TASK/'check_six_read_owned_resource_v1_child_composed_20261119.py').read_text()
childtree=ast.parse(child);childlines=child.splitlines(keepends=True)
child=''.join(''.join(childlines[n.lineno-1:n.end_lineno])+'\n'for n in childtree.body if not(isinstance(n,ast.If)and '__name__'in ast.unparse(n.test)))
path.write_text(text+'\n# Actual immutable child transport composition; no factory substitution.\n'+child+'\n',encoding='utf8',newline='\n')
print('NEW_OWNING_CHECKER_BASE_AUTHORED')
