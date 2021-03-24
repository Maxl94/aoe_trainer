from queue import Queue
from threading import Thread
import time
import json
import keyboard
from typing import List
from playsound import playsound
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlText, ControlLabel, ControlButton


class Alarm(Thread):
    def __init__(self, keyQueue: Queue,  name: str, alarmThreshold: float, hotkeys: List[str]) -> None:
        super().__init__()
        currentTime = time.time()
        self._keyQueue = keyQueue
        self._hotkeys = {hotkey: currentTime for hotkey in hotkeys}
        self._name = name
        self._alarmThreshold = alarmThreshold
        self._alarmCoolDown = 3
        self._running = True

    def run(self) -> None:
        print(f'Keylogger "{self._name}" started')
        lastAlarm = time.time()

        while self._running:

            if not self._keyQueue.empty():
                keyHit = self._keyQueue.get(timeout=1)

                if keyHit.event_type == 'up' and self._hotkeys.get(keyHit.name) is not None:
                    print(f'Hotkey hit: {keyHit.name}')
                    self._hotkeys[keyHit.name] = time.time()
                elif keyHit.event_type == 'down' and keyHit.name in ('strg', 'alt', 'shift'):
                    keyHitNext = self._keyQueue.get(timeout=1)
                    combinedHotkey: str = keyHit.name + '+' + keyHitNext.name
                    print(f'Hotkey hit: {combinedHotkey}')
                    self._hotkeys[combinedHotkey] = time.time()
                    self._keyQueue.task_done()

                self._keyQueue.task_done()
                

            sendAlarm: bool = True
            currentTime = time.time()

            for _, value in self._hotkeys.items():
                if value + self._alarmThreshold > currentTime:
                    sendAlarm = False

            if sendAlarm and lastAlarm + self._alarmCoolDown < currentTime:
                print('ALARM!!!!')
                playsound('resources\stop_idealing.mp3')
                lastAlarm = currentTime

        print(f'Keylogger "{self._name}" stopped')

    def stop(self):
        self._running = False


class AoEActivityTrainer(BaseWidget):

    def __init__(self, *args, **kwargs):
        super().__init__('AoE II Activity Trainer')

        self._alarms: List[Alarm] = []
        self._keyQueue: Queue = Queue()

        with open('resources\settings.json') as f:
            self._settings = json.load(f)

        if len(self._settings['profiles']) != 1:
            print("You must add exact one profile. Currently more are not supported.")
            return

        # Definition of the forms fields
        self._text = ControlLabel('Active profiles: \n' + '\n'.join(' + ' +
                                  profile['name'] for profile in self._settings['profiles']))

        self._thresholdText = ControlText('Treshold in seconds when to inform you about ideling')
        self._startbutton = ControlButton('Start')
        self._stopButton = ControlButton('Stop')

        self._thresholdText.value = str(self._settings['profiles'][0]['alarmThreshold'])

        # Define the event that will be called when the run button is processed
        self._startbutton.value = self.__runEvent
        self._stopButton.value = self.__stopEvent

        # Define the organization of the Form Controls
        self._formset = [
            '_text',
            '_thresholdText',
            ('_startbutton', '_stopButton'),
        ]

    def __runEvent(self):
        if len(self._alarms) != 0:
            self.__stopEvent()

        print("Starting all alarms")
        for profile in self._settings['profiles']:
            name: str = profile['name']
            alarmThreshold = float(self._thresholdText.value)
            hotkeys = profile['keys']

            alarm: Alarm = Alarm(
                keyQueue=self._keyQueue, name=name, alarmThreshold=alarmThreshold, hotkeys=hotkeys)
            self._alarms.append(alarm)

        for alarm in self._alarms:
            alarm.start()

        keyboard.start_recording(self._keyQueue)
        self._stopButton.checked = True

    def __stopEvent(self):
        if len(self._alarms) != 0:
            print("Stopping all active alarms")
            keyboard.stop_recording()
            for alarm in self._alarms:
                alarm.stop()
                alarm.join()
                del alarm
            self._alarms = []


if __name__ == '__main__':

    from pyforms import start_app
    start_app(AoEActivityTrainer)
