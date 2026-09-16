import pytest
from datetime import datetime, timezone, timedelta
from packages.core.orchestrator import Orchestrator
from packages.core.event_bus import EventBus
from packages.core.task_state_machine import TaskStateMachine, TaskStatus
from packages.policy.capability_registry import CapabilityRegistry
from packages.policy.approval_engine import ApprovalEngine
from packages.secrets.secret_broker import SecretBroker
from services.vm_controller.vm_controller_adapter import WindowsVMControllerAdapter
from services.scheduler_service.application_scheduler import ApplicationScheduler
from services.scheduler_service.windows_task_scheduler_adapter import WindowsTaskSchedulerAdapter
from packages.observability.trace_manager import TraceManager
from packages.observability.evidence_store import EvidenceStore, EvidenceType
from packages.avatar.motion_engine import AvatarState, MotionEngine
from packages.contracts.task_report import TaskReport


@pytest.mark.asyncio
async def test_full_e2e_nightly_vm_research_mission(tmp_path):
    """İterasyon 1 Tamamlanma Ölçütü (Page 11 & Page 14):

    'Yarın saat 02.00’de VM’de yapay zekâ ajanları hakkında araştırma yap,
    en az beş güvenilir kaynak kullan ve sabah bana kısa bir rapor hazırla.'
    """
    event_bus = EventBus()
    events_log = []

    async def _event_collector(evt):
        events_log.append(evt["eventType"])

    event_bus.subscribe_all(_event_collector)

    # 1. Altyapı ve Servislerin Başlatılması
    trace_mgr = TraceManager()
    evidence_store = EvidenceStore(base_dir=str(tmp_path / "evidence"))
    policy_registry = CapabilityRegistry()
    approval_engine = ApprovalEngine(capability_registry=policy_registry, autonomy_tier="medium")
    secret_broker = SecretBroker()
    scheduler = ApplicationScheduler(db_path=str(tmp_path / "sched.db"))
    win_task_sched = WindowsTaskSchedulerAdapter(use_simulation=True)

    # VM Controller Adaptörü
    vm_adapter = WindowsVMControllerAdapter(vm_name="NightlyAgentVM", use_simulation=True)

    # 2. Kullanıcı Girişi
    user_instruction = (
        "Yarın saat 02.00’de VM’de yapay zekâ ajanları hakkında araştırma yap, "
        "en az beş güvenilir kaynak kullan ve sabah bana kısa bir rapor hazırla."
    )

    # 3. Yönlendirme ve Görev Planlama
    # Router isteği analiz eder
    from packages.core.router import Router
    router = Router()
    routing_decision = await router.route(user_instruction)
    assert routing_decision.target_environment == "vm_hyperv"

    # 4. Görevin Zamanlanması (Scheduler)
    scheduled_time = datetime.now(timezone.utc) + timedelta(hours=6)
    job_id = scheduler.schedule(
        instruction=user_instruction,
        run_at=scheduled_time,
        environment=routing_decision.target_environment
    )
    assert job_id.startswith("job-")

    # Windows Task Scheduler girdisi oluşturulur
    ok_sch = win_task_sched.create_scheduled_task("AgentNightlyResearch", scheduled_time)
    assert ok_sch is True

    # 5. Zamanın Gelmesi ve Görevin VM İçinde İcrası (Saat 02:00 Simülasyonu)
    # Orchestrator'a VM portu kaydedilir
    ports = {
        "vm": vm_adapter,
        "browser": vm_adapter,     # VM içindeki tarayıcı
        "filesystem": vm_adapter,  # VM içindeki dosya sistemi
        "notification": vm_adapter
    }
    orchestrator = Orchestrator(port_registry=ports, event_bus=event_bus)

    # Görevin orkestratör tarafından çalıştırılması
    report: TaskReport = await orchestrator.submit_instruction(
        user_instruction=user_instruction,
        source="scheduler"
    )

    # 6. Sonuçların ve Raporun Doğrulanması (Page 12 Kabul Kriterleri)
    assert report.status == "completed"
    assert report.environment == "vm_hyperv"
    assert report.durationSeconds >= 0.0
    assert len(report.completedSteps) >= 1
    assert len(report.collectedSources) >= 5

    # En az 5 güvenilir kaynak toplandığı doğrulanır
    for source in report.collectedSources:
        assert source.startswith("https://")

    # Rapor dosyasının oluşturulduğu doğrulanır
    assert len(report.createdFiles) >= 1

    # 7. Kanıtların Kaydedilmesi (EvidenceStore)
    ev_dom = evidence_store.save_evidence(
        task_id=report.taskId,
        trace_id=report.traceId,
        evidence_type=EvidenceType.DOM_SNAPSHOT,
        raw_data=b"<html>DOM Snapshot of AI Agent Research</html>",
        file_extension="html"
    )
    ev_screen = evidence_store.save_evidence(
        task_id=report.taskId,
        trace_id=report.traceId,
        evidence_type=EvidenceType.SCREENSHOT,
        raw_data=b"PNG_SAMPLE_RESEARCH_SCREENSHOT",
        file_extension="png"
    )
    stored_evidence = evidence_store.get_evidence_for_task(report.taskId)
    assert len(stored_evidence) == 2

    # 8. Avatarın Sonucu Bildirmesi ve Güvenli Hareket Motoru (Page 14)
    avatar_motion = MotionEngine.validate_motion_json({
        "description": "Avatar sabah raporu sunar",
        "target_state": "success",
        "commands": [
            {"command": "bounce", "duration_ms": 300, "parameters": {"count": 1}},
            {"command": "show_bubble", "duration_ms": 2000, "parameters": {"text": "Günaydın efendim! Gece 02.00'de istediğiniz VM yapay zekâ araştırma raporunu 5 kaynakla hazırladım."}}
        ]
    })
    assert avatar_motion.target_state == AvatarState.SUCCESS
    assert avatar_motion.commands[1].command.value == "show_bubble"
    assert "Günaydın" in avatar_motion.commands[1].parameters["text"]

    # 9. EventBus ve TraceId Doğrulaması
    assert "task_created" in events_log
    assert "step_started" in events_log
    assert "step_finished" in events_log
    assert "task_completed" in events_log
    assert report.traceId is not None and report.traceId.startswith("trace-")
