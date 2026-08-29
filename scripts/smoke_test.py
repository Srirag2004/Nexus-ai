import requests


def main() -> None:
    base_url = "http://localhost:8000"
    print(requests.get(f"{base_url}/health", timeout=10).json())
    print(requests.post(f"{base_url}/api/v1/chat", json={"message": "What can you do?"}, timeout=20).json())


if __name__ == "__main__":
    main()

