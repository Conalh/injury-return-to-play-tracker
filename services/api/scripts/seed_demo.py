import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main() -> int:
    api_url = os.getenv("RETURN_PLAY_SEED_API_URL", "http://api:8000").rstrip("/")
    request = Request(
        f"{api_url}/api/demo/seed",
        data=b"",
        method="POST",
        headers={
            "x-actor-id": os.getenv("RETURN_PLAY_ACTOR_ID", "clinician_demo"),
            "x-actor-role": os.getenv("RETURN_PLAY_ACTOR_ROLE", "clinician"),
            "x-organization-id": os.getenv("RETURN_PLAY_ORGANIZATION_ID", "org_demo"),
        },
    )

    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        sys.stderr.write(f"Demo seed failed with HTTP {exc.code}: {exc.read().decode('utf-8')}\n")
        return 1
    except URLError as exc:
        sys.stderr.write(f"Demo seed could not reach {api_url}: {exc.reason}\n")
        return 1

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
