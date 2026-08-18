# -*- coding: utf-8 -*-

import Keys

from gui import InputHandler
from helpers import dependency

from frameworks.wulf import WindowLayer
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader


MOD_NAME = 'ServerReticleToggle'
MOD_VERSION = '1.0.0'

HOTKEY = Keys.KEY_F9


class SettingsProvider(object):
    settingsCore = dependency.descriptor(ISettingsCore)


settings_provider = SettingsProvider()


def log(message):
    print '[%s] %s' % (MOD_NAME, message)


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
        notify(
            '<font color="#FF8080">'
            'Server Reticle: ERROR'
            '</font>'
        )
        return

    if new_value:
        state = 'ON'
        message = (
            '<font color="#80FF80">'
            'Server Reticle: ON'
            '</font>'
        )
    else:
        state = 'OFF'
        message = (
            '<font color="#FF8080">'
            'Server Reticle: OFF'
            '</font>'
        )

    log('Server Reticle: %s' % state)
    notify(message)


def on_key_down(event):
    try:
        if event.key == HOTKEY:
            toggle_server_reticle()

    except Exception as error:
        log(
            'Key handler failed: %s'
            % error
        )


def init():
    try:
        InputHandler.g_instance.onKeyDown += on_key_down

        log(
            'v%s loaded successfully - hotkey F9'
            % MOD_VERSION
        )

    except Exception as error:
        log(
            'Initialization failed: %s'
            % error
        )


init()