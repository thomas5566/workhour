import asyncio
import logging
from datetime import UTC, datetime

from app.core.config import settings
from app.database import SessionLocal
from app.repository.alert_log_crud import synchronize_alert_logs
from app.services import monitoring

logger = logging.getLogger(__name__)


def collect_alert_logs_once() -> int:
    """Collect one complete High-or-higher snapshot from every Zabbix host."""
    if not settings.ZABBIX_URL or not settings.ZABBIX_TOKEN:
        return 0

    # Fetch all inputs before opening a transaction. A failed or partial Zabbix
    # request must not falsely mark every active incident as recovered.
    branch_devices = monitoring.get_branch_peplink_health(settings)
    problems = monitoring.get_high_problems(settings)
    problems = monitoring.apply_branch_wan_rules(problems, branch_devices)
    observed_at = datetime.now(UTC)

    with SessionLocal() as db:
        return synchronize_alert_logs(db, problems, observed_at)


async def run_alert_log_collector(stop_event: asyncio.Event) -> None:
    """Periodically persist alert history independently of browser activity."""
    while not stop_event.is_set():
        try:
            created = await asyncio.to_thread(collect_alert_logs_once)
            if created:
                logger.info("Recorded %d new High-or-higher alert incidents", created)
        except Exception as error:
            # Exception text may contain database or remote endpoint details.
            logger.error("Alert log collection failed (%s)", type(error).__name__)

        try:
            await asyncio.wait_for(
                stop_event.wait(), timeout=settings.ALERT_LOG_POLL_SECONDS
            )
        except TimeoutError:
            continue
