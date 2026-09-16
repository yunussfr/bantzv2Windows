import pytest
from datetime import datetime, timezone, timedelta
from services.scheduler_service.application_scheduler import ApplicationScheduler
from services.scheduler_service.windows_task_scheduler_adapter import WindowsTaskSchedulerAdapter


def test_scheduler_persistence_survives_restart(tmp_path):
    db_file = str(tmp_path / "test_sched.db")

    # 1. İlk oturum: Görev planla
    sched1 = ApplicationScheduler(db_path=db_file)
    run_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    job_id = sched1.schedule(
        instruction="VM'de gece 02:00 web araştırması yap",
        run_at=run_time,
        environment="vm_hyperv"
    )

    # 2. Simüle yeniden başlatma: Yeni scheduler örneği aç
    sched2 = ApplicationScheduler(db_path=db_file)
    due_jobs = sched2.list_due_jobs()

    assert len(due_jobs) == 1
    assert due_jobs[0].job_id == job_id
    assert due_jobs[0].environment == "vm_hyperv"
    assert "gece 02:00" in due_jobs[0].instruction


def test_scheduler_missed_jobs_detection(tmp_path):
    db_file = str(tmp_path / "test_sched_missed.db")
    sched = ApplicationScheduler(db_path=db_file)

    # 3 saat önce çalışması gereken ama bilgisayar kapalı olduğu için çalışmayan görev
    past_time = datetime.now(timezone.utc) - timedelta(hours=3)
    sched.schedule(instruction="Eski rapor görevi", run_at=past_time)

    missed = sched.handle_missed_jobs()
    assert len(missed) == 1
    assert missed[0].status == "missed"


def test_windows_task_scheduler_adapter():
    adapter = WindowsTaskSchedulerAdapter(use_simulation=True)
    target_time = datetime(2026, 9, 17, 2, 0, tzinfo=timezone.utc)
    ok = adapter.create_scheduled_task("NightlyResearch", target_time)
    assert ok is True
    assert "NightlyResearch" in adapter._registered_tasks
