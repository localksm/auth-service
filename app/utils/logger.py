import logging

logging.basicConfig()

logger = logging.getLogger(__name__)


def logger(msg):
    logger.critical(msg)
    