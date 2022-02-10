import requests
from yaml import load, Loader
import fire


## token, port, URL can be set in your own config yaml for a real application
auth_data = load(open("../.tokens.yaml", "r"), Loader=Loader)
token = auth_data.get('INITIAL_ADMIN')
compose_data = load(open("../skyportal/docker-compose.yaml", "r"), Loader=Loader)
port = compose_data["services"]["web"]["ports"][0].split(":")[0]
URL = "http://localhost"


def api(method, endpoint, data=None):
    headers = {'Authorization': f'token {token}'}
    response = requests.request(method, endpoint, json=data, headers=headers)
    return response

def get_sysinfo():
    response = api('GET', f'{URL}:{port}/api/sysinfo')

    print(f'HTTP code: {response.status_code}, {response.reason}')
    if response.status_code in (200, 400):
        sysinfo = response.json()
        print(f'JSON response: {sysinfo}')

    return sysinfo, response.status_code

if __name__ == "__main__":
    fire.Fire(get_sysinfo)