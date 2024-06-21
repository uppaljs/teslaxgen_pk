"""Contains anything that communicates with the Teslasm server."""

import json
import time
import threading
from collections import MutableMapping

import paho.mqtt.client as mqtt

from .const import LOGGER


def flatten(dictionary, parent_key=False, separator="."):
    """https://github.com/ScriptSmith/socialreaper/blob/master/socialreaper/tools.py#L8"""
    items = []
    for key, value in dictionary.items():
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator).items())
        elif isinstance(value, list):
            for k, v in enumerate(value):
                items.extend(flatten({str(k): v}, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)


class TeslaPVServer:
    """Class to handle communication with the Teslasm server."""

    def __init__(
        self, inverter_name, client_id, host, port, username, password, interval=120
    ):
        """Initializes the communication."""

        self._inverter_name = inverter_name
        self._host = host
        self._port = port
        self._topic = "xgen/" + username
        self._timing_mutex = threading.RLock()
        self._last_request_time = None
        self._last_response_time = None
        self._callback_mutex = threading.RLock()
        self._in_callback_mutex = threading.Lock()
        self._on_receive = None
        self._interval = interval

        self._client = client = mqtt.Client(client_id)
        client.on_connect = self._mqtt_on_connect
        client.on_message = self._mqtt_on_message
        client.on_log = self._mqtt_on_log
        client.username_pw_set(username, password)

        self.connect(client)

    def connect(self, client):
        """Establishes the mqtt connection"""

        LOGGER.info("%s: Connecting to TeslaPV mqtt broker", self._inverter_name)
        client.connect(self._host, self._port, 60)
        client.loop_start()

    def _mqtt_on_connect(
        self, client, userdata, flags, rc
    ):  # pylint: disable=invalid-name
        """Callback to handle mqtt connection"""

        if rc == 0:
            LOGGER.info(
                "%s: Connected to TeslaPV mqtt broker & subscribing the topic",
                self._inverter_name,
            )
            client.subscribe(self._topic + "/dev")
        else:
            LOGGER.error(
                "%s: Unable to connected to TeslaPV mqtt broker, error code: %s",
                self._inverter_name,
                str(rc),
            )
            time.sleep(1 * 1000)
            self.connect(client)

    async def request(self):
        """Sends a message to request telemetry data"""

        with self._timing_mutex:
            if (
                self._time_since_last_request is None
                or self._last_response_time is not None
                or self._time_since_last_request > self._interval
            ):
                LOGGER.debug(
                    "%s: Requesting update >>>>>>>>>>>>>>>>>>>>>>>>>>",
                    self._inverter_name,
                )

                self._last_request_time = time.perf_counter()
                self._client.publish(self._topic + "/app", "ts")
                self._last_response_time = None

    @property
    def _time_since_last_request(self):
        if self._last_request_time is None:
            time_since_last_request = None
        else:
            time_since_last_request = time.perf_counter() - self._last_request_time

        return time_since_last_request

    def _mqtt_on_message(self, client, userdata, msg):
        """Callback to handle mqtt message"""

        json_message = None

        try:
            payload = str(msg.payload.decode("utf-8", "ignore"))
            json_message = json.loads(payload)
        except Exception as err:  # pylint: disable=broad-except
            LOGGER.exception(
                "%s: Error: %s while handling message: %s",
                self._inverter_name,
                err,
                str(msg.payload),
            )

        if json_message is not None:
            with self._in_callback_mutex:
                try:
                    self._on_receive(flatten(json_message))
                except Exception as err:  # pylint: disable=broad-except
                    LOGGER.error(
                        "%s: Caught exception in callback function %s, error: %s",
                        self._inverter_name,
                        self._on_receive.__name__,
                        err,
                    )

            if "oth" in json_message:
                with self._timing_mutex:
                    self._last_response_time = time.perf_counter()

                LOGGER.debug(
                    "%s: Got full telemetry <<<<<<<<<<<<<<<<<<<<<<<<<<",
                    self._inverter_name,
                )

    def _mqtt_on_log(self, client, userdata, level, buf):
        """Callback to log any errors"""
        if level == mqtt.MQTT_LOG_ERR:
            LOGGER.error(
                "%s: MQTT error: %s:, message %s", self._inverter_name, level, buf
            )

    @property
    def on_receive(self):
        """Callback that is invoked when telemetry about the inverter is received."""

        return self._on_receive

    @on_receive.setter
    def on_receive(self, callback_func):
        """Sets the receive callback implementation.

        Expected signature:
            on_receive_callback(properties)

        properties: telemetry properties returned from the mqtt server.
        """
        with self._callback_mutex:
            self._on_receive = callback_func
