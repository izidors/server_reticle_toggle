# -*- coding: utf-8 -*-

import json
import os

import Keys

from gui import InputHandler
from helpers import dependency

from frameworks.wulf import WindowLayer
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader


MOD_NAME = 'ServerAimToggle'
MOD_VERSION = '1.0.0'

CONFIG_PATH = './mods/configs/promise/serverAimToggle.json'

DEFAULT_CFG = {
    'enabled': True,
    'hotkey': ['KEY_LALT', 'KEY_B'],
    'persist': False,
}

CFG = dict(DEFAULT_CFG)


class SettingsProvider(object):
    settingsCore = dependency.descriptor(ISettingsCore)


settings_provider = SettingsProvider()


def log(message):
    print '[%s] %s' % (MOD_NAME, message)


def load_config():
    global CFG

    CFG = dict(DEFAULT_CFG)

    try:
        if not os.path.isfile(CONFIG_PATH):
            log('Config not found, using defaults')
            return

        with open(CONFIG_PATH, 'r') as config_file:
            data = json.load(config_file)

        if isinstance(data, dict):
            CFG.update(data)

        log('Config loaded')

    except Exception as error:
        log('Config load failed: %s' % error)


def get_hotkey_codes():
    result = []

    for key_name in CFG.get('hotkey', []):
        key_code = getattr(Keys, key_name, None)

        if key_code is None:
            log('Unknown key in config: %s' % key_name)
            continue

        result.append(key_code)

    return result


def is_hotkey_pressed(event):
    hotkeys = get_hotkey_codes()

    if not hotkeys:
        return False

    trigger_key = hotkeys[-1]

    if event.key != trigger_key:
        return False

    for modifier in hotkeys[:-1]:
        if not InputHandler.isKeyDown(modifier):
            return False

    return True


def notify(message):
    try:
        battle = dependency.instance(IAppLoader).getApp()

        if battle is None:
            return

        container = battle.containerManager.getContainer(
            WindowLayer.VIEW
        )

        if container is None:
            return

        battle_page = container.getView()

        if battle_page is None:
            return

        player_messages = battle_page.components.get(
            'battlePlayerMessages'
        )

        if player_messages is None:
            return

        player_messages.as_showPurpleMessageS(
            None,
            message
        )

    except Exception as error:
        log('Notification failed: %s' % error)


def get_server_reticle_state():
    try:
        return bool(
            settings_provider.settingsCore.getSetting(
                'useServerAim'
            )
        )

    except Exception as error:
        log(
            'Cannot read server reticle setting: %s'
            % error
        )

        return None


def set_server_reticle_state(enabled):
    try:
        settings_core = settings_provider.settingsCore

        settings_core.isChangesConfirmed = True

        settings_core.applySettings({
            'useServerAim': enabled
        })

        confirmators = settings_core.applyStorages(True)

        settings_core.confirmChanges(confirmators)
        settings_core.clearStorages()

        return True

    except Exception as error:
        log(
            'Cannot change server reticle setting: %s'
            % error
        )

        return False


def toggle_server_reticle():
    current_value = get_server_reticle_state()

    if current_value is None:
        notify(
            '<font color="#FF8080">'
            'Server Reticle: ERROR'
            '</font>'
        )
        return

    new_value = not current_value

    if not set_server_reticle_state(new_value):
        return

    if new_value:
        message = (
            '<font color="#80FF80">'
            'Server Reticle: ON'
            '</font>'
        )
    else:
        message = (
            '<font color="#FF8080">'
            'Server Reticle: OFF'
            '</font>'
        )

    log(
        'Server Reticle: %s'
        % ('ON' if new_value else 'OFF')
    )

    notify(message)


def on_key_down(event):
    try:
        if not CFG.get('enabled', True):
            return

        if is_hotkey_pressed(event):
            toggle_server_reticle()

    except Exception as error:
        log(
            'Key handler failed: %s'
            % error
        )


def init():
    try:
        load_config()

        InputHandler.g_instance.onKeyDown += on_key_down

        log(
            'v%s loaded successfully'
            % MOD_VERSION
        )

        log(
            'Hotkey: %s'
            % ' + '.join(
                CFG.get('hotkey', [])
            )
        )

    except Exception as error:
        log(
            'Initialization failed: %s'
            % error
        )


init()