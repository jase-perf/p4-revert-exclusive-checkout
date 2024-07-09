#!/bin/zsh
pyinstaller --onefile -n "p4-revert-exclusive-checkout" --distpath ./bin/macOS_arm64 ./app/main.py