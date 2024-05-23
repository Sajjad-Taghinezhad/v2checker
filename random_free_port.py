import socket
import random


def is_port_free(port):
  """
  Checks if a given port is free on the local machine.

  Args:
      port (int): The port number to check.

  Returns:
      bool: True if the port is free, False otherwise.
  """
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
      # Attempt to bind the socket to the specified port
      s.bind(('', port))
      return True
    except OSError:
      # OSError is raised if the port is already in use
      return False


def get(min_port=1024, max_port=65535):
  """
  Finds a free port on the local machine within a specified range.

  Args:
      min_port (int, optional): The minimum port number to consider (default: 1024).
      max_port (int, optional): The maximum port number to consider (default: 65535).

  Returns:
      int: A free port number within the specified range, or None if no free port is found.
  """
  while True:
    port = random.randint(min_port, max_port)
    if is_port_free(port):
      return port


# Example usage
# free_port = get_free_port()

# if free_port:
#   print(f"Found a free port: {free_port}")
# else:
#   print("No free port found within the specified range.")
