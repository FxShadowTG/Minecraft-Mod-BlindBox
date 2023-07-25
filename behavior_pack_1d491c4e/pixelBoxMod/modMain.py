# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi

@Mod.Binding(name="pixelBoxMod", version="0.0.1")
class pixelBoxMod(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def pixelBoxModServerInit(self):
        serverApi.RegisterSystem("pixelBoxMod","pixelBoxModServerSystem","pixelBoxMod.pixelBoxModServerSystem.pixelBoxModServerSystem")
        print("服务注册成功")

    @Mod.DestroyServer()
    def pixelBoxModServerDestroy(self):
        print("服务销毁成功")

    @Mod.InitClient()
    def pixelBoxModClientInit(self):
        clientApi.RegisterSystem("pixelBoxMod","pixelBoxModClientSystem","pixelBoxMod.pixelBoxModClientSystem.pixelBoxModClientSystem")
        print("客户注册成功")

    @Mod.DestroyClient()
    def pixelBoxModClientDestroy(self):
        print("客户销毁成功")
