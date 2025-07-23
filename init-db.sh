#!/bin/bash
docker run --rm \
  --network user-workspace_app-network \
  -v "$(pwd)/scripts:/scripts" \
  -w /scripts \
  node:18 \
  /bin/bash -c "set -e && \
    echo 'Installing dependencies...' && \
    npm install -g typescript ts-node && \
    npm install pg bcryptjs && \
    echo 'Dependencies installed' && \
    echo 'Running database initialization...' && \
    ts-node --project tsconfig.json init-db-direct.ts"
