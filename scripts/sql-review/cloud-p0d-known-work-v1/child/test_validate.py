import json
from pathlib import Path
import unittest
from uuid import uuid4
import validate

CLOCK = 1800000000000
HASH = "f"*64


def record(phase, status, **detail):
    seq = validate.PHASES.index(phase) if phase != "ENTRY" else 0
    return json.dumps({"schema":validate.SCHEMA,"phase":phase,"sequence":seq,"status":status,
                       "pools_closed":True,**detail}).encode()


class TestKnownWork(unittest.TestCase):
    def test_receipts(self):
        ready=record("INIT","READY")
        self.assertEqual(validate.receipt(ready,"INIT",acknowledged=True,process_exit=None)["status"],"READY")
        row=record("CLAIM","PHASE_PASS",outcome="claimed",lease={
            "fence":1,"deadline_ms":CLOCK+18000,"lease_digest_sha256":HASH})
        self.assertEqual(validate.receipt(row,"CLAIM",acknowledged=True,process_exit=None,server_ms=CLOCK)["lease"]["fence"],1)
        for change in ({"server_ms":CLOCK+1},{"acknowledged":False},{"process_exit":0}):
            with self.assertRaises(validate.Held):
                validate.receipt(row,"CLAIM",**({"acknowledged":True,"process_exit":None,"server_ms":CLOCK}|change))
        with self.assertRaises(validate.Held):
            validate.receipt(ready[:-1]+b',"phase":"INIT"}',"INIT",acknowledged=True,process_exit=None)
        done=record("FINISH","PASS",assertion_promotions=0)
        self.assertEqual(validate.receipt(done,"FINISH",acknowledged=False,process_exit=0)["status"],"PASS")

    def test_stop_latches_exact_state(self):
        row=record("CLAIM","STOPPED",code="OWNER_COMMIT_UNCONFIRMED",outcome_unconfirmed=True)
        self.assertTrue(validate.receipt(row,"CLAIM",acknowledged=False,process_exit=1)["outcome_unconfirmed"])
        with self.assertRaises(validate.Held):
            validate.receipt(row.replace(b"true}",b"false}"),"CLAIM",acknowledged=False,process_exit=1)

    def test_exact_pre_pool_stop_family(self):
        for phase, codes in (("ENTRY", validate.ENTRY_CODES), ("INIT", validate.INIT_CODES)):
            for code in codes:
                with self.subTest(phase=phase, code=code):
                    unconfirmed = phase == "INIT" and code in validate.UNCERTAIN
                    row = record(phase, "STOPPED", code=code, outcome_unconfirmed=unconfirmed)
                    self.assertEqual(validate.receipt(row, "INIT", acknowledged=False, process_exit=1)["code"], code)
            for unconfirmed in (True, False):
                with self.subTest(phase=phase, unconfirmed=unconfirmed):
                    row = record(phase, "STOPPED", code="OWNER_COMMIT_UNCONFIRMED", outcome_unconfirmed=unconfirmed)
                    with self.assertRaises(validate.Held):
                        validate.receipt(row, "INIT", acknowledged=False, process_exit=1)

    def test_grant_xid_append_only(self):
        fixture=json.loads((Path(__file__).parent/"bundle"/"worker-fixture.json").read_bytes())
        source={"id":str(uuid4()),"issuer_service":"wa_context_issuer","role":"wa_app_runtime",
                "owner":"customer_buyer_profile","action":"SH-004.v1","purpose":"provision","target_kind":"CustomerProfile",
                "target_id":"cdfa190f-3235-5c98-b217-bf27a5d03d66","security_generation":0,"source_generation":0,
                "policy":"wa-p0d-known-work.v1","pid":123,"runtime_xid":"12","issuer_xid":"13",
                "fields_sha256":"684bc408a16638003b12e3a6b19e5dc17e0da1d7f728d12af237c0e396e6f3ec",
                "identity_exact":True,"metadata_exact":True,"row_sha256":HASH}
        schedule={**source,"id":str(uuid4()),"owner":"platform_integration_owner","action":"runtime.schedule_work.v1",
                  "purpose":"work.schedule","target_kind":"RuntimeWorkItem","target_id":"530db9d1-b945-53ec-bb0c-6d91c914b5fc",
                  "pid":124,"runtime_xid":"14","issuer_xid":"15","fields_sha256":"6fcd1458f8cdf7f054e097f8cd3a39c81dded57b9c687268a52986ab9e7d5dbc"}
        self.assertEqual(validate.grant_observation("SOURCE",{"count":1,"distinct_hashes":1,"grants":[source]},[],fixture),"12")
        self.assertEqual(validate.grant_observation("SCHEDULE",{"count":2,"distinct_hashes":2,"grants":[source,schedule]},[source],fixture),"14")
        with self.assertRaises(validate.Held):
            validate.grant_observation("SCHEDULE",{"count":2,"distinct_hashes":2,
                "grants":[source,{**schedule,"issuer_xid":"12"}]},[source],fixture)

    def test_work_renewal_and_reclaim_receipts(self):
        old={"count":1,"identity_exact":True,"state":"leased","fence":1,"attempt":1,"deadline_ms":CLOCK+18000,
             "lease_digest_sha256":HASH,"mutation_xid":"200","row_sha256":"a"*64,
             "without_deadline_xid_sha256":"b"*64,"identity_sha256":"c"*64}
        renewed={**old,"deadline_ms":CLOCK+26000,"mutation_xid":"201","row_sha256":"d"*64}
        fields=("fence","deadline_ms","lease_digest_sha256")
        receipt={name:renewed[name] for name in fields}
        validate.work_observation("RENEW",renewed,old,"201",receipt,CLOCK,CLOCK+80)
        with self.assertRaises(validate.Held):
            validate.work_observation("RENEW",{**renewed,"without_deadline_xid_sha256":"e"*64},old,"201",receipt,CLOCK,CLOCK+80)
        reclaimed={**renewed,"fence":2,"attempt":2,"deadline_ms":CLOCK+44000,"mutation_xid":"202",
                   "lease_digest_sha256":"8"*64,"row_sha256":"9"*64,"without_deadline_xid_sha256":"7"*64}
        receipt={name:reclaimed[name] for name in fields}
        validate.work_observation("RECLAIM",reclaimed,renewed,"202",receipt,CLOCK+26001,CLOCK+26080)
        with self.assertRaises(validate.Held):
            validate.work_observation("RECLAIM",reclaimed,renewed,"202",receipt,CLOCK+25999,CLOCK+26080)


    def test_leased_snapshot_types_and_shape_are_exact(self):
        work = {"count":1,"identity_exact":True,"state":"leased","fence":1,"attempt":1,"deadline_ms":CLOCK+18000,
                "lease_digest_sha256":HASH,"mutation_xid":"200","row_sha256":"a"*64,
                "without_deadline_xid_sha256":"b"*64,"identity_sha256":"c"*64}
        validate.work_observation("LIVE_RECLAIM", work, work, "201", None, CLOCK, CLOCK+80)
        changes = (
            {"deadline_ms":float(work["deadline_ms"])}, {"deadline_ms":True}, {"deadline_ms":0},
            {"lease_digest_sha256":None}, {"lease_digest_sha256":HASH.upper()}, {"lease_digest_sha256":HASH[:-1]},
            {"fence":True}, {"attempt":1.0}, {"fence":0,"attempt":0}, {"fence":3,"attempt":3},
        )
        for change in changes:
            with self.subTest(change=change):
                seen = work | change
                with self.assertRaises(validate.Held):
                    validate.work_observation("LIVE_RECLAIM", seen, seen, "201", None, CLOCK, CLOCK+80)

        renewed = work | {"deadline_ms":CLOCK+26000,"mutation_xid":"201","row_sha256":"d"*64}
        node = {name:renewed[name] for name in ("fence","deadline_ms","lease_digest_sha256")}
        validate.work_observation("RENEW", renewed, work, "201", node, CLOCK, CLOCK+80)
        for bad_before, bad_node in (
            (work | {"deadline_ms":float(work["deadline_ms"])}, node),
            (work, node | {"deadline_ms":float(node["deadline_ms"])}),
            (work, node | {"fence":True}),
        ):
            with self.subTest(before=bad_before, node=bad_node), self.assertRaises(validate.Held):
                validate.work_observation("RENEW", renewed, bad_before, "201", bad_node, CLOCK, CLOCK+80)


if __name__ == "__main__":
    unittest.main()
