from getmac import get_mac_address as gma

debug = False

db_url_async = "sqlite+aiosqlite:///service.db"

node_endpoint = f"http://rpcuser:{gma()}@localhost:9999"
node_executable = "eqpayd"

github_releases_endpoint = "https://api.github.com/repos/equitypay/eqpay/releases/latest"
run_node_command = f"./node/{node_executable} -rpcuser=rpcuser -rpcpassword={gma()}"
