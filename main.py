import v2ray2json 
import os
import random_free_port
import proxy
import time
import check_connection
from concurrent.futures import ThreadPoolExecutor
import threading
import logging

configs_file = "./vless.txt"
valid_configs_file = "./valid_configs.txt"
max_valid_configs = 10  # Set the specific count limit for valid configs

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

def create_config_file(filename, content):
    try:
        with open(filename, 'x') as f:  # 'x' mode for exclusive creation
            f.write(content)
        logging.info(f"Successfully created and wrote to file: {filename}")
    except FileExistsError:
        logging.warning(f"File '{filename}' already exists.")
    except Exception as e:
        logging.error(f"Error creating file '{filename}': {e}")

def check_config(config):
    global valid_configs, failed_configs

    with counter_lock:
        if valid_configs >= max_valid_configs:
            logging.info(f"Reached the limit of {max_valid_configs} valid configs. Stopping further processing.")
            return
    try:
        port = random_free_port.get()
        config_filename = str(port) + '.json'
        config_content = v2ray2json.generateConfig(port, config)

        create_config_file(config_filename, config_content)

        proxy_process = proxy.start_v2ray(config_filename)
        logging.info(f"Proxy started for config file: {config_filename}")

        
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
        # logging.info(f"Proxy stopped for config file: {config_filename}")
        os.remove(config_filename)
        # logging.info(f"Deleted config file: {config_filename}")



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
            executor.map(check_config, configs)

        logging.info(f"Total valid configs: {valid_configs}")
        logging.info(f"Total failed configs: {failed_configs}")

    except Exception as e:
        logging.error(f"Error processing config file '{file_path}': {e}")

# Uncomment the line below to run the code
process_configs(configs_file)
