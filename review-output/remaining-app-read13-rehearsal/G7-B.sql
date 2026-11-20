SELECT jsonb_build_object('read13_marker','G7-B'::text,'position','BEFORE'::text);
INSERT INTO app.consent_disposition (fingerprint,id,kind,presentation_id,proof_id,semantic_key,user_id) VALUES ('c119af16c36728d99c3709d513d7a6a8069ffc40b766ade015152c3ac71822d5','f9f011da-46bf-5e7e-98a7-da1c034295a8','declined','6a167adf-6699-5ac9-92f6-e3728b6becb9',NULL,'read13/d848e852-f857-4c03-8288-4893e2e8aa0c/B/declined/v1','f43120a8-db4f-5202-9172-fd5ec7787940');
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','G7-B'::text,'position','AFTER'::text);
COMMIT;
