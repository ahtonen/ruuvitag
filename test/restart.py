import requests
from utils import get_env_var

headers = {"Content-Type": "application/json"}
data = {"appId": get_env_var("BALENA_APP_ID")}
url = "{}/v1/restart?apikey={}".format(
    get_env_var("BALENA_SUPERVISOR_ADDRESS"), get_env_var("BALENA_SUPERVISOR_API_KEY")
)

# Post restart command to supervisor
response = requests.post(url, json=data, headers=headers)
