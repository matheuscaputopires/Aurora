import os

CONSTANTS_DIR = os.path.dirname(__file__)
CORE_DIR = os.path.dirname(CONSTANTS_DIR)
ROOT_DIR = os.path.dirname(CORE_DIR)
TEMP_DIR = os.path.join(ROOT_DIR, 'temp')

INSTANCES_DIR = os.path.join(CORE_DIR, 'instances')
LOGS_DIR = os.path.join(CORE_DIR, '_logs')
