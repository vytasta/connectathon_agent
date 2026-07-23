{\rtf1\ansi\ansicpg1252\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
import subprocess\
import logging\
import json\
from typing import Dict, List, Any\
\
# Configure logging\
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')\
logger = logging.getLogger("ConnectathonAgent")\
\
class ConnectathonAgent:\
    def __init__(self, test_dir: str):\
        """\
        Initializes the agent.\
        :param test_dir: Path to the compiled Connectathon test suite directory.\
        """\
        self.test_dir = os.path.abspath(test_dir)\
        # Standard Connectathon test subdirectories/scripts\
        self.suites = \{\
            "basic": "./runtests.basic",\
            "general": "./runtests.general",\
            "special": "./runtests.special"\
        \}\
\
    def _verify_environment(self) -> bool:\
        """Ensures the test directory exists and contains execution scripts."""\
        if not os.path.exists(self.test_dir):\
            logger.error(f"Test directory not found: \{self.test_dir\}")\
            return False\
        return True\
\
    def run_suite(self, suite_name: str, target_mount: str) -> Dict[str, Any]:\
        """\
        Executes a specific Connectathon test suite against a mounted directory.\
        """\
        if suite_name not in self.suites:\
            return \{"suite": suite_name, "status": "FAILED", "error": f"Unknown suite: \{suite_name\}"\}\
\
        script = self.suites[suite_name]\
        logger.info(f"Starting Connectathon [\{suite_name.upper()\}] suite on target: \{target_mount\}")\
\
        # Connectathon tests require target mount directory passed as an argument\
        cmd = [script, target_mount]\
\
        try:\
            # Execute script inside the Connectathon directory context\
            process = subprocess.Popen(\
                cmd,\
                cwd=self.test_dir,\
                stdout=subprocess.PIPE,\
                stderr=subprocess.PIPE,\
                text=True\
            )\
            \
            stdout, stderr = process.communicate()\
            \
            if process.returncode == 0:\
                logger.info(f"Connectathon [\{suite_name.upper()\}] passed successfully.")\
                return \{\
                    "suite": suite_name,\
                    "status": "PASSED",\
                    "return_code": process.returncode,\
                    "output": stdout\
                \}\
            else:\
                logger.error(f"Connectathon [\{suite_name.upper()\}] failed with exit code \{process.returncode\}.")\
                return \{\
                    "suite": suite_name,\
                    "status": "FAILED",\
                    "return_code": process.returncode,\
                    "output": stdout,\
                    "error": stderr\
                \}\
\
        except Exception as e:\
            logger.exception(f"Exception occurred while running \{suite_name\} suite.")\
            return \{"suite": suite_name, "status": "ERROR", "error": str(e)\}\
\
    def run_all_suites(self, target_mount: str) -> Dict[str, Any]:\
        """Executes basic, general, and special test suites sequentially."""\
        results = \{\}\
        all_passed = True\
\
        if not self._verify_environment():\
            return \{"status": "ENVIRONMENT_ERROR", "message": "Verification failed."\}\
\
        for suite in self.suites.keys():\
            res = self.run_suite(suite, target_mount)\
            results[suite] = res\
            if res["status"] != "PASSED":\
                all_passed = False\
\
        summary = \{\
            "overall_status": "PASSED" if all_passed else "FAILED",\
            "results": results\
        \}\
        \
        logger.info(f"All suites finished. Final Status: \{summary['overall_status']\}")\
        return summary\
\
# Example Usage\
if __name__ == "__main__":\
    # Change these paths to match your actual local layout\
    CONNECTATHON_DIR = "/path/to/cthon04" \
    NFS_MOUNT_POINT = "/mnt/nfs_test_target"\
\
    agent = ConnectathonAgent(test_dir=CONNECTATHON_DIR)\
    \
    # Run the full automated sweep\
    report = agent.run_all_suites(target_mount=NFS_MOUNT_POINT)\
    \
    # Print clean JSON result summary\
    print(json.dumps(report, indent=2))\
}