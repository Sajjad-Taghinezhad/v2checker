import v2ray2json
import os
import random_free_port
import proxy
import time
import check_connection
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import logging
import signal
import sys
import argparse

# Default values
DEFAULT_CONFIGS_FILE = "./configs"
DEFAULT_VALID_CONFIGS_FILE = "./sajx.sub"
DEFAULT_MAX_VALID_CONFIGS = 10000

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Check and validate V2Ray configurations.")
parser.add_argument('--configs_file', type=str, default=DEFAULT_CONFIGS_FILE, help='Path to the configurations file.')
parser.add_argument('--valid_configs_file', type=str, default=DEFAULT_VALID_CONFIGS_FILE, help='Path to the output file for valid configurations.')
parser.add_argument('--max_valid_configs', type=int, default=DEFAULT_MAX_VALID_CONFIGS, help='Maximum number of valid configurations before stopping.')
args = parser.parse_args()

configs_file = args.configs_file
valid_configs_file = args.valid_configs_file
max_valid_configs = args.max_valid_configs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("config_check.log"),
        logging.StreamHandler()
    ]
)

# Lock for thread-safe writing to the valid_configs file and counters
file_lock = threading.Lock()
counter_lock = threading.Lock()

# Counters
total_configs = 0
valid_configs = 0
failed_configs = 0

# Flag for stopping threads
stop_flag = threading.Event()

def create_config_file(filename, content):
    try:
        with open(filename, 'x') as f:  # 'x' mode for exclusive creation
            f.write(content)
        # logging.info(f"Successfully created and wrote to file: {filename}")
    except FileExistsError:
        logging.warning(f"File '{filename}' already exists.")
    except Exception as e:
        logging.error(f"Error creating file '{filename}': {e}")

def check_config(config):
    global valid_configs, failed_configs
    
    # Check if stop flag is set to terminate early
    if stop_flag.is_set():
        logging.info("Stop flag set. Terminating early.")
        return
    
    with counter_lock:
        if valid_configs >= max_valid_configs:
            logging.info(f"Reached the limit of {max_valid_configs} valid configs. Stopping further processing.")
            stop_flag.set()
            return

    try:
        port = random_free_port.get()
        config_filename = str(port) + '.json'
        config_content = v2ray2json.generateConfig(port, config)

        create_config_file(config_filename, config_content)

        proxy_process = proxy.start_v2ray(config_filename)
        # logging.info(f"Proxy started for config file: {config_filename}")

        time.sleep(5)
        if check_connection.https("https://google.com/generate_204", port):
            logging.info(f'{valid_configs} OK')
            with file_lock:
                with open(valid_configs_file, 'a') as valid_file:
                    valid_file.write(config)
            with counter_lock:
                valid_configs += 1
        else:
            logging.warning(f'{failed_configs} Fail')
            with counter_lock:
                failed_configs += 1

        proxy.stop_v2ray(proxy_process)
        os.remove(config_filename)

        

    except Exception as e:
        logging.error(f"Error processing config: {e}")

def process_configs(file_path):
    global total_configs
    try:
        with open(file_path, 'r') as f:
            configs = f.readlines()

        total_configs = len(configs)
        logging.info(f"Total configs: {total_configs}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_config, config) for config in configs]
            for future in as_completed(futures):
                if stop_flag.is_set():
                    logging.info("Stop flag detected. Cancelling remaining tasks.")
                    for future in futures:
                        future.cancel()
                    break

        logging.info(f"Total valid configs: {valid_configs}")
        logging.info(f"Total failed configs: {failed_configs}")

    except Exception as e:
        logging.error(f"Error processing config file '{file_path}': {e}")

def signal_handler(sig, frame):
    logging.info("SIGINT received. Stopping all threads.")
    stop_flag.set()
    sys.exit(0)

# Set up signal handling for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)

# Run the code
process_configs(configs_file)
