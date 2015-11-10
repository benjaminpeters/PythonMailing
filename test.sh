#!/bin/sh
if [ -e "$emailData.txt" ]; then
    python main.py
else
    python generate_emails.py
    python main.py
fi