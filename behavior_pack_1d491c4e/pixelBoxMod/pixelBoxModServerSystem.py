# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import random
ServerSystem = serverApi.GetServerSystemCls()

factory = serverApi.GetEngineCompFactory()

class pixelBoxModServerSystem(ServerSystem):
    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.ListenEvent()
        print("加载监听ing")
        print("加载监听ok")

    def ListenEvent(self):
        #获取levelId
        self.levelId = serverApi.GetLevelId()
        #qpvvf:b525479602_finder_block限时表 30s
        self.finderBlockList = {}
        #错误方块cd表，防止加载过多（默认5秒一次）
        self.errorBlockList = {}
        #福方块cd表，防止加载过多（默认10秒一次）
        self.fuBlockList = {}
        #总方块cd表，防止同时段加载过多（默认1秒一次）
        self.allBlockList = {}  
        #更新实例
        self.timer = None
        #倒计时是否已经开始
        self.isTiming = False
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'OnStandOnBlockServerEvent', self, self.OnStandOnBlockServerEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'ServerBlockUseEvent', self, self.OnServerBlockUseEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'ServerChatEvent', self, self.OnServerChatEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'DestroyBlockEvent', self, self.OnDestroyBlockEvent)      
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'ServerPlayerTryDestroyBlockEvent', self, self.OnServerPlayerTryDestroyBlockEvent)         
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'PlayerAttackEntityEvent', self, self.OnPlayerAttackEntityEvent)         

    def UpdateBlockList(self):
        #减少allBlockList时间表的时间
        for i in self.allBlockList.keys():
            if self.allBlockList[i] > 0:
                self.allBlockList[i] = self.allBlockList[i] - 0.25
            elif self.allBlockList[i] <= 0:
                del self.allBlockList[i]

        #减少finder_block时间表的时间
        for i in self.finderBlockList.keys():
            if self.finderBlockList[i] > 0:
                self.finderBlockList[i] = self.finderBlockList[i] - 0.25
            elif self.finderBlockList[i] <= 0:
                del self.finderBlockList[i]

        #减少errorBlockList时间表的时间
        for i in self.errorBlockList.keys():
            if self.errorBlockList[i] > 0:
                self.errorBlockList[i] = self.errorBlockList[i] - 0.25
            elif self.errorBlockList[i] <= 0:
                del self.errorBlockList[i]

        #减少fuBlockList时间表的时间
        for i in self.fuBlockList.keys():
            if self.fuBlockList[i] > 0:
                self.fuBlockList[i] = self.fuBlockList[i] - 0.25
            elif self.fuBlockList[i] <= 0:  
                del self.fuBlockList[i] 
            

    def OnPlayerAttackEntityEvent(self,args):
        print(args)
        print("666")

    #成功破坏方块
    def OnDestroyBlockEvent(self, args):
        print("destroy:",args)

        playerId = args["playerId"]
        print(playerId)

        #校验总方块cd
        if(playerId in self.allBlockList):
            return

        compByCreateCommand = factory.CreateCommand(self.levelId)

        if(args["fullName"] == "qpvvf:b20298592_basketball_block"):
            print("basketball..")
            compByCreateGame = factory.CreateGame(self.levelId)
            compByCreateGame.SetNotifyMsg("你实在是太美", serverApi.GenerateColor('WHITE'))
            #bgm
            compByCreateCommand.SetCommand("/playsound mob.chicken.say @s")
        #momo方块，人invisibility
        elif(args["fullName"] == "qpvvf:r2641157210_momo_block"):
            print("momo..")
            compByCreateCommand.SetCommand("/effect @p invisibility 600 0",playerId)
            compByCreateCommand.SetCommand("/playsound mob.cat.meow @s")
        #西瓜条方块，播报
        elif(args["fullName"] == "qpvvf:bdnone_watermelon_block"):
            print("watermelon..")
            compByCreateGame = factory.CreateGame(self.levelId)
            compByCreateGame.SetNotifyMsg("家人们谁懂啊", serverApi.GenerateColor('GREEN'))
            #bgm
            compByCreateCommand.SetCommand("/playsound mob.panda.sneeze @s ~~~")
        #帝皇方块，爆金套装
        elif(args["fullName"] == "qpvvf:qpvvf:ksnone_god_block"):
            print("god..")
            
            #bgm
            compByCreateCommand.SetCommand("/playsound mob.panda.sneeze @s ~~~")

        #挂上cd
        self.allBlockList[playerId] = 0.5    #0.5s
        return

    def OnServerChatEvent(self, args):
        playerId = args["playerId"]

        if(playerId in self.finderBlockList):
            username = args["username"]
            text = args["message"]
            target = text.split('#')[1]

            #尝试是否能够以玩家名tp到玩家
            compByCreateCommand = factory.CreateCommand(self.levelId)
            result = compByCreateCommand.SetCommand("/tp @s " + target,playerId)
            if result == True:
                return

            #如果不能就传送到建筑目标
            if target != "" and result == False:
                #获取玩家维度
                compByCreateDimension = factory.CreateDimension(playerId)
                dimension = compByCreateDimension.GetEntityDimensionId()

                #获取玩家位置
                compByCreatePos = factory.CreatePos(playerId)
                pos = compByCreatePos.GetPos()
                posX = int(round(pos[0]))
                posY = int(round(pos[1]))
                posZ = int(round(pos[2]))

                compByCreateFeature = factory.CreateFeature(self.levelId)
                structurePos = compByCreateFeature.LocateStructureFeature(int(target), dimension, (posX,posY,posZ))
                #如果结构坐标不存在
                if structurePos == None:
                    compByCreateMsg = factory.CreateMsg(playerId)
                    compByCreateMsg.NotifyOneMessage(playerId, "§c当前维度不存在该坐标，无法传送")
                    return

                #传送玩家
                compByCreateDimension = factory.CreateDimension(playerId)
                compByCreateDimension.ChangePlayerDimension(dimension, (int(round(structurePos[0])),64,int(round(structurePos[1]))))
                #取消聊天事件
                args["cancel"] == True
                return

    def OnStandOnBlockServerEvent(self,args):
        entityId = args["entityId"]

        if(self.isTiming == False):
            compByCreateGame = factory.CreateGame(self.levelId)
            self.timer = compByCreateGame.AddRepeatedTimer(0.25,self.UpdateBlockList)
            self.isTiming = True

        print(self.allBlockList)

        #校验总方块cd
        if(entityId in self.allBlockList):
            return
    
        #获取方块pos
        newPosX = args["blockX"]
        newPosY = args["blockY"]
        newPosZ = args["blockZ"]

        #获取生物类型
        compByCreateEngineType = factory.CreateEngineType(entityId)
        entityType = compByCreateEngineType.GetEngineTypeStr()

        compByCreateCommand = factory.CreateCommand(self.levelId)

        #当踩在村民肢体错误方块时生成4只僵尸村民(5秒cd)并赋予减速5，失明，凋零4同时赋予僵尸村民和玩家
        if (args["blockName"] == "qpvvf:b439895022_error_block") and entityType == "minecraft:player" and (entityId not in self.errorBlockList):

            compByCreateCommand.SetCommand("/execute @s ~~~ summon minecraft:zombie_villager",entityId)
            compByCreateCommand.SetCommand("/execute @s ~~~ summon minecraft:zombie_villager",entityId)
            compByCreateCommand.SetCommand("/execute @s ~~~ summon minecraft:zombie_villager",entityId)
            compByCreateCommand.SetCommand("/execute @s ~~~ summon minecraft:zombie_villager",entityId)
            compByCreateCommand.SetCommand("/effect @e[r=2] slowness 5 4 false")
            compByCreateCommand.SetCommand("/effect @e[r=2] wither 5 3 false")
            compByCreateCommand.SetCommand("/effect @e[r=2] blindness 5 0 false")
            #bgm
            compByCreateCommand.SetCommand("/playsound mob.zombie.wood @s")
            #挂上cd
            self.errorBlockList[entityId] = 5

        # 当有生物在站在方块上时给予该生物挖掘疲劳10分钟并失明3秒。
        # 如果该生物或《监视者》上存在水，造成2点伤害且失明效果持续10秒
        elif (args["blockName"] == "qpvvf:b175755796_monitor_block"):
            compByCreateBlockInfo = factory.CreateBlockInfo(self.levelId)
            block = compByCreateBlockInfo.GetBlockNew((newPosX,newPosY+1,newPosZ), 0)
            compByCreateEffect = factory.CreateEffect(entityId)
            if (block["name"] == "minecraft:water" or block["name"] == "minecraft:flowing_water"):
                compByCreateEffect.AddEffectToEntity("fatal_poison", 3, 2, False)
                compByCreateEffect.AddEffectToEntity("blindness", 10, 0, False)
                #bgm(是人才播放)
                if entityType == "minecraft:player":
                    compByCreateCommand.SetCommand("/playsound random.splash @s")
            else:
                compByCreateEffect.AddEffectToEntity("mining_fatigue", 600, 0, False)
                compByCreateEffect.AddEffectToEntity("blindness", 3, 0, False)
                #bgm(是人才播放)
                if entityType == "minecraft:player":
                    compByCreateCommand.SetCommand("/playsound random.splash @s")

            #挂上cd
            self.allBlockList[entityId] = 0.25    #0.25s
        return

    #点击方块时
    def OnServerBlockUseEvent(self,args):
        playerId = args["playerId"]
        print(self.allBlockList)
        print(args)

        if(self.isTiming == False):
            compByCreateGame = factory.CreateGame(self.levelId)
            self.timer = compByCreateGame.AddRepeatedTimer(0.25,self.UpdateBlockList)
            self.isTiming = True

        #进入镜子介绍
        isMirror = checkBlindBoxInfoByMirrorTool(playerId,args["blockName"])
        
        #如果是镜子与对应方块则return
        if(isMirror == True):
            return

        #校验总方块cd
        if(playerId in self.allBlockList):
            return
        
        compByCreateBlockUseEventWhiteList = factory.CreateBlockUseEventWhiteList(self.levelId)
        compByCreateBlockUseEventWhiteList.AddBlockItemListenForUseEvent("minecraft:mob_spawner:-1")
        compByCreateGame = factory.CreateGame(self.levelId)
        compByCreateCommand = factory.CreateCommand(self.levelId)
        
        #点击方块后会以当前玩家为坐标搜索5000格内的建筑，并通过聊天栏显示
        #在30秒内输入"传送#生物名"即可传送至坐标建筑
        if (args["blockName"] == "qpvvf:b525479602_finder_block" and (playerId not in self.finderBlockList)):

            compByCreateMsg = factory.CreateMsg(playerId)
            compByCreateMsg.NotifyOneMessage(playerId, "1-末地城\n2-下界要塞\n3-废弃矿井\n4-海底神殿\n5-要塞\n6-沙漠神殿/雪屋/丛林神庙/女巫小屋\n7-村庄\n8-林地府邸\n9-沉船\n10-埋藏的宝藏\n11-水下遗迹\n12-掠夺者前哨站\n13-废弃传送门\n14-堡垒遗迹\n在30秒内输入 §6传送#§a数字或玩家名§f 即可传送到目标")
            #挂上cd
            print("pre take cd")
            self.finderBlockList[playerId] = 30    #30s
            print("take ok")

        #如果是刷怪笼方块则被点击后替换成普通刷怪箱并随机爆出一个生成蛋
        elif(args["blockName"] == "qpvvf:b76969706_spawner_block"):
            print("spaner..")

            blockDict = {
                'name': 'minecraft:mob_spawner',
                'aux': 0
            }
            #替换成刷怪笼
            comp = factory.CreateBlockInfo(self.levelId)
            comp.SetBlockNew((args["x"],args["y"],args["z"]), blockDict, 0, 0, True)
            #爆出蛋
            compByCreateCommand.SetCommand("/summon qpvvf:blindbox_spawner_egg " + str(int(args["x"])) + " " + str(int(args["y"] + 1)) + " " + str(int(args["z"])))
            compByCreateCommand.SetCommand("/execute @s ~~~ kill @e[type=qpvvf:blindbox_spawner_egg,r=500]",playerId)
            #特效
            compByCreateCommand.SetCommand("/summon fireworks_rocket " + str(int(args["x"])) + " " + str(int(args["y"] + 1)) + " " + str(int(args["z"])))
            #bgm
            compByCreateCommand.SetCommand("/playsound item.trident.riptide_3 @s")
        #点击后暗台灯变亮台灯，反之
        elif(args["blockName"] == "qpvvf:dynone_timeday_block"):
            blockDict = {
                'name': 'qpvvf:dynone_timenight_block',
                'aux': 0
            }
            #替换成亮台灯
            comp = factory.CreateBlockInfo(self.levelId)
            comp.SetBlockNew((args["x"],args["y"],args["z"]), blockDict, 0, 0, True)
            #bgm
            compByCreateCommand.SetCommand("/playsound use.ladder @s",playerId)
        elif(args["blockName"] == "qpvvf:dynone_timenight_block"):
            print("准备替换台灯")
            blockDict = {
                'name': 'qpvvf:dynone_timeday_block',
                'aux': 0
            }
            #替换成暗台灯
            comp = factory.CreateBlockInfo(self.levelId)
            comp.SetBlockNew((args["x"],args["y"],args["z"]), blockDict, 0, 0, True)
            #bgm
            compByCreateCommand.SetCommand("/playsound use.ladder @s",playerId)
        #如果是流汗黄豆则让全部实体(c=30)脚下生成岩浆
        elif(args["blockName"] == "qpvvf:bd113887832_ok_block"):
            compByCreateCommand.SetCommand("/execute @e[r=15,c=30] ~~~ setblock ~~~ flowing_lava",playerId)
            #bgm
            compByCreateCommand.SetCommand("/playsound mob.drowned.shoot @s",playerId)
        #如果是流汗水豆则让全部实体(c=30)脚下生成水
        elif(args["blockName"] == "qpvvf:bd113887832_waterok_block"):
            compByCreateCommand.SetCommand("/execute @e[r=15,c=30] ~~~ setblock ~~~ flowing_water",playerId)
            #bgm
            compByCreateCommand.SetCommand("/playsound mob.drowned.shoot @s",playerId)
        #如果是抽象方块则生成5个tnt
        elif(args["blockName"] == "qpvvf:bd440378168_sun_block"):
            print("sun..")
            compByCreateCommand.SetCommand("/execute @e ~~~ summon minecraft:tnt " + str(int(args["x"])) + " " + str(int(args["y"])) + " " + str(int(args["z"])))
            blockDict = {
                'name': 'air',
                'aux': 0
            }
            #替换成空气
            comp = factory.CreateBlockInfo(self.levelId)
            comp.SetBlockNew((args["x"],args["y"],args["z"]), blockDict, 0, 0, True)
            
            #爆出可可豆
            compByCreateCommand.SetCommand("/summon qpvvf:shi " + str(int(args["x"])) + " " + str(int(args["y"] + 2)) + " " + str(int(args["z"])))
            compByCreateCommand.SetCommand("/summon qpvvf:shi " + str(int(args["x"] + 3)) + " " + str(int(args["y"] + 2)) + " " + str(int(args["z"])))
            compByCreateCommand.SetCommand("/summon qpvvf:shi " + str(int(args["x"])) + " " + str(int(args["y"] + 2)) + " " + str(int(args["z"] + 3)))
            compByCreateCommand.SetCommand("/summon qpvvf:shi " + str(int(args["x"] - 3)) + " " + str(int(args["y"] + 2)) + " " + str(int(args["z"] - 3)))
            compByCreateCommand.SetCommand("/execute @s ~~~ kill @e[type=qpvvf:shi,r=500]",playerId)

            #bgm
            compByCreateCommand.SetCommand("/playsound mob.ghast.fireball @s",playerId)

        #如果是盾构机方块则将附近r=100的实体往这个方块吸引并打雷且通知
        elif(args["blockName"] == "qpvvf:dyhuobaobaobao_shield_block"):

            #关闭输出
            ruleDict ={
                'cheat_info': {
                    'sendcommandfeedback': True,
                }
            }

            compByCreateGame.SetGameRulesInfoServer(ruleDict)

            print("shield...")

            for i in range(1, 50):
                compByCreateCommand.SetCommand("/execute @e[r=100] ~~~ tp @s ^^1^0.05 facing " + str(int(args["x"])) + " " + str(int(args["y"])) + " " + str(int(args["z"])),playerId,False)
                compByCreateCommand.SetCommand("/summon lightning_bolt " + str(int(args["x"])) + " " + str(int(args["y"])) + " " + str(int(args["z"])),playerId,False)
                compByCreateGame.SetOneTipMessage(playerId, serverApi.GenerateColor("RED") + str(i * 2 + 2) + "%")

        #如果是全能方块则获取超级buff，30秒
        elif(args["blockName"] == "qpvvf:negnone_neg_block"):
            compByCreateEffect = factory.CreateEffect(playerId)
            compByCreateEffect.AddEffectToEntity("speed", 30, 255, True)
            compByCreateEffect.AddEffectToEntity("resistance", 30, 255, True)
            compByCreateEffect.AddEffectToEntity("jump_boost", 30, 255, True)
            #bgm
            compByCreateCommand.SetCommand("/playsound random.totem @s",playerId)

        #如果是急迫方块则加255的急迫效果
        elif(args["blockName"] == "qpvvf:ks1222355846_haste_block"):
            print("haste..")
            compByCreateEffect = factory.CreateEffect(playerId)
            compByCreateEffect.AddEffectToEntity("haste", 30, 255, True)
            #bgm
            compByCreateCommand.SetCommand("/playsound random.totem @s",playerId)

        #如果是眼镜男方块则立刻挂掉
        elif(args["blockName"] == "qpvvf:bdnone_dead_block"):
            print("dead..")
            compByCreateGame.SetNotifyMsg("§6爆金币咯！", serverApi.GenerateColor('WHITE'))
            compByCreateCommand.SetCommand("kill @s",playerId)
            #bgm
            compByCreateCommand.SetCommand("/playsound note.cow_bell @s",playerId)

        #如果是尺寸方块则一直长大
        elif(args["blockName"] == "qpvvf:b34127671_changesize_block"):
            print("size..")
            compByCreateScale = factory.CreateScale(playerId)
            size = compByCreateScale.GetEntityScale()
            if size < 20:
                compByCreateScale.SetEntityScale(playerId, size + 0.1)
                compByCreateGame.SetNotifyMsg("§a当前模型尺寸：" + str(round(size,1)) + " 。加油，快炸了！"), serverApi.GenerateColor('WHITE')
            else:
                compByCreateGame.SetNotifyMsg("§c炸了！"), serverApi.GenerateColor('WHITE')
                compByCreateScale.SetEntityScale(playerId,1)
                compByCreateCommand.SetCommand("/summon tnt ~~~",playerId)
                #bgm
                compByCreateCommand.SetCommand("/playsound random.explode @s",playerId)
            #bgm
            compByCreateCommand.SetCommand("/playsound note.cow_bell @s",playerId)

        #如果是福方块则r=100,c=30实体产生tnt，要有cd不然卡死
        elif(args["blockName"] == "qpvvf:bnone_bless_block" and (playerId not in self.fuBlockList)):
            print("fu..")
            compByCreateCommand.SetCommand("/execute @e[r=100,c=30] ~~~ summon tnt ~~~",playerId)
            #bgm
            compByCreateCommand.SetCommand("/playsound mob.ghast.fireball @s",playerId)
            #挂上cd
            self.fuBlockList[playerId] = 10

        #冰鬼方块r=30,c=30实体召唤闪电并结冰
        elif(args["blockName"] == "qpvvf:bnone_iceghost_block"):
            print("iceghost..")
            compByCreateCommand.SetCommand("/execute @e[r=100,c=30] ~~~ summon lightning_bolt ~~~",playerId)
            compByCreateCommand.SetCommand("/execute @e[r=100,c=30] ~~~ fill ~~~ ~~1~ ice 0 replace air 0",playerId)
            #bgm
            compByCreateCommand.SetCommand("/playsound mob.ghast.fireball @s",playerId)

        #闪电方块,召唤闪电法阵在点击者附近一圈
        elif(args["blockName"] == "qpvvf:bnone_lightning_block"):
            print("lightning..")
            compByCreateCommand.SetCommand("/execute @p ~~~ summon lightning_bolt ^5^^",playerId)
            compByCreateCommand.SetCommand("/execute @p ~~~ summon lightning_bolt ^-5^^",playerId)
            compByCreateCommand.SetCommand("/execute @p ~~~ summon lightning_bolt ^^^5",playerId)
            compByCreateCommand.SetCommand("/execute @p ~~~ summon lightning_bolt ^^^-5",playerId)
            compByCreateCommand.SetCommand("/execute @p ~~~ summon lightning_bolt ^5^^5",playerId)
            compByCreateCommand.SetCommand("/execute @p ~~~ summon lightning_bolt ^-5^^5",playerId)
            compByCreateCommand.SetCommand("/execute @p ~~~ summon lightning_bolt ^-5^^-5",playerId)
            compByCreateCommand.SetCommand("/execute @p ~~~ summon lightning_bolt ^5^^-5",playerId)
            #bgm
            compByCreateCommand.SetCommand("/playsound mob.ghast.fireball @s",playerId)

        #如果是告示牌方块则广播上方的文字
        elif(args["blockName"] == "qpvvf:bnone_sign_block"):
            print("sign..")
            compByCreateBlockInfo = factory.CreateBlockInfo(playerId)
            text = compByCreateBlockInfo.GetSignBlockText((int(args["x"]),int(args["y"]+1),int(args["z"])))
            
            if text == None:
                compByCreateMsg = factory.CreateMsg(playerId)
                compByCreateMsg.NotifyOneMessage(playerId, "上方未放置告示牌，无法广播内容", "§c")
            else:
                compByCreateCommand.SetCommand("/execute @p ~~~ say " + text,playerId)
                #bgm
                compByCreateCommand.SetCommand("/playsound raid.horn @s",playerId)
        
        elif(args["blockName"] == "qpvvf:bnone_threegodpillars_block"):
            print("threegodpillars..")
            compByCreateMsg = factory.CreateMsg(playerId)
            
            #放置结构
            comp = serverApi.GetEngineCompFactory().CreateGame(self.levelId)
            result = comp.PlaceStructure(None, (args["x"], args["y"], args["z"]), "qpvvf:threegodpillars", 0, 0)
            
            #定义物品表
            itemList = [
                {
                    'itemName': 'minecraft:redstone_block',
                    'count': 1,
                    'auxValue': 0,
                },
                {
                    'itemName': 'minecraft:lapis_block',
                    'count': 2,
                    'auxValue': 0,
                },
                {
                    'itemName': 'minecraft:diamond',
                    'count': 2,
                    'auxValue': 0,
                },
                {
                    'itemName': 'minecraft:totem',
                    'count': 1,
                    'auxValue': 0,
                },
                {
                    'itemName': 'minecraft:gold_ingot',
                    'count': 5,
                    'auxValue': 0,
                }
                ,
                {
                    'itemName': 'minecraft:iron_ingot',
                    'count': 2,
                    'auxValue': 0,
                }
                ,
                {
                    'itemName': 'minecraft:torch',
                    'count': 16,
                    'auxValue': 0,
                }
                ,
                {
                    'itemName': 'minecraft:bed',
                    'count': 1,
                    'auxValue': 0,
                }
            ]
            #随机次数
            count = random.randrange(1,len(itemList))

            # 准备生成物品到箱子
            compByCreateItem = factory.CreateItem(self.levelId)
            #循环x次
            for i in range(count):
                #随机箱子格数
                slot = random.randrange(0,26)
                #每次从itemList里抽取count个物品
                #生成物品到箱子
                compByCreateItem.SpawnItemToContainer(random.choice(itemList), slot, (int(args["x"]+2),int(args["y"]+1),int(args["z"]+3)), 0)
            
            # #todo
            # compByCreateMsg.NotifyOneMessage(playerId, "此方块能量过于强大，你暂时无法驾驭", "§c")
            #bgm
            compByCreateCommand.SetCommand("/playsound random.toast @s",playerId)
            print("over..",result)
        
        #指令包方块，点击后背包获得三种cb状态的方块
        elif(args["blockName"] == "qpvvf:dynone_cbtool_block"):
            print("cbTool..")
            compByCreateCommand.SetCommand("/give @s command_block 1",playerId)
            compByCreateCommand.SetCommand("/give @s chain_command_block 1",playerId)
            compByCreateCommand.SetCommand("/give @s repeating_command_block 1",playerId)
            #bgm
            compByCreateCommand.SetCommand("/playsound ui.loom.take_result @s",playerId)
        
        #随机时间方块，点击后随机一段时间
        elif(args["blockName"] == "qpvvf:negnone_changetime_block"):
            print("changetime..")
            compByCreateTime = factory.CreateTime(self.levelId)
            # 随机时间
            time = random.randrange(0,24000)
            compByCreateTime.SetTimeOfDay(time)
            #bgm
            compByCreateCommand.SetCommand("/playsound ui.cartography_table.take_result @s",playerId)
        
        #镜子方块，提醒人靠近方块可照镜子
        elif(args["blockName"] == "qpvvf:rnone_mirror_block"):
            print("mirror..")
            compByCreateMsg = factory.CreateMsg(playerId)    
            compByCreateMsg.NotifyOneMessage(playerId, "靠近该方块使屏幕变成一片黑，你就会发现一个靓仔或靓女", "§b")
            #bgm
            compByCreateCommand.SetCommand("/playsound beacon.power @s",playerId)
        
        #招聘方块
        elif(args["blockName"] == "qpvvf:bnone_recruit_block"):
            print("recruit..")
            compByCreateMsg = factory.CreateMsg(playerId)
            compByCreateMsg.NotifyOneMessage(playerId, "你想成为一名资源中心的贡献者吗？欢迎加入刷怪笼工作室，目前正在初步招人中，如果你会做地图/编写mod/画材质/画皮肤，都可以加入，详情可点击开发者主页查看。", "§a")
            #bgm
            compByCreateCommand.SetCommand("/playsound beacon.power @s",playerId)
        
        #石头剪刀布方块
        elif(args["blockName"] == "qpvvf:bnone_rps_block"):
            print("rps..")

            #获取玩家名字
            compByCreateName = factory.CreateName(playerId)
            playerName = compByCreateName.GetName()

            #随机
            num = random.randrange(0,3)
            result = ""
            if num == 0:
                result = "§7§l石头"
            elif num == 1:
                result = "§6§l剪刀"
            elif num == 2:
                result = "§r§l布"

            compByCreateMsg = factory.CreateMsg(self.levelId)
            compByCreateMsg.SendMsg(playerName,result)

            #bgm
            compByCreateCommand.SetCommand("/playsound block.scaffolding.hit @s",playerId)

        #红石大炮方块
        elif(args["blockName"] == "qpvvf:dynone_redstoneartillery_block"):
            print("redstoneArtillery..")

            #放置结构
            comp = serverApi.GetEngineCompFactory().CreateGame(self.levelId)
            result = comp.PlaceStructure(None, (args["x"], args["y"], args["z"]), "qpvvf:redstoneartillery", 0, 0)
            
            print("result,",result)
            #bgm
            compByCreateCommand.SetCommand("/playsound ambient.cave @s",playerId)
        
        #沙子电路方块
        elif(args["blockName"] == "qpvvf:ksnone_sandcircuit_block"):
            print("sandcircuit..")

            #放置结构
            comp = serverApi.GetEngineCompFactory().CreateGame(self.levelId)
            result = comp.PlaceStructure(None, (args["x"], args["y"], args["z"]), "qpvvf:sandcircuit", 0, 0)
            print("result,",result)
            #bgm
            compByCreateCommand.SetCommand("/playsound ambient.cave @s",playerId)
        
        #挂上cd
        self.allBlockList[playerId] = 0.5    #0.5s
        
    
    def UnListenEvent(self):
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'OnStandOnBlockServerEvent', self, self.OnStandOnBlockServerEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'ServerBlockUseEvent', self, self.OnServerBlockUseEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'ServerChatEvent', self, self.OnServerChatEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'DestroyBlockEvent', self, self.OnDestroyBlockEvent)      
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'ServerPlayerTryDestroyBlockEvent', self, self.OnServerPlayerTryDestroyBlockEvent)      
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'PlayerAttackEntityEvent', self, self.OnPlayerAttackEntityEvent)         
    def Destroy(self):
        compByCreateGame = factory.CreateGame(self.levelId)
        compByCreateGame.CancelTimer(self.timer)
        self.UnListenEvent()

