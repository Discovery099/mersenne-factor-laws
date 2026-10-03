from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from mf import protocol
from ops import worker, supervisor
from ops.common import execute_engine, exclusive_lock


class ProtocolTests(unittest.TestCase):
    def fixture(self, root):
        for name in ("laws/L002.py","mf/checker.py","mf/checker2.c","mf/census_kp.c","mf/census_pk.c","mf/null_n0.py",
                     "mf/predict.py","mf/stats.py","mf/score.py","mf/protocol.py","mf/__init__.py","ops/__init__.py","ops/worker.py","ops/common.py","vendor/mini-gmp.c","vendor/mini-gmp.h"):
            path=root/name
            path.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(protocol.ROOT/name,path)
        pred=root/"predictions/test.json"
        pred.parent.mkdir()
        obj={"bounds":[3,23,10],"law_path":"laws/L002.py","sources":protocol.source_hashes("laws/L002.py",root)}
        pred.write_text(json.dumps(obj)+"\n")
        (root/"ALERTS.md").write_text(protocol.digest(pred)+"\n")
        for args in (("init",),("config","user.name","Test"),("config","user.email","test@example.invalid"),("config","core.autocrlf","false"),("add",".")):
            subprocess.run(["git","-C",str(root),*args],check=True,capture_output=True)
        env={**os.environ,"GIT_AUTHOR_DATE":"2020-01-01T00:00:00+00:00","GIT_COMMITTER_DATE":"2020-01-01T00:00:00+00:00"}
        subprocess.run(["git","-C",str(root),"commit","-m","prediction before computation"],env=env,check=True,capture_output=True)
        return pred

    def test_real_git_commit_audit_and_mutations(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            pred=self.fixture(root)
            manifest=root/"manifest.json"
            value=protocol.begin(pred,manifest,root)
            census=root/"census.txt"
            census.write_bytes(b"3 1\n")
            value.update(status="complete",census_sha256=protocol.digest(census))
            protocol.atomic_json(manifest,value)
            protocol.audit(pred,census,manifest,root)
            old=census.stat().st_mtime
            os.utime(census,(1,1))
            with self.assertRaisesRegex(ValueError,"postdate"):
                protocol.audit(pred,census,manifest,root)
            os.utime(census,(old,old))
            census.write_bytes(b"11 4\n")
            with self.assertRaisesRegex(ValueError,"modified"):
                protocol.audit(pred,census,manifest,root)
            (root/"mf/score.py").write_text("# changed after commit\n")
            with self.assertRaisesRegex(ValueError,"source hash"):
                protocol.registered(pred,root)

    def test_missing_alert_or_uncommitted_prediction_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            pred=self.fixture(root)
            obj=json.loads(pred.read_text());obj["bounds"]=[5,23,10]
            pred.write_text(json.dumps(obj)+"\n")
            with self.assertRaisesRegex(ValueError,"git commit"):
                protocol.registered(pred,root)

    def test_worker_resume_timeout_and_corrupt_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);work=root/"work";work.mkdir()
            calls=[0]
            def interrupted(name,bounds,timeout):
                calls[0]+=1
                if calls[0]==3:
                    raise subprocess.TimeoutExpired("injected",1)
                return execute_engine(name,bounds,timeout)
            def begin(*args,**kwargs):
                return {"bounds":[3,23,10],"start_head":"fixture","started_at":protocol.utcnow()}
            # Real engines/checkers; isolate only git registration and artifact destination.
            with patch.object(worker,"ROOT",root),patch.object(worker,"begin",side_effect=begin),patch.object(worker,"ledger"):
                with patch.object(worker,"execute_engine",side_effect=interrupted):
                    first=worker.work("prediction.json",work,12,1,chunk=5)
                self.assertEqual(first["status"],"paused-budget")
                state=json.loads((work/"checkpoint.json").read_text())
                self.assertEqual(state["next"],8)
                # The acceptance subprocess imports the real installed workspace module.
                real_run=subprocess.run
                def run_in_project(*args,**kwargs):
                    kwargs["cwd"]=protocol.ROOT
                    return real_run(*args,**kwargs)
                with patch.object(worker.subprocess,"run",side_effect=run_in_project):
                    result=worker.work("prediction.json",work,12,1,chunk=5)
                self.assertEqual(result["status"],"complete")
                state=json.loads((work/"checkpoint.json").read_text());state["parts"].pop(0)
                protocol.atomic_json(work/"checkpoint.json",state)
                with self.assertRaisesRegex(ValueError,"coverage"):
                    worker.work("prediction.json",work,12,1,chunk=5)

    def test_queue_constraints_and_exclusive_lock(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"queue.jsonl"
            row={"id":"test","kind":"census","hours":1,"seed":12,"checkpoint":"runs/test","predictions":"predictions/test.json"}
            path.write_text(json.dumps(row)+"\n")
            self.assertEqual(len(supervisor.queue(path)),1)
            row["checkpoint"]="../outside"
            path.write_text(json.dumps(row)+"\n")
            with self.assertRaises(ValueError):
                supervisor.queue(path)
            lock=Path(td)/"lock"
            with exclusive_lock(lock):
                with self.assertRaises(OSError):
                    with exclusive_lock(lock):
                        pass

    def test_supervisor_stops_after_three_restarts(self):
        class Failed:
            pid=12345
            returncode=1
            def poll(self): return 1
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);runtime=root/"ops/runtime";runtime.mkdir(parents=True)
            q=root/"queue.jsonl"
            q.write_text(json.dumps({"id":"failure","hours":1,"seed":12,"checkpoint":"runs/failure","predictions":"predictions/failure.json"})+"\n")
            with patch.object(supervisor,"ROOT",root),patch.object(supervisor,"RUNTIME",runtime),patch.object(supervisor.subprocess,"Popen",return_value=Failed()) as spawn,patch.object(supervisor.time,"sleep"):
                states=supervisor.run(q,1,1)
            self.assertEqual(spawn.call_count,4)
            self.assertEqual(states["failure"]["status"],"failed")
