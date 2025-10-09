from loguru import logger

def log_request(method: str, path: str) -> None:
    logger.info(f"{method} {path}")


def log_error(error: str, method: str, path: str) -> None:
    logger.error(f"Error in {method} {path}: {error}")