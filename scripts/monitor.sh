#! /usr/bin/bash

# name for the tmux session
SESSION_NAME="my_split_session"

# kill any existing sessions
tmux kill-session -t $SESSION_NAME 2>/dev/null || true

# top screen
tmux new-session -d -s $SESSION_NAME "htop; exec bash"

# bottom screen
tmux split-window -v -t $SESSION_NAME:0.0 "python3 app.py; exec bash"

# Select the top pane to be active
tmux select-pane -t $SESSION_NAME:0.0

# attach to the tmux session
tmux attach-session -t $SESSION_NAME