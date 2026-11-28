BEGIN READ ONLY;
SELECT jsonb_build_object(
  'worker_service_exact', EXISTS (
    SELECT 1 FROM platform_private.identity_service_authorization a
    JOIN platform_private.identity_service_receipt r ON r.id=a.identity_receipt_id AND r.service_principal=a.service_principal
    WHERE a.service_principal='lease-revoke-worker.v1' AND a.identity_receipt_id='f23ed33a-575b-5ecd-95bd-2f573a7004a6'
      AND a.security_generation=0 AND r.security_generation=0 AND r.transition='bootstrap'
      AND r.identity_authorization_ref='synthetic-lease-revoke-worker-bootstrap.v1'
      AND r.previous_generation IS NULL AND r.previous_receipt_id IS NULL
      AND a.mutation_transaction_id=r.mutation_transaction_id AND a.revoked_at IS NULL AND r.revoked_at IS NULL)
);
COMMIT;
