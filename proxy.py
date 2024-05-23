import platform
import subprocess
import os


def start_v2ray(config_path):
  """
  Starts the V2Ray process using the specified configuration file.

  Args:
      config_path (str): The path to the V2Ray configuration file.

  Raises:
      FileNotFoundError: If either the V2Ray executable or config file is not found.
      RuntimeError: If the operating system is not macOS or Linux.

  Returns:
      subprocess.Popen: The Popen object representing the running V2Ray process.
  """

  # Check operating system
  if platform.system() == "Darwin":  # macOS
    v2ray_path = "/opt/homebrew/bin/v2ray"
  elif platform.system() == "Linux":
    v2ray_path = "/usr/bin/v2ray"
  else:
    raise RuntimeError(f"Unsupported operating system: {platform.system()}")

  # Validate file existence
  if not os.path.exists(v2ray_path):
    raise FileNotFoundError(f"V2Ray executable not found at {v2ray_path}")

  if not os.path.exists(config_path):
    raise FileNotFoundError(f"V2Ray configuration file not found at {config_path}")

  # Build the command with clear arguments
  command = [v2ray_path, "run", "-c", config_path]

  # Start V2Ray in the background with output redirection
  process = subprocess.Popen(
      command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
  )

  # Print process information if needed (commented out for now)
  # print(f"V2Ray is running in the background with PID: {process.pid}")

  return process


def stop_v2ray(process):
  """
  Stops the running V2Ray process.

  Args:
      process (subprocess.Popen): The Popen object representing the V2Ray process.
  """
  process.terminate()
  process.wait()


# Example usage (uncomment if needed)
# config_path = "/path/to/your/v2ray.json"
# v2ray_process = start_v2ray(config_path)
# ... (your code that interacts with the running V2ray process)
# stop_v2ray(v2ray_process)
