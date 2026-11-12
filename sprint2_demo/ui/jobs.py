"""Start the existing budgeted runner; never accept a browser-supplied key or path."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import uuid

from core import ROOT, load

JOB_DIR = ROOT / "verification/ui-jobs"
LOCK = ROOT / "verification/ui-worker.lock"


def live_allowed(server_address):
    return (server_address in {"127.0.0.1", "localhost", "::1"} and
            os.environ.get("TRACK3_LOCAL_LIVE") == "1" and bool(os.environ.get("OPENAI_API_KEY", "").strip()))


def write(path, value):
    temporary = path.with_suffix(".pending")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def job_status(job_id):
    if not isinstance(job_id, str) or not len(job_id) == 32 or any(c not in "0123456789abcdef" for c in job_id):
        raise ValueError("Invalid job identifier")
    return load(JOB_DIR / (job_id + ".json"))


def start_live(server_address, project=None):
    if not live_allowed(server_address):
        raise ValueError("Live refinement requires the local launcher with a server-side API key")
    if (ROOT / "pilot_spend.lock").exists():
        raise ValueError("A model run is already active or needs its lock checked")
    JOB_DIR.mkdir(parents=True, exist_ok=True)
    try:
        handle = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("A run is already starting or active; refresh its progress") from None
    os.close(handle)
    job_id = uuid.uuid4().hex
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_name = "live-" + stamp
    log_path, record_path = JOB_DIR / (job_id + ".log"), JOB_DIR / (job_id + ".json")
    record = {"job_id": job_id, "run_name": run_name, "status": "RUNNING", "started_utc": stamp}
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        input_args = []
        if project is not None:
            from project_io import save_input, validate_upload
            from dataclasses import asdict
            package, draft, manifest = validate_upload(json.dumps(asdict(project["package"])).encode("utf-8"),
                                                      json.dumps(asdict(project["drafts"]["v0_input"])).encode("utf-8"))
            input_dir = JOB_DIR / (job_id + "-input")
            save_input(input_dir, package, draft, manifest)
            record["input_origin"] = "uploaded"
            record["project_name"] = project["name"]
            input_args = ["--input-dir", str(input_dir)]
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen([sys.executable, "-u", str(ROOT / "run_live.py"), "--execute",
                "--allow-provisional", "--output", str(ROOT / "runs" / run_name), *input_args], cwd=ROOT, env=env,
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        record["pid"] = process.pid
        write(record_path, record)
    except Exception:
        LOCK.unlink(missing_ok=True)
        raise RuntimeError("The run could not start; no retry was made") from None
    finally:
        env.pop("OPENAI_API_KEY", None)

    def finish():
        code = process.wait()
        record.update(status="COMPLETED" if code == 0 else "STOPPED", exit_code=code,
                      ended_utc=datetime.now(timezone.utc).isoformat())
        try:
            write(record_path, record)
        finally:
            LOCK.unlink(missing_ok=True)

    threading.Thread(target=finish, daemon=True).start()
    return job_id


def progress(job_id):
    record = job_status(job_id)
    log = JOB_DIR / (job_id + ".log")
    lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    # Show only our own stage markers, not arbitrary provider errors or input text.
    markers = [line for line in lines if line.startswith(("Starting ", "Finished "))]
    record["stage_markers"] = markers[-4:]
    return record


# ------------------------------------------------------------------ Half 2: detector-guided revision with checks
HALF2_WRITER = os.environ.get("HALF2_WRITER_MODEL", "gpt-5.4-mini")
HALF2_CHECKER = os.environ.get("HALF2_CHECKER_MODEL", "gpt-5.4")
HALF2_CRITIC = os.environ.get("HALF2_CRITIC_MODEL", "gpt-5.6-luna")
HALF2_MAX_PARAGRAPHS = 5


def start_half2(server_address, paragraph_ids, topic=None):
    """Run sprint2_demo/half2_pipeline.py on a few chosen paragraphs, in the background.

    topic: None for the reviewed example, or a topic id from drafts/track3_five_topic_index.json."""
    if topic is not None and not (isinstance(topic, str) and topic.startswith("cluster") and topic[7:].isdigit()):
        raise ValueError("Unknown topic")
    if not live_allowed(server_address):
        raise ValueError("Live revision requires the local launcher with a server-side API key")
    ids = [p for p in paragraph_ids if isinstance(p, str) and p[:1] == "P" and p[1:].isdigit()]
    if not ids or len(ids) > HALF2_MAX_PARAGRAPHS:
        raise ValueError(f"Choose between 1 and {HALF2_MAX_PARAGRAPHS} paragraphs")
    JOB_DIR.mkdir(parents=True, exist_ok=True)
    try:
        handle = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("A run is already starting or active; refresh its progress") from None
    os.close(handle)
    job_id = uuid.uuid4().hex
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_name = "half2-" + stamp
    log_path, record_path = JOB_DIR / (job_id + ".log"), JOB_DIR / (job_id + ".json")
    record = {"job_id": job_id, "run_name": run_name, "status": "RUNNING", "started_utc": stamp,
              "kind": "half2", "paragraphs": ids, "topic": topic or "cluster7"}
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen([sys.executable, "-u", str(ROOT / "half2_pipeline.py"),
                "--output", str(ROOT / "runs" / run_name), "--writer-model", HALF2_WRITER,
                "--checker-model", HALF2_CHECKER, "--critic-model", HALF2_CRITIC,
                "--paragraphs", ",".join(ids)] + (["--topic", topic] if topic else []), cwd=ROOT, env=env,
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        record["pid"] = process.pid
        write(record_path, record)
    except Exception:
        LOCK.unlink(missing_ok=True)
        raise RuntimeError("The run could not start; no retry was made") from None
    finally:
        env.pop("OPENAI_API_KEY", None)

    def finish():
        code = process.wait()
        record.update(status="COMPLETED" if code == 0 else "STOPPED", exit_code=code,
                      ended_utc=datetime.now(timezone.utc).isoformat())
        try:
            write(record_path, record)
        finally:
            LOCK.unlink(missing_ok=True)

    threading.Thread(target=finish, daemon=True).start()
    return job_id


def half2_progress(job_id):
    """Progress lines printed by half2_pipeline.py ('12:01:02 P035 attempt 1: ACCEPTED - ...')."""
    record = job_status(job_id)
    log = JOB_DIR / (job_id + ".log")
    lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    record["steps"] = [line[9:] for line in lines if len(line) > 9 and line[2] == ":" and line[5] == ":"
                       and " attempt " in line][-12:]
    return record
