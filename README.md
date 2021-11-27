# MqttFindMyPhone
Triggers Android FindMyPhone requests via mqtt as there is no official api.

## Warning
This solution requires to store your Google session cookies. If someone steals them, they can be used nearly as your credentials (e.g. access your mails, ...).

Also, this is not a well build tool, it's just the solution I use for myself.

## How to use
- clone the repo
```bash
git clone https://github.com/lukeIam/MqttFindMyPhone.git
```
- build the docker image
```bash
docker-compose build
```
- run the docker container
```
docker-compose up -d
```
- wait until a message `Not logged in` is published on topic `FindMyPhone/log`
- open a private tab in your browser, login to https://google.com and export the cookies with [EditThisCookie](https://www.editthiscookie.com)
- post the cookie-json as payload to `FindMyPhone/setCookie` (only required once - cookies are stored and refreshed automatically)
- post the device name (exactly as shown [here](https://www.google.com/android/find)) to `FindMyPhone/ring` to trigger a ring (takes a few seconds)
