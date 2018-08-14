import os
import time
import pUtil
from SocketServer import BaseRequestHandler 
from Configuration import Configuration

class UpdateHandler(BaseRequestHandler):
    """ update self.__env['jobDic'] status with the messages sent from child via socket, do nothing else """
    
    def __init__(self, request, client_address, server):
        self.__env = Configuration()
        BaseRequestHandler.__init__(self, request, client_address, server)

    def handle(self):
        try:
            pUtil.tolog("Connected from %s" % str(self.client_address))
            data = self.request.recv(4096)
            jobmsg = data.split(";")
            pUtil.tolog("--- TCPServer: Message received from child is : %s" % str(jobmsg))
            jobinfo = {}
            for i in jobmsg:
                if not i: continue # skip empty line
                try:
                    jobinfo[i.split("=")[0]] = i.split("=")[1]
                except Exception, e:
                    pUtil.tolog("!!WARNING!!1999!! Exception caught: %s" % (e))
    
            # update self.__env['jobDic']
            for k in self.__env['jobDic'].keys():
                if self.__env['jobDic'][k][1].jobId == jobinfo["jobid"]: # job pid matches
#                if self.__env['jobDic'][k][2] == int(jobinfo["pgrp"]) and self.__env['jobDic'][k][1].jobId == int(jobinfo["jobid"]): # job pid matches
                    # protect with try statement in case the pilot server goes down (jobinfo will be corrupted)
                    try:
                        self.__env['jobDic'][k][1].currentState = jobinfo["status"]
                        if jobinfo["status"] == "stagein":
                            self.__env['stagein'] = True
                            self.__env['stageout'] = False
                            self.__env['jobDic'][k][1].result[0] = "running"
                        elif jobinfo["status"] == "stageout":
                            self.__env['stagein'] = False
                            self.__env['stageout'] = True
                            self.__env['jobDic'][k][1].result[0] = "running"
                            self.__env['stageoutStartTime'] = int(time.time())
                        else:
                            self.__env['stagein'] = False
                            self.__env['stageout'] = False
                            self.__env['jobDic'][k][1].result[0] = jobinfo["status"]
                        self.__env['jobDic'][k][1].result[1] = int(jobinfo["transecode"]) # transExitCode
                        self.__env['jobDic'][k][1].result[2] = int(jobinfo["pilotecode"]) # pilotExitCode
                        self.__env['jobDic'][k][1].timeStageIn = jobinfo["timeStageIn"]
                        self.__env['jobDic'][k][1].timeStageOut = jobinfo["timeStageOut"]
                        self.__env['jobDic'][k][1].timeSetup = jobinfo["timeSetup"]
                        self.__env['jobDic'][k][1].timeExe = jobinfo["timeExe"]
                        self.__env['jobDic'][k][1].cpuConsumptionTime = jobinfo["cpuTime"]
                        self.__env['jobDic'][k][1].cpuConsumptionUnit = jobinfo["cpuUnit"]
                        self.__env['jobDic'][k][1].cpuConversionFactor = jobinfo["cpuConversionFactor"]
                        self.__env['jobDic'][k][1].jobState = jobinfo["jobState"]
                        self.__env['jobDic'][k][1].vmPeakMax = int(jobinfo["vmPeakMax"])
                        self.__env['jobDic'][k][1].vmPeakMean = int(jobinfo["vmPeakMean"])
                        self.__env['jobDic'][k][1].RSSMean = int(jobinfo["RSSMean"])
                        self.__env['jobDic'][k][1].JEM = jobinfo["JEM"]
                        self.__env['jobDic'][k][1].cmtconfig = jobinfo["cmtconfig"]

                        try:
                            self.__env['jobDic'][k][1].pgrp = int(jobinfo["pgrp"])
                        except:
                            pUtil.tolog("!!WARNING!!2222!! Failed to convert pgrp value to int: %s" % (e))
                        else:
                            pUtil.tolog("Process groups: %d (pilot), %d (sub process)" % (os.getpgrp(), self.__env['jobDic'][k][1].pgrp))

                        tmp = self.__env['jobDic'][k][1].result[0]
                        if (tmp == "failed" or tmp == "holding" or tmp == "finished") and jobinfo.has_key("logfile"):
                            self.__env['jobDic'][k][1].logMsgFiles.append(jobinfo["logfile"])

                        if jobinfo.has_key("pilotErrorDiag"):
                            self.__env['jobDic'][k][1].pilotErrorDiag = pUtil.decode_string(jobinfo["pilotErrorDiag"])

                        if jobinfo.has_key("exeErrorDiag"):
                            self.__env['jobDic'][k][1].exeErrorDiag = pUtil.decode_string(jobinfo["exeErrorDiag"])

                        if jobinfo.has_key("exeErrorCode"):
                            self.__env['jobDic'][k][1].exeErrorCode = int(jobinfo["exeErrorCode"])

                        if jobinfo.has_key("filesWithFAX"):
                            self.__env['jobDic'][k][1].filesWithFAX = int(jobinfo["filesWithFAX"])
    
                        if jobinfo.has_key("filesWithoutFAX"):
                            self.__env['jobDic'][k][1].filesWithoutFAX = int(jobinfo["filesWithoutFAX"])

                        if jobinfo.has_key("bytesWithFAX"):
                            self.__env['jobDic'][k][1].bytesWithFAX = int(jobinfo["bytesWithFAX"])

                        if jobinfo.has_key("bytesWithoutFAX"):
                            self.__env['jobDic'][k][1].bytesWithoutFAX = int(jobinfo["bytesWithoutFAX"])

                        if jobinfo.has_key("filesAltStageOut"):
                            self.__env['jobDic'][k][1].filesAltStageOut = int(jobinfo["filesAltStageOut"])

                        if jobinfo.has_key("filesNormalStageOut"):
                            self.__env['jobDic'][k][1].filesNormalStageOut = int(jobinfo["filesNormalStageOut"])

                        if jobinfo.has_key("nEvents"):
                            try:
                                self.__env['jobDic'][k][1].nEvents = int(jobinfo["nEvents"])
                            except Exception, e:
                                pUtil.tolog("!!WARNING!!2999!! jobinfo did not return an int as expected: %s" % str(e))
                                self.__env['jobDic'][k][1].nEvents = 0
                        if jobinfo.has_key("nEventsW"):
                            try:
                                self.__env['jobDic'][k][1].nEventsW = int(jobinfo["nEventsW"])
                            except Exception, e:
                                pUtil.tolog("!!WARNING!!2999!! jobinfo did not return an int as expected: %s" % str(e))
                                self.__env['jobDic'][k][1].nEventsW = 0
    
                        if jobinfo.has_key("finalstate"):
                            self.__env['jobDic'][k][1].finalstate = jobinfo["finalstate"]
                        if jobinfo.has_key("spsetup"):
                            self.__env['jobDic'][k][1].spsetup = jobinfo["spsetup"]
                            # restore the = and ;-signs
                            self.__env['jobDic'][k][1].spsetup = self.__env['jobDic'][k][1].spsetup.replace("^", ";").replace("!", "=")
                            pUtil.tolog("Handler received special setup command: %s" % (self.__env['jobDic'][k][1].spsetup))

                        if jobinfo.has_key("output_latereg"):
                            pUtil.tolog("Got output_latereg=%s" % (jobinfo["output_latereg"]))
                            self.__env['jobDic'][k][1].output_latereg = jobinfo["output_latereg"]
    
                        if jobinfo.has_key("output_fields"):
                            self.__env['jobDic'][k][1].output_fields = pUtil.stringToFields(jobinfo["output_fields"])
                            pUtil.tolog("Got output_fields=%s" % str(self.__env['jobDic'][k][1].output_fields))
                            pUtil.tolog("Converted from output_fields=%s" % str(jobinfo["output_fields"]))

                        # hpc status
                        if jobinfo.has_key("mode"):
                            self.__env['jobDic'][k][1].mode = jobinfo['mode']
                        if jobinfo.has_key("hpcStatus"):
                            self.__env['jobDic'][k][1].hpcStatus = jobinfo['hpcStatus']
                        if jobinfo.has_key("refreshNow"):
                            self.__env['jobDic'][k][1].refreshNow = jobinfo['refreshNow']
                        if jobinfo.has_key("coreCount"):
                            self.__env['jobDic'][k][1].coreCount = jobinfo['coreCount']

                    except Exception, e:
                        pUtil.tolog("!!WARNING!!1998!! Caught exception. Pilot server down? %s" % str(e))
                        try:
                            pUtil.tolog("Received jobinfo: %s" % str(jobinfo))
                        except:
                            pass

        except Exception, e:
            pUtil.tolog("!!WARNING!!1998!! Caught exception. Pilot server down? %s" % str(e))
            
            
        # pUtil.tolog("---updateHandler : self.__env['jobDic'] is %s" % str(self.__env['jobDic']))
        self.request.send("OK")
