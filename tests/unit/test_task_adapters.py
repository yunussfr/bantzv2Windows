import pytest
from adapters.browser.browser_adapter import BrowserAdapter
from adapters.filesystem.filesystem_adapter import WindowsFileSystemAdapter
from adapters.process.process_adapter import WindowsProcessAdapter
from adapters.screen.screen_adapter import WindowsScreenAdapter
from packages.contracts.tool_request import ToolRequest


@pytest.mark.asyncio
async def test_browser_adapter_navigation_and_security():
    browser = BrowserAdapter()

    # Geçerli URL
    req_valid = ToolRequest(
        taskId="task-1", traceId="tr-1", port="browser",
        action="navigate", parameters={"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}
    )
    res_valid = await browser.execute(req_valid)
    assert res_valid.success is True
    assert res_valid.output["current_url"].startswith("https://")

    # Geçersiz URL şeması (file:// engeli)
    req_file = ToolRequest(
        taskId="task-1", traceId="tr-1", port="browser",
        action="navigate", parameters={"url": "file:///C:/Windows/System32/drivers/etc/hosts"}
    )
    res_file = await browser.execute(req_file)
    assert res_file.success is False
    assert "Yalnızca http ve https" in res_file.error

    # SSRF yerel ağ engeli
    req_ssrf = ToolRequest(
        taskId="task-1", traceId="tr-1", port="browser",
        action="navigate", parameters={"url": "http://169.254.169.254/latest/meta-data/"}
    )
    res_ssrf = await browser.execute(req_ssrf)
    assert res_ssrf.success is False
    assert "Yerel ağ adreslerine erişim engellendi" in res_ssrf.error


@pytest.mark.asyncio
async def test_filesystem_adapter_sandbox_and_traversal_protection(tmp_path):
    fs = WindowsFileSystemAdapter(allowed_base_dir=str(tmp_path))

    # Yazma ve Okuma
    req_write = ToolRequest(
        taskId="task-1", traceId="tr-1", port="filesystem",
        action="write", parameters={"filename": "notes.txt", "content": "Test verisi"}
    )
    res_write = await fs.execute(req_write)
    assert res_write.success is True

    req_read = ToolRequest(
        taskId="task-1", traceId="tr-1", port="filesystem",
        action="read", parameters={"path": "notes.txt"}
    )
    res_read = await fs.execute(req_read)
    assert res_read.success is True
    assert res_read.output["content"] == "Test verisi"

    # Path traversal saldırı engeli (../../etc/passwd veya C:\Windows)
    req_traversal = ToolRequest(
        taskId="task-1", traceId="tr-1", port="filesystem",
        action="read", parameters={"path": "../../../sensitive.key"}
    )
    res_traversal = await fs.execute(req_traversal)
    assert res_traversal.success is False
    assert "izin verilen klasörün dışındadır" in res_traversal.error


@pytest.mark.asyncio
async def test_process_adapter_allowed_and_forbidden_commands():
    proc = WindowsProcessAdapter()

    # İzinli komut (echo)
    req_echo = ToolRequest(
        taskId="task-1", traceId="tr-1", port="process",
        action="echo", parameters={"command": "echo BantzTest"}
    )
    res_echo = await proc.execute(req_echo)
    assert res_echo.success is True
    assert "BantzTest" in res_echo.output["stdout"]

    # İzin verilmeyen komut (calc / format)
    req_forbidden = ToolRequest(
        taskId="task-1", traceId="tr-1", port="process",
        action="run", parameters={"command": "format C: /fs:ntfs"}
    )
    res_forbidden = await proc.execute(req_forbidden)
    assert res_forbidden.success is False
    assert "Güvenlik ihlali" in res_forbidden.error or "İzin verilmeyen" in res_forbidden.error


@pytest.mark.asyncio
async def test_screen_adapter_execution():
    screen = WindowsScreenAdapter()
    req = ToolRequest(taskId="task-1", traceId="tr-1", port="screen", action="screenshot")
    res = await screen.execute(req)
    assert res.success is True
    assert "bytes" in res.output
    assert len(res.evidenceIds) >= 1
