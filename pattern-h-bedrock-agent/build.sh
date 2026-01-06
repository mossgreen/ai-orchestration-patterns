#!/bin/bash
#
# Build Lambda packages for Pattern H: Bedrock Agent
# Creates 2 separate Lambda zips: action, invoker
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PATTERN_DIR="$SCRIPT_DIR"
DIST_DIR="$PATTERN_DIR/dist"
BUILD_DIR="$DIST_DIR/build"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
REQ_FILE="$SCRIPTS_DIR/requirements-lambda.txt"

echo "=== Building Pattern H Lambda packages ==="
echo "Pattern dir: $PATTERN_DIR"
echo "Dist dir: $DIST_DIR"

# 1. Clean previous build
echo ""
echo "=== Step 1: Cleaning previous build ==="
rm -rf "$DIST_DIR"
mkdir -p "$BUILD_DIR"
mkdir -p "$DIST_DIR/action"
mkdir -p "$DIST_DIR/invoker"

# 2. Generate requirements.txt
echo ""
echo "=== Step 2: Generating requirements ==="
cd "$PATTERN_DIR"
uv pip compile pyproject.toml -o "$REQ_FILE" --no-emit-package ai-orchestration-shared

# 3. Install dependencies using Docker
echo ""
echo "=== Step 3: Installing dependencies with Docker ==="
docker run --rm \
    --platform linux/amd64 \
    --entrypoint pip \
    -v "$BUILD_DIR:/build" \
    -v "$REQ_FILE:/requirements.txt" \
    public.ecr.aws/lambda/python:3.12 \
    install -r /requirements.txt -t /build --upgrade --no-cache-dir

# 4. Copy source files
echo ""
echo "=== Step 4: Copying source files ==="
cp -r "$PATTERN_DIR/src" "$BUILD_DIR/src"
cp -r "$PROJECT_ROOT/shared" "$BUILD_DIR/shared"

# 5. Create zip files
echo ""
echo "=== Step 5: Creating zip archives ==="

cd "$BUILD_DIR"

# Action Lambda
echo "Creating action/lambda.zip..."
zip -r "$DIST_DIR/action/lambda.zip" . -x "*.pyc" -x "__pycache__/*" > /dev/null

# Invoker Lambda
echo "Creating invoker/lambda.zip..."
zip -r "$DIST_DIR/invoker/lambda.zip" . -x "*.pyc" -x "__pycache__/*" > /dev/null

# Report sizes
echo ""
echo "=== Build Complete ==="
echo ""
echo "Lambda packages created:"
ls -lh "$DIST_DIR/action/lambda.zip"
ls -lh "$DIST_DIR/invoker/lambda.zip"
echo ""
echo "Ready for: cd terraform/pattern_h && terraform apply"
