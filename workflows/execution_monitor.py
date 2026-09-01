from datetime import datetime


class ExecutionMonitor:

    def __init__(self):
        self.started_at = None
        self.completed_at = None
        self.step_logs = []

    def start(self):
        self.started_at = datetime.now()
        self.completed_at = None
        self.step_logs = []

    def log_step(
        self,
        step_name,
        step_type,
        status,
        duration=0,
        error=None
    ):
        self.step_logs.append({
            "step": step_name,
            "type": step_type,
            "status": status,
            "duration_seconds": round(duration, 3),
            "error": error
        })

    def finish(self):
        self.completed_at = datetime.now()

    def get_metrics(self):

        if not self.started_at:
            return {
                "status": "NOT_STARTED",
                "total_duration_seconds": 0,
                "total_steps": 0,
                "completed_steps": 0,
                "failed_steps": 0,
                "success_rate": 0,
                "step_logs": []
            }

        end_time = (
            self.completed_at
            if self.completed_at
            else datetime.now()
        )

        total_duration = (
            end_time - self.started_at
        ).total_seconds()

        total_steps = len(self.step_logs)

        completed_steps = sum(
            1
            for item in self.step_logs
            if item["status"] == "COMPLETED"
        )

        failed_steps = sum(
            1
            for item in self.step_logs
            if item["status"] == "FAILED"
        )

        success_rate = (
            (completed_steps / total_steps) * 100
            if total_steps
            else 0
        )

        return {
            "status": (
                "COMPLETED"
                if failed_steps == 0
                else "PARTIAL"
            ),
            "total_duration_seconds":
                round(total_duration, 3),
            "total_steps":
                total_steps,
            "completed_steps":
                completed_steps,
            "failed_steps":
                failed_steps,
            "success_rate":
                round(success_rate, 2),
            "step_logs":
                self.step_logs
        }