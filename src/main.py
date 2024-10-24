import os
from queue import Queue
from speech_recognition import SpeechRecognition
from conversation_manager import ConversationManager
import time
import logging
import argparse
import sys

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

def parse_args():
    parser = argparse.ArgumentParser("Seamless conversation with AI")

    parser.add_argument('-overridelog', action='store_true', help='Override logging of external libraries and enable logging')

    return parser.parse_args()

class ModuleFilter(logging.Filter):
    def filter(self, record):
        return record.name in ['conversation_manager', 'speech_recognition']

def setup_logging(override_log):
    if DEBUG or override_log:
        logging.basicConfig(level=logging.DEBUG) 

    if not override_log:
        return
    root_logger = logging.getLogger()

    filter_module = ModuleFilter()
    root_logger.addFilter(filter_module)

    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.addFilter(filter_module)

def main():
    args  = parse_args()
    setup_logging(args.overridelog)

    api_key = os.environ.get("OPENAI_API_KEY")
    system_prompt_path = 'ai_prompts/system/response_decision_prompt.txt'
    model_path = "models/vosk-model-en-us-0.22"

    shared_queue = Queue(maxsize=2000)

    speech_recognizer = SpeechRecognition(shared_queue, model_path)
    conversation_manager = ConversationManager(api_key, system_prompt_path, shared_queue)

    try:
        speech_recognizer.start()
        conversation_manager.start()

        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("Recieved KeyboardInterrupt, stopping.")
        speech_recognizer.stop()
        conversation_manager.stop()
    except Exception as e:
        logging.critical(f"An error occurred: {e}")
        speech_recognizer.stop()
        conversation_manager.stop()
        raise

if __name__ == "__main__":
    main()
