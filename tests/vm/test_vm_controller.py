import pytest
from services.vm_controller.hyper_v_adapter import HyperVAdapter
from services.vm_controller.guest_connection import GuestConnection
from services.vm_controller.vm_controller_adapter import WindowsVMControllerAdapter
from packages.contracts.tool_request import ToolRequest


@pytest.mark.asyncio
async def test_hyperv_adapter_lifecycle():
    adapter = HyperVAdapter(use_simulation=True)
    assert await adapter.get_vm_state("TestVM") == "Off"

    assert await adapter.start_vm("TestVM") is True
    assert await adapter.get_vm_state("TestVM") == "Running"

    assert await adapter.checkpoint_vm("TestVM", "chk_test") is True
    assert await adapter.restore_checkpoint("TestVM", "chk_test") is True

    assert await adapter.stop_vm("TestVM") is True
    assert await adapter.get_vm_state("TestVM") == "Off"


def test_guest_connection_hmac_verification():
    conn = GuestConnection(shared_secret="secret-key-123")
    msg = {"action": "test", "val": 42}

    envelope = conn.pack_message(msg)
    assert "signature" in envelope

    # Geçerli imza doğrulanır
    unpacked = conn.unpack_message(envelope)
    assert unpacked == msg

    # Tahrif edilmiş veri reddedilir
    tampered = dict(envelope)
    tampered["payload"] = {"action": "tampered", "val": 999}
    assert conn.unpack_message(tampered) is None


@pytest.mark.asyncio
async def test_vm_controller_execute_and_isolation():
    vm_adapter = WindowsVMControllerAdapter(use_simulation=True)

    # 1. Başarılı görev ve kanıt dönüşü
    req_ok = ToolRequest(
        taskId="12345678-0000-0000-0000-000000000000",
        traceId="trace-123",
        port="vm",
        action="search_and_extract",
        parameters={"topic": "AI Agents"}
    )
    res_ok = await vm_adapter.execute(req_ok)
    assert res_ok.success is True
    assert len(res_ok.output.get("sources", [])) == 5
    assert len(res_ok.evidenceIds) >= 1

    # 2. İzolasyon testi: Host yolu erişimi reddedilmeli
    req_leak = ToolRequest(
        taskId="12345678-0000-0000-0000-000000000000",
        traceId="trace-123",
        port="vm",
        action="read_file",
        parameters={"path": "C:\\Users\\admin\\Desktop\\private.txt"}
    )
    res_leak = await vm_adapter.execute(req_leak)
    assert res_leak.success is False
    assert "İzolasyon ihlali" in res_leak.error
