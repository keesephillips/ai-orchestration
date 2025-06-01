#! /usr/bin/bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3
sudo apt-get install tmux
sudo apt install htop
pip install -r requirements.txt