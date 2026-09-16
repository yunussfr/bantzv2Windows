import subprocess
from datetime import datetime
from typing import Optional


class WindowsTaskSchedulerAdapter:
    """Windows Görev Zamanlayıcısı (Task Scheduler / schtasks) entegrasyon adaptörü."""

    def __init__(self, use_simulation: bool = True):
        self.use_simulation = use_simulation
        self._registered_tasks = {}

    def create_scheduled_task(
        self,
        task_name: str,
        start_time: datetime,
        command_to_run: str = "py -m bantz --once"
    ) -> bool:
        """Windows Task Scheduler üzerinde yeni bir görev girdisi oluşturur."""
        time_str = start_time.strftime("%H:%M")
        date_str = start_time.strftime("%d/%m/%Y")

        if self.use_simulation:
            self._registered_tasks[task_name] = {
                "time": time_str,
                "date": date_str,
                "cmd": command_to_run
            }
            return True

        # schtasks /Create /SC ONCE /TN task_name /TR command /ST HH:MM /SD DD/MM/YYYY /F
        sch_cmd = [
            "schtasks", "/Create",
            "/SC", "ONCE",
            "/TN", f"Bantz_{task_name}",
            "/TR", command_to_run,
            "/ST", time_str,
            "/SD", date_str,
            "/F"
        ]
        try:
            res = subprocess.run(sch_cmd, capture_output=True, text=True, check=False)
            return res.returncode == 0
        except Exception:
            return False

    def delete_scheduled_task(self, task_name: str) -> bool:
        if self.use_simulation:
            return self._registered_tasks.pop(task_name, None) is not None

        sch_cmd = ["schtasks", "/Delete", "/TN", f"Bantz_{task_name}", "/F"]
        try:
            res = subprocess.run(sch_cmd, capture_output=True, text=True, check=False)
            return res.returncode == 0
        except Exception:
            return False
