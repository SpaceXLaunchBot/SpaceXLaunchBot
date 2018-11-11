"""
Dealing with errors
"""

import logging
import sys

logger = logging.getLogger(__name__)

def fatalError(message):
    logger.critical(message)
    sys.exit(-1)
