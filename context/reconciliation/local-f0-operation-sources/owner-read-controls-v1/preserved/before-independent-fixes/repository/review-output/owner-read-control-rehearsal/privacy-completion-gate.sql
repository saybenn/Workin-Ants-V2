SELECT 'WA_OR_BEFORE_PRIVACY_COMPLETION_GATE';
UPDATE app.privacy_requests SET status='completed',completed_at=clock_timestamp(),revision=revision+1 WHERE id='2ca389cc-26a1-548a-b499-b7e0cb74d984';
SELECT 'WA_OR_AFTER_PRIVACY_COMPLETION_GATE';
COMMIT;
