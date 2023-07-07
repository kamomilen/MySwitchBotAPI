import sys
import json
import time
import hashlib
import hmac
import base64
import uuid
import requests

###########################
###### User settings ######
# open token
token = '' # copy and paste from the SwitchBot app V6.14 or later
# secret key
secret = '' # copy and paste from the SwitchBot app V6.14 or later
###########################

###########################
##### Custom settings #####
API_HOST = 'https://api.switch-bot.com'
DEVICE_URL = f"{API_HOST}/v1.1/devices"
###########################


args = sys.argv
apiHeader = {}

def _build_api(_token, _secret):
    if len(_token) == 0:
        print('Error : Open token is blank. Please set Open token.')
        return -1
    
    if len(_secret) == 0:
        print('Error : Secret key is blank. Please set Secret key.')
        return -1

    nonce = uuid.uuid4()
    t = int(round(time.time() * 1000))
    string_to_sign = '{}{}{}'.format(_token, t, nonce)
    string_to_sign = bytes(string_to_sign, 'utf-8')
    _secret = bytes(_secret, 'utf-8')
    sign = base64.b64encode(hmac.new(_secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

    #Build api header JSON
    apiHeader['Authorization']=_token
    apiHeader['Content-Type']='application/json'
    apiHeader['charset']='utf8'
    apiHeader['t']=str(t)
    apiHeader['sign']=str(sign, 'utf-8')
    apiHeader['nonce']=str(nonce)
    
    return 0


def _get_request(url):
    res = requests.get(url, headers=apiHeader)
    data = res.json()
    if data['message'] == 'success':
        return res.json()
    return {}

def _post_request(url, params):
    res = requests.post(url, data=json.dumps(params), headers=apiHeader) 
    data = res.json()
    if data['message'] == 'success':
        return res.json()
    return {}

def get_device_list():
    try:
        return _get_request(DEVICE_URL)["body"]
    except Exception as e:
        print("Exception message:{0}".format(e.message))
        return

def get_default_device_list():
    devices = get_device_list()
    return devices['deviceList']

def get_virtual_device_list():
    devices = get_device_list()
    return devices['infraredRemoteList']

def get_device_status(deviceId):
    url = f"{DEVICE_URL}/{deviceId}/status"
    try:
        res = _get_request(url)["body"]
        #if res['message'] == 'success':
        #    return res
        return res
    except Exception as e:
        print("Exception message:{0}".format(e.message))
        return {}

def send_device_command(deviceId, command, param='default'):
    url = f"{DEVICE_URL}/{deviceId}/commands"
    params = {
        "command": f"{command}",
        "parameter": f"{param}",
        "commandType": "command"
    }
    try:
        res = _post_request(url, params)
        #if res['message'] == 'success':
        #    return res
        return res
    except Exception as e:
        print("Exception message:{0}".format(e.message))
        return {}

if __name__ == '__main__':
    if _build_api(token, secret) != 0:
        sys.exit(1)
    
    data = get_default_device_list()
    for device in data:
        if len(args) == 1:
            print (device)
            continue

        if device['deviceId'] == args[1]:
            # [Status] args : DeviceID only.
            if len(args) == 2:
                result = get_device_status(device['deviceId']) 
            # [Send] args : DeviceID + Command.
            elif len(args) == 3:
                result = send_device_command(device['deviceId'], args[2])
            # [Send] args : DeviceID + Command + Command parameter.
            elif len(args) >= 4:
                result = send_device_command(device['deviceId'], args[2], args[3])
            print(result)
            break

    sys.exit(0)
