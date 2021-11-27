import pickle
from pickle_secure import pickle_secure
import os
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
import paho.mqtt.client as mqtt
import json
import re
import time

MQTT_SERVER = "MQTT_SERVER"
MQTT_PORT = 1883
MQTT_USER = "MQTT_USER"
MQTT_PW = "MQTT_PW"


class FindMyPhone:
    cookie_path = "/session/cookies.pkl"
    url_home: str = "https://www.google.com/"
    url_find: str = "https://www.google.com/search?q=find+my+mobile&ie=UTF-8&oe=UTF-8"

    def ring_device(self, ringDevice: str = None, cookies: Dict[str, str] = None):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)

        self.driver.get(self.url_home)

        self.load_cookies()

        if cookies is not None:
            self.set_cookies_from_dict(cookies)

        self.driver.refresh()

        if not self.check_logged_in():
            return "Not logged in"

        if ringDevice is None:
            return "no ringDevice - nothing todo (session cookie maintained)"

        return self.trigger_ring_device(ringDevice)

    def trigger_ring_device(self, device_name: str):
        self.driver.get(
            "https://www.google.com/search?q=find+my+mobile&ie=UTF-8&oe=UTF-8"
        )

        btn_for_dropdown = self.driver.find_elements(
            By.TAG_NAME, ".gws-action__act-device-label"
        )
        if len(btn_for_dropdown) == 0:
            return "dropdown not found"
        btn_for_dropdown = btn_for_dropdown[0]
        btn_for_dropdown.click()

        btn_device_in_dropdown = btn_for_dropdown.find_elements(
            By.XPATH, f"//*[contains(text(), '{device_name}')]"
        )
        if len(btn_device_in_dropdown) == 0:
            return "device not found"
        btn_device_in_dropdown = btn_device_in_dropdown[0]
        btn_device_in_dropdown.click()

        ring_button = self.driver.find_elements(By.ID, "act-ring-link")
        if len(ring_button) == 0:
            return "ring button not found"
        ring_button = ring_button[0]
        time.sleep(1)
        ring_button.click()
        time.sleep(1)
        return f"successfully triggered {device_name}"

    def check_logged_in(self):
        self.driver.get(self.url_home)
        self.driver.refresh()

        loginBtnQuery = self.driver.find_elements(
            By.XPATH, "//a[contains(@href,'ServiceLogin')]"
        )

        if len(loginBtnQuery) == 0:
            self.save_cookies()
            return True

        return False

    def dispose(self):
        self.driver.quit()

    def save_cookies(self):
        with open(self.cookie_path, "wb") as f:
            pickle_secure.dump(
                self.driver.get_cookies(), f, key='asdfjnsadf5&%/"§("§sdfmsdf'
            )

    def load_cookies(self):
        if not os.path.isfile(self.cookie_path):
            return
        with open(self.cookie_path, "rb") as f:
            cookies = pickle_secure.load(f, key='asdfjnsadf5&%/"§("§sdfmsdf')
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def set_cookies_from_dict(self, cookies):
        for key, value in cookies.items():
            self.driver.add_cookie({"name": key, "value": value})


def log(client, message):
    print(message)
    client.publish("FindMyPhone/log", payload=message)


def on_connect(client, userdata, flags, rc):
    client.subscribe("FindMyPhone/ring")
    client.subscribe("FindMyPhone/setCookie")


def on_message(client, userdata, msg):
    if msg.topic == "FindMyPhone/ring":
        mobile_name = re.sub(
            r"[^A-Za-z0-9-_ ]+", "", msg.payload.decode("utf-8").strip()
        )
        print(f"request for {mobile_name}")
        fmp = FindMyPhone()
        res = fmp.ring_device(ringDevice=mobile_name)
        fmp.dispose()
        log(client, res)
    elif msg.topic == "FindMyPhone/setCookie":
        print(f"request for setCookie")
        try:
            cookies = json.loads(msg.payload.decode("utf-8"))
            cookies = {item["name"]: item["value"] for item in cookies}
            fmp = FindMyPhone()
            res = fmp.ring_device(cookies=cookies)
            fmp.dispose()
            log(client, res)
        except Exception as e:
            print("error while setCookie: " + repr(e))
            log(client, "error while setCookie: " + repr(e))


def main():
    client = mqtt.Client(
        client_id="FindMyPhone",
        clean_session=True,
    )
    client.on_connect = on_connect
    client.on_message = on_message

    client.username_pw_set(username=MQTT_USER, password=MQTT_PW)
    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    log(client, "Mqtt connected")
    client.loop_start()

    while True:
        fmp = FindMyPhone()
        res = fmp.ring_device()  # maintain session
        fmp.dispose()
        log(client, res)
        time.sleep(43200)


if __name__ == "__main__":
    main()
