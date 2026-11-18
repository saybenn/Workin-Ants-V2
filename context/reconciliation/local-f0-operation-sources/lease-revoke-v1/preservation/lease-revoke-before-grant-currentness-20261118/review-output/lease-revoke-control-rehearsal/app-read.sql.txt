SELECT jsonb_build_object('visible_exact_work',count(*)) FROM platform.runtime_work_item WHERE id='8d465067-3364-5f58-b16a-1d6601acbc02';
ROLLBACK;
