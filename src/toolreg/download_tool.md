# Httpx Download Tool

Downloads files from URLs using httpx. Supports:
- Multiple authentication methods
- Progress tracking
- Automatic retries
- Custom headers
- Streaming large files

## Configuration
```yaml
name: download
description: "Download a file from a URL"
requires_confirmation: true
requires_capability: can_read_files
priority: 50
metadata:
  group: network
  icon: mdi:download
```

## Implementation
```python
from typing import Literal
from upathtools import UPath
import httpx

async def download(
    url: str,
    destination: str,
    *,
    auth_type: Literal["none", "basic", "bearer", "custom"] = "none",
    auth_token: str | None = None,
    username: str | None = None,
    password: str | None = None,
    headers: dict[str, str] | None = None,
    verify_ssl: bool = True,
    timeout: float = 30.0,
    allow_redirects: bool = True,
) -> str:
    """Download a file from a URL to a local path.

    Args:
        url: URL to download from
        destination: Local path to save to
        auth_type: Authentication type to use
        auth_token: Token for bearer auth
        username: Username for basic auth
        password: Password for basic auth
        headers: Additional HTTP headers
        verify_ssl: Whether to verify SSL certificates
        timeout: Request timeout in seconds
        allow_redirects: Whether to follow redirects

    Returns:
        Path where the file was saved

    Raises:
        httpx.RequestError: If download fails
        OSError: If saving fails
    """
    # Prepare auth
    auth = None
    if auth_type == "basic" and username and password:
        auth = httpx.BasicAuth(username=username, password=password)

    # Prepare headers
    request_headers = headers or {}
    if auth_type == "bearer" and auth_token:
        request_headers["Authorization"] = f"Bearer {auth_token}"

    # Create client
    async with httpx.AsyncClient(
        auth=auth,
        headers=request_headers,
        verify=verify_ssl,
        follow_redirects=allow_redirects,
        timeout=timeout
    ) as client:
        # Stream download
        async with client.stream("GET", url) as response:
            response.raise_for_status()

            # Get total size if available
            total = int(response.headers.get("content-length", 0))

            # Ensure parent directory exists
            dest = UPath(destination)
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Stream to file with progress
            downloaded = 0
            async with dest.open("wb") as f:
                async for chunk in response.aiter_bytes():
                    await f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        progress = (downloaded / total) * 100
                        print(f"Downloaded: {progress:.1f}%")

    return str(dest)
```

## Examples

### Simple Download
```python
# Download a file with default settings
path = await download(
    url="https://example.com/file.pdf",
    destination="downloads/file.pdf"
)
print(f"Downloaded to: {path}")
```

### With Authentication
```python
# Download with bearer token auth
path = await download(
    url="https://api.example.com/files/123",
    destination="downloads/protected.pdf",
    auth_type="bearer",
    auth_token="my-secret-token"
)
```

### Custom Headers
```python
# Download with custom headers
path = await download(
    url="https://example.com/file.zip",
    destination="downloads/file.zip",
    headers={
        "User-Agent": "MyApp/1.0",
        "Accept": "application/octet-stream"
    }
)
```

### Error Handling
```python
try:
    path = await download(
        url="https://example.com/not-found",
        destination="downloads/missing.txt"
    )
except httpx.HTTPStatusError as e:
    print(f"Download failed with status {e.response.status_code}")
except httpx.RequestError as e:
    print(f"Network error: {e}")
```

### Basic Auth Example
```python
# Download with username/password
path = await download(
    url="https://protected.example.com/file.pdf",
    destination="downloads/protected.pdf",
    auth_type="basic",
    username="user",
    password="pass"
)
```

### Template Usage
```jinja
{% set path = await download(
    url=file_url,
    destination=save_path,
    verify_ssl=False
) %}
Downloaded file saved to: {{ path }}
```
Description: Example of using the download tool in a template with SSL verification disabled.
