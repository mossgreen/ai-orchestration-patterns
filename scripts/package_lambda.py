#!/usr/bin/env python3
"""
Package the Pattern A Lambda function using Docker for AWS compatibility.
Replaces build_lambda.sh
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None, env=None):
    """Run a command and capture output."""
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(
            cmd, 
            cwd=cwd, 
            check=True, 
            env=env or os.environ.copy()
        )
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

def package_lambda():
    """Package the Lambda function with all dependencies."""
    
    # Define paths
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    pattern_dir = project_root / "pattern-a-ai-as-service"
    dist_dir = pattern_dir / "dist"
    build_dir = dist_dir / "build"
    
    # 1. Clean previous build
    print("Cleaning previous build...")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    build_dir.mkdir(parents=True)
    
    # 2. Generate requirements.txt
    # We use 'uv pip compile' to ignore local package 'ai-orchestration-shared'
    # which we will copy manually later.
    print("Generating requirements from pyproject.toml...")
    req_file = script_dir / "requirements-lambda.txt"
    
    run_command(
        ["uv", "pip", "compile", "pyproject.toml", "-o", str(req_file), "--no-emit-package", "ai-orchestration-shared"],
        cwd=str(pattern_dir)
    )
    
    # 3. Install dependencies using Docker
    # This ensures we get Linux-compatible wheels (essential for AWS Lambda)
    print("Installing dependencies with Docker...")
    
    try:
        run_command(["docker", "--version"])
    except FileNotFoundError:
        print("Error: Docker is not installed or not in PATH")
        sys.exit(1)
        
    docker_cmd = [
        "docker", "run", "--rm",
        "--platform", "linux/amd64",
        "--entrypoint", "pip",
        "-v", f"{build_dir}:/build",
        "-v", f"{req_file}:/requirements.txt",
        "public.ecr.aws/lambda/python:3.12",
        "install", "-r", "/requirements.txt", "-t", "/build", "--upgrade", "--no-cache-dir"
    ]
    
    run_command(docker_cmd)
    
    # 4. Copy source code
    print("Copying source files...")
    
    # Copy src directory
    shutil.copytree(pattern_dir / "src", build_dir / "src")
    
    # Copy shared directory
    shutil.copytree(project_root / "shared", build_dir / "shared")
    
    # 5. Create zip file
    print("Creating zip archive...")
    zip_path = dist_dir / "lambda.zip"
    
    # shutil.make_archive creates the zip file. 
    # root_dir is the directory to zip (build_dir)
    # base_dir is '.' to include everything inside build_dir at root of zip
    shutil.make_archive(
        str(dist_dir / "lambda"), 
        'zip', 
        root_dir=str(build_dir), 
        base_dir='.'
    )
    
    # Calculate size
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\nBuild complete!")
    print(f"File: {zip_path}")
    print(f"Size: {size_mb:.2f} MB")
    
    return zip_path

if __name__ == "__main__":
    package_lambda()
