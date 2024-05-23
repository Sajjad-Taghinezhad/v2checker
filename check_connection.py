import requests

def https(url, proxy_port="", timeout=5):  # Added timeout parameter
  """
  Sends an HTTPS request to the specified URL using an HTTP proxy, with a timeout.

  Args:
      url (str): The URL to send the request to.
      proxy_port (str, optional): The proxy server port (default: "").
      timeout (int, optional): The maximum time in seconds to wait for a response (default: 5).

  Returns:
      bool: True if the request was successful, False otherwise.
  """
  try:
    proxies = {
      "http": f"http://127.0.0.1:{proxy_port}",  # Use f-string for cleaner formatting
      "https": f"http://127.0.0.1:{proxy_port}"
    }
    response = requests.get(url, proxies=proxies, verify=False, timeout=timeout)
    response.raise_for_status()  # Raise an exception for non-200 status codes
    return True
  except requests.exceptions.RequestException as e:
    print(f"Error sending request: {e}")  # Print error details for debugging
    return False
