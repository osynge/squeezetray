import sys, os
sys.path = [os.path.abspath(os.path.dirname(os.path.dirname(__file__)))] + sys.path
import sqtray
import pytest

import unittest
import logging

class TestModule_runnershell2():
    def test_initialise(self):
        pass

if __name__ == "__main__":
    logging.basicConfig()
    LoggingLevel = logging.WARNING
    logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")
    pytest.runmodule()
