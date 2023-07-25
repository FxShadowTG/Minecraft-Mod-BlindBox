# -*- coding: utf-8 -*-

from mod.common.mod import Mod


@Mod.Binding(name="Script_NeteaseModfqCBbRyM", version="0.0.1")
class Script_NeteaseModfqCBbRyM(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def Script_NeteaseModfqCBbRyMServerInit(self):
        pass

    @Mod.DestroyServer()
    def Script_NeteaseModfqCBbRyMServerDestroy(self):
        pass

    @Mod.InitClient()
    def Script_NeteaseModfqCBbRyMClientInit(self):
        pass

    @Mod.DestroyClient()
    def Script_NeteaseModfqCBbRyMClientDestroy(self):
        pass
