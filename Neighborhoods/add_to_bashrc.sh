#!/bin/bash
# Alternative method: Add auto-mount to ~/.bashrc
# This will mount the drive every time you start a WSL session

MOUNT_ENTRY='# Auto-mount J: drive
if [ ! -d /mnt/j ] || ! mountpoint -q /mnt/j 2>/dev/null; then
    sudo mount -t drvfs J: /mnt/j 2>/dev/null
fi'

if ! grep -q "Auto-mount J: drive" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "$MOUNT_ENTRY" >> ~/.bashrc
    echo "Added auto-mount entry to ~/.bashrc"
    echo "The J: drive will be mounted automatically when you start WSL"
else
    echo "Auto-mount entry already exists in ~/.bashrc"
fi

