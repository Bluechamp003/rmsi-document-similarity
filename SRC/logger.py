import logging

logging.basicConfig(
    filename="../run.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filemode="w"
)

logger = logging.getLogger(__name__)