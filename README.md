# bus-time

## Example Config File
```json
{
    "api_key": "real cta bustracker api key",
    "stop_id": "cta bus stop id for predictions",
    "route_id": "cta bus route id for prediction",
    "s3_bucket": "s3 bucket name where predictions are saved",
    "aws": {
        "region_name": "for use with s3 resource client",
        "aws_access_key_id": "for user with permission to s3_bucket",
        "aws_secret_access_key": "for user with permission to s3_bucket"
    },
    "led_pins": {
        "red": 1,
        "yellow": 2,
        "green": 3
    },
    "arrival_thresholds": {
        "yellow": {
            "min": 10,
            "max": 12
        },
        "green": {
            "min": 5,
            "max": 7
        }
    }    
}
```


## Deploy to Raspberry Pi
```bash
$ cd playbooks/
$ ansible-playbook raspberrypi.yaml
```
```bash
$ rsync -r rpi/ pi@penelopi.local:bus_time_alert/
$ ssh pi@penelopi.local
$ cd bus_time_alert
$ sudo pip3 install -r requirements.txt
```

## Schedule minute cron job on Raspberry Pi
```
* * * * * python3 bus_time_alert/main.py bus_time_alert/config.json
```
