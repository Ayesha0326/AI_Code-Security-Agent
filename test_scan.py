
import subprocess
import os

def run_command(command):
    return subprocess.call(command, shell=True)

password = "TEST_PASSWORD_PLACEHOLDER"

os.system("echo Security scanner test")
