#!/bin/bash

echo "1. Checking Login Redirect..."
CODE=$(curl -o /dev/null -s -w "%{http_code}\n" http://localhost:8000/)
if [ "$CODE" == "307" ]; then
    echo "PASS: Root redirects (307)"
else
    echo "FAIL: Root returned $CODE"
fi

echo "2. Checking /workspaces/new Access protection..."
CODE=$(curl -o /dev/null -s -w "%{http_code}\n" http://localhost:8000/workspaces/new)
if [ "$CODE" == "307" ]; then
    echo "PASS: /workspaces/new redirects (307)"
else
    echo "FAIL: /workspaces/new returned $CODE"
fi