#检查玩家手上拿的是否是镜子
def checkBlindBoxInfoByMirrorTool(playerId,block):
    compByCreateItem = factory.CreateItem(playerId)
    itemDict = compByCreateItem.GetPlayerItem(serverApi.GetMinecraftEnum().ItemPosType.CARRIED, 0)
    
    if itemDict == None:
        return False
    
    if itemDict["newItemName"] == "qpvvf:identify_mirror":
        compByCreateMsg = factory.CreateMsg(playerId) 
        compByCreateCommand = factory.CreateCommand(0)
        compByCreateCommand.SetCommand("/playsound block.grindstone.use @s")
        if block == "qpvvf:b175755796_monitor_block":   
            compByCreateMsg.NotifyOneMessage(playerId, "当有生物站在该方块上时会获得挖掘疲劳与失明。如果该方块上存在水，则变成造成中毒和失明效果", "§e")
            return True
        elif block == "qpvvf:b20298592_basketball_block":
            compByCreateMsg.NotifyOneMessage(playerId, "敲掉会显示一段文字并配有鲲声（和谐）", "§e")
            return True
        elif block == "qpvvf:b34127671_changesize_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后自己会变大，到达一定程度后会还原大小", "§e")
            return True
        elif block == "qpvvf:b439895022_error_block":
            compByCreateMsg.NotifyOneMessage(playerId, "站在上方会产生僵尸村民以及获得失明效果", "§e")
            return True
        elif block == "qpvvf:b439895022_error2_block":
            compByCreateMsg.NotifyOneMessage(playerId, "用于合成村民肢体错误方块的原料", "§e")
            return True
        
        elif block == "qpvvf:b525479602_finder_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后在一定时间内输入对应的指令即可传送到建筑结构坐标，也可用来传送到其它玩家", "§e")
            return True
        elif block == "qpvvf:b76969706_blindBox_block":
            compByCreateMsg.NotifyOneMessage(playerId, "盲盒方块，挖掉后随机获得一颗盲盒子", "§e")
            return True
        elif block == "qpvvf:b76969706_spawner_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后产生一格刷怪笼并赠送随机生成蛋", "§e")
            return True
        elif block == "qpvvf:bd113887832_ok_block":
            compByCreateMsg.NotifyOneMessage(playerId, "周围的实体脚下会生成岩浆", "§e")
            return True
        elif block == "qpvvf:bd113887832_waterok_block":
            compByCreateMsg.NotifyOneMessage(playerId, "周围的实体脚下会产生水", "§e")
            return True
        elif block == "qpvvf:bd440378168_sun_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后会产生TNT和咖啡豆，如果周围的实体越多，TNT效果越强", "§e")
            return True
        elif block == "qpvvf:bdnone_dead_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后会GG", "§e")
            return True
        elif block == "qpvvf:bnone_sign_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后会将上方告示牌的内容输出到聊天栏上", "§e")
            return True

        elif block == "qpvvf:bdnone_fertilizer_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后会随机爆出种植方面的东西", "§e")
            return True
        elif block == "qpvvf:bdnone_watermelon_block":
            compByCreateMsg.NotifyOneMessage(playerId, "敲掉会显示一段文字并配有特效声（和谐）", "§e")
            return True
        elif block == "qpvvf:bnone_bless_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后会周围的实体脚下会产生TNT", "§e")
            return True
        elif block == "qpvvf:bnone_iceghost_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后周围的实体脚下会产生冰柱并遭雷劈", "§e")
            return True
        elif block == "qpvvf:bnone_lightning_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后方块处会产生闪电", "§e")
            return True
        elif block == "qpvvf:bnone_recruit_block":
            compByCreateMsg.NotifyOneMessage(playerId, "显示招聘信息", "§e")
            return True
        elif block == "qpvvf:ksnone_sandcircuit_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后会生成一座沙子电路门，怀念经典", "§e") 
            return True
        elif block == "qpvvf:bnone_rps_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后会随机出拳并输出到聊天栏上", "§e")
            return True
        elif block == "qpvvf:bnone_threegodpillars_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后生成一座三圣柱领域", "§e")
            return True
        elif block == "qpvvf:dyhuobaobaobao_shield_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后将周围的实体传送到方块顶端并被雷劈", "§e")
            return True
        elif block == "qpvvf:dynone_cbtool_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后获得三种不一样的命令方块", "§e")
            return True
        elif block == "qpvvf:dynone_redstoneartillery_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后生成一座红石大炮", "§e")
            return True
        elif block == "qpvvf:dynone_timeday_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后亮灯", "§e")
            return True
        elif block == "qpvvf:dynone_timenight_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后暗灯", "§e")  
            return True
        elif block == "qpvvf:ks1222355846_haste_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后获得一段时间的急迫", "§e") 
            return True
        elif block == "qpvvf:ksnone_god_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后产出金质装备", "§e") 
            return True
        elif block == "qpvvf:ksnone_randomsapling_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后爆出随机树苗", "§e") 
            return True
        elif block == "qpvvf:negNone_changetime_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后随机改变世界时间", "§e") 
            return True
        elif block == "qpvvf:negnone_neg_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后获得超快的移速和其它属性", "§e")        
            return True
        elif block == "qpvvf:r2641157210_momo_block":
            compByCreateMsg.NotifyOneMessage(playerId, "点击后获得透明效果", "§e")
            return True
        elif block == "qpvvf:r590678453_rainbowglass_block":
            compByCreateMsg.NotifyOneMessage(playerId, "装饰作用", "§e")
            return True
        elif block == "qpvvf:r590678453_rainbowglass2_block":
            compByCreateMsg.NotifyOneMessage(playerId, "装饰作用", "§e")
            return True
        elif block == "qpvvf:rfxshadow_beetroot_block":
            compByCreateMsg.NotifyOneMessage(playerId, "挖掉后产出随机红薯", "§e")
            return True
        elif block == "qpvvf:rnone_mirror_block":
            compByCreateMsg.NotifyOneMessage(playerId, "靠近该方块使屏幕变成一片黑，你就会发现一个靓仔或靓女", "§e")
            return True

        return False
    return False
