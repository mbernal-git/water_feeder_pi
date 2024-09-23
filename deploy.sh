#!/bin/sh -e
pip install -r requirements.txt --break-system-packages
sudo pip install -r requirements.txt --break-system-packages
if [ -d /opt/app ]; then
    sudo rm -rf /opt/app
fi
sudo mkdir -p /opt/app
sudo cp -r * /opt/app
sudo cp -r app.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable app
sudo systemctl restart app
echo "Complete."