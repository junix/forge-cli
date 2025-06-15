import aiohttp
from loguru import logger

async def async_make_request(
    method: str,
    url: str,
    json_payload: dict = None,
    data=None,  # For form-data
    params: dict = None
) -> tuple[int, dict | str | None]:
    """
    Makes an asynchronous HTTP request.

    Args:
        method: HTTP method (e.g., "GET", "POST").
        url: The URL for the request.
        json_payload: JSON payload for the request body.
        data: Data for form-data requests.
        params: URL query parameters.

    Returns:
        A tuple containing the status code and response data (dict, str, or None).

    Raises:
        Exception: For API request failures with non-2xx status codes (excluding 404).
        aiohttp.ClientError: For client-side errors during the request.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method, url, json=json_payload, data=data, params=params
            ) as response:
                status_code = response.status

                if status_code == 200:
                    try:
                        json_response = await response.json()
                        return status_code, json_response
                    except aiohttp.ContentTypeError: # Handles cases where response is not JSON
                        logger.error(f"Response from {method} {url} was 200 but not valid JSON. Text: {await response.text()}")
                        return status_code, await response.text()
                elif status_code == 404:
                    logger.warning(f"Resource not found (404) for {method} {url}.")
                    return status_code, None
                elif status_code >= 200 and status_code < 300: # Other 2xx statuses
                    logger.info(f"Request to {method} {url} returned status {status_code}. Text: {await response.text()}")
                    return status_code, await response.text()
                else: # Non-2xx status codes that are not 404
                    error_text = await response.text()
                    logger.error(
                        f"API request to {method} {url} failed with status {status_code}: {error_text}"
                    )
                    raise Exception(
                        f"API request failed with status {status_code}: {error_text}"
                    )
        except aiohttp.ClientError as e:
            logger.error(f"aiohttp.ClientError during request to {method} {url}: {e}")
            raise  # Re-raise the original ClientError
        except Exception as e:
            logger.error(f"Unexpected error during request to {method} {url}: {e}")
            raise # Re-raise other unexpected errors
