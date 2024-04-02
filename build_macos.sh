#!/bin/zsh
pyinstaller --onefile -n "p4-revert-exclusive-checkout (macOS arm64)" --distpath ./bin ./app/main.py