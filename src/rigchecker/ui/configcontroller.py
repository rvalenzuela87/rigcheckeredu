from PySide2.QtCore import QObject, Slot, Signal

from .. import getconf
reload(getconf)

class ConfigController(QObject):
    configuration_saved = Signal([str], [None])
    save_configuration_failed = Signal([str], [None])

    configuration_reset = Signal([str], [dict], [None])
    reset_configuration_failed = Signal([str], [None])

    def __init__(self, *args, **kwargs):
        super(ConfigController, self).__init__(*args, **kwargs)

    @Slot(dict)
    def saveConfiguration(self, conf):
        try:
            assert getconf.save_conf(conf) is True
        except(AssertionError, RuntimeError, Exception) as exc:
            self.save_configuration_failed[str].emit(exc.message)
            self.save_configuration_failed[None].emit()

            return False
        else:
            self.configuration_saved[str].emit("Configuration changes saved")
            self.configuration_saved[None].emit()

            return True

    @Slot()
    def resetConfiguration(self):
        try:
            assert getconf.reset_conf_to_default() is True
        except(AssertionError, RuntimeError, Exception) as exc:
            self.reset_configuration_failed[str].emit(exc.message)
            self.reset_configuration_failed[None].emit()

            return False
        else:
            self.configuration_reset[str].emit("Configuration reset to defaults")
            self.configuration_reset[dict].emit(getconf.get_def_conf())
            self.configuration_reset[None].emit()

            return True
