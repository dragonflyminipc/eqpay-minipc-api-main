# eqpay-minipc-api

## Requirements

**Ubuntu** 20.04+
**Python** 3.8+

## API update

To update the api you just need to go into the project directory and do "git pull" and then restart the services.

```
cd /root/eqpay-minipc-api
```

```
git pull
```

```
sudo systemctl restart minipc_api
```

```
sudo systemctl restart minipc_api_sync
```

## Deployment


Run these commands to set up the api

```
cd /root/
```

```
git clone git@github.com:equitypay/eqpay.git
```

```
cd eqpay-minipc-api
```

```
sudo apt-get install -y python3-venv
```

```
sudo apt-get install -y libgmp-dev
```

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
pip3 install -r requirements.txt
```

```
cp docs/config.example.py config.py
```

Now create .service files in order to run the api:

```
sudo nano /etc/systemd/system/minipc_api.service
```

```
[Unit]
Description=Uvicorn instance to serve the mini pc api
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/eqpay-minipc-api
Environment="PATH=/root/eqpay-minipc-api/venv/bin"
ExecStart=/root/eqpay-minipc-api/venv/bin/uvicorn app:app --reload --host=0.0.0.0 --port=8888
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Run:

```
sudo systemctl start minipc_api
```

```
sudo systemctl enable minipc_api
```

```
sudo systemctl status minipc_api
```

After the last command you should see "Active: active (running)" in green. You might need to press Ctrl+C if the command line is unavailable.

```
sudo nano /etc/systemd/system/minipc_api_sync.service
```

```
[Unit]
Description=Sync instance to serve the mini pc api
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/eqpay-minipc-api
Environment="PATH=/root/eqpay-minipc-api/venv/bin"
ExecStart=/root/eqpay-minipc-api/venv/bin/python3 sync.py
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Run:

```
sudo systemctl start minipc_api_sync
```

```
sudo systemctl enable minipc_api_sync
```

```
sudo systemctl status minipc_api_sync
```

After the last command you should see "Active: active (running)" in green. You might need to press Ctrl+C if the command line is unavailable.


```
sudo nano /etc/systemd/system/minipc_api_node.service
```

```
[Unit]
Description=Script that restarts an eqpay node if needed to serve the mini pc api
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/eqpay-minipc-api
Environment="PATH=/root/eqpay-minipc-api/venv/bin"
ExecStart=/root/eqpay-minipc-api/venv/bin/python3 start_node.py
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Run:

```
sudo systemctl start minipc_api_node
```

```
sudo systemctl enable minipc_api_node
```

```
sudo systemctl status minipc_api_node
```

After the last command you should see "Active: active (running)" in green. You might need to press Ctrl+C if the command line is unavailable.

The api should be up and running now.
