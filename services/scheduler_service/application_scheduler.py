import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid


class ScheduledJob:
    def __init__(
        self,
        job_id: str,
        task_id: str,
        instruction: str,
        run_at: datetime,
        repeat_interval_seconds: Optional[int] = None,
        status: str = "pending",
        environment: str = "host",
        limits: Optional[Dict[str, Any]] = None
    ):
        self.job_id = job_id
        self.task_id = task_id
        self.instruction = instruction
        self.run_at = run_at
        self.repeat_interval_seconds = repeat_interval_seconds
        self.status = status  # pending, running, completed, missed, cancelled
        self.environment = environment
        self.limits = limits or {
            "max_duration_seconds": 600,
            "max_steps": 10,
            "max_retries": 3
        }


class ApplicationScheduler:
    """Kalıcı SQLite tabanlı ve kaçırılan görevleri yönetebilen zamanlayıcı servisi."""

    def __init__(self, db_path: str = "data/scheduler.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_jobs (
                    job_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    instruction TEXT NOT NULL,
                    run_at TEXT NOT NULL,
                    repeat_interval_seconds INTEGER,
                    status TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    limits_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def schedule(
        self,
        instruction: str,
        run_at: datetime,
        task_id: Optional[str] = None,
        repeat_interval_seconds: Optional[int] = None,
        environment: str = "host",
        limits: Optional[Dict[str, Any]] = None
    ) -> str:
        job_id = f"job-{uuid.uuid4().hex[:10]}"
        t_id = task_id or str(uuid.uuid4())
        limits_dict = limits or {"max_duration_seconds": 600, "max_steps": 10, "max_retries": 3}

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO scheduled_jobs (
                    job_id, task_id, instruction, run_at, repeat_interval_seconds,
                    status, environment, limits_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, t_id, instruction, run_at.isoformat(), repeat_interval_seconds,
                "pending", environment, json.dumps(limits_dict), datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
        return job_id

    def list_due_jobs(self, current_time: Optional[datetime] = None) -> List[ScheduledJob]:
        now = current_time or datetime.now(timezone.utc)
        now_str = now.isoformat()
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM scheduled_jobs
                WHERE status = 'pending' AND run_at <= ?
                ORDER BY run_at ASC
            """, (now_str,)).fetchall()

        jobs = []
        for r in rows:
            jobs.append(ScheduledJob(
                job_id=r["job_id"],
                task_id=r["task_id"],
                instruction=r["instruction"],
                run_at=datetime.fromisoformat(r["run_at"]),
                repeat_interval_seconds=r["repeat_interval_seconds"],
                status=r["status"],
                environment=r["environment"],
                limits=json.loads(r["limits_json"])
            ))
        return jobs

    def mark_status(self, job_id: str, new_status: str) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE scheduled_jobs SET status = ? WHERE job_id = ?
            """, (new_status, job_id))
            conn.commit()

    def handle_missed_jobs(self, current_time: Optional[datetime] = None) -> List[ScheduledJob]:
        """Bilgisayar kapalı kaldığı için kaçırılan görevleri tespit eder ve 'missed' olarak işaretler."""
        now = current_time or datetime.now(timezone.utc)
        due = self.list_due_jobs(now)
        missed = []
        for j in due:
            # Planlanan zamandan 1 saatten fazla geçmişse kaçırılmış say
            if (now - j.run_at).total_seconds() > 3600:
                self.mark_status(j.job_id, "missed")
                j.status = "missed"
                missed.append(j)
        return missed
