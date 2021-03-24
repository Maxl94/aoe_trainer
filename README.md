# AoE Trainer
## How to use
First make sure you have a working python environment. The script was developed with `python 3.6`, but I think any greater version should also work.
To start the trainer clone or download the repository and open a terminal in the folder (Powershell, CMD, Bash).

Next use `pip install -r requirements.txt` to install the need libraries. There are used a lot, because of the UI framework. 

Now got to `resources` and open the `settings.json` in an editor. Here you can customize your hotkeys and times (always in seconds) for warning sounds, use lower letters. Currently combinations like `STRG+{any letter}` are not supported. I plan this for the future.

To start the application, reopen your terminal and enter `python aoe_trainer.py`, a UI to control the trainer should open.