#!/bin/bash
# Script to permanently mount Windows J: drive in WSL
# Run with: sudo bash setup_j_drive_mount.sh

# Check if entry already exists
if grep -q "J: /mnt/j" /etc/fstab; then
    echo "Mount entry for J: drive already exists in /etc/fstab"
    exit 0
fi

# Ensure mount point exists
if [ ! -d /mnt/j ]; then
    echo "Creating mount point /mnt/j..."
    mkdir -p /mnt/j
fi

# Add entry to fstab
echo "Adding J: drive mount entry to /etc/fstab..."
echo "J: /mnt/j drvfs defaults 0 0" >> /etc/fstab

echo "Mount entry added successfully!"
echo ""
echo "To mount the drive now, run:"
echo "  sudo mount -t drvfs J: /mnt/j"
echo ""
echo "Or restart WSL and it will mount automatically."

