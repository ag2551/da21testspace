from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def test_celery_task(message: str = "Hello from Celery!") -> str:
    """
    Test task to verify Celery is working correctly.

    Args:
        message: Message to log and return

    Returns:
        The message that was processed
    """
    logger.info(f"Celery task executed: {message}")
    return f"Task completed: {message}"


@shared_task
def publish_to_platform(transaction_uuid: str, platform: str):
    """
    Background task to publish content to a social media platform.

    Args:
        transaction_uuid: UUID of the PostTransaction
        platform: Platform name ('facebook', 'linkedin', 'line')
    """
    logger.info(f"Publishing transaction {transaction_uuid} to {platform}")
    # TODO: Implement actual platform publishing logic
    return {
        "transaction_uuid": transaction_uuid,
        "platform": platform,
        "status": "success"
    }
