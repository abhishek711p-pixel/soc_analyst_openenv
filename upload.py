import os
from huggingface_hub import HfApi

token = os.getenv("HF_TOKEN") # Set this in your environment for security!
username = "abhishekjiii"
repo_id = f"{username}/soc_triage_openenv"

api = HfApi(token=token)

print(f"Creating Space {repo_id}...")
api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="docker", exist_ok=True)

files_to_upload = [
    "src/env.py", "src/schemas.py", "scripts/inference.py", "Dockerfile", 
    "README.md", "requirements.txt", "openenv.yaml", 
    "pyproject.toml", "api/app.py", "api/templates/index.html", "uv.lock",
    "tests/adversarial_test.py", "scripts/test_server_load.py"
]

print("Uploading files individually...")
for f in files_to_upload:
    print(f"Uploading {f}...")
    api.upload_file(
        path_or_fileobj=f,
        path_in_repo=f,
        repo_id=repo_id,
        repo_type="space"
    )

print(f"Link: https://huggingface.co/spaces/{repo_id}")
