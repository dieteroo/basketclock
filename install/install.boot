#!/bin/bash

# Enable the overlay file system
# This command modifies the Raspberry Pi configuration to enable an overlay filesystem.
# The overlay filesystem creates a temporary filesystem on top of the existing root filesystem.
# All changes are written to this temporary filesystem, which is lost upon reboot.
# This is useful for making the root filesystem read-only and protecting it from corruption.
sudo raspi-config nonint enable_overlayfs

# Enable the boot partition as read-only
# This command modifies the Raspberry Pi configuration to set the boot partition as read-only.
# By making the boot partition read-only, you protect the boot files from accidental changes or corruption.
# This is important for maintaining the stability and integrity of the boot process.
sudo raspi-config nonint enable_bootro

## Reboot
echo -n "The system needs to be rebooted as a final step. Reboot now? [Y/n]: "
            read answer < /dev/tty
            if [ "$answer" != "${answer#[Nn]}" ]; then
                echo "Installation reboot aborted."
                exit 0
            fi
            sudo shutdown -r now
