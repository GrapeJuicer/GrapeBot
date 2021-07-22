import enum
import multiprocessing as mp
import sys
# import signal
from time import sleep

from lib_vcstatus.main import launch_vcstatus

# set process launchers
libs = [
    launch_vcstatus, # voice chat status
]

# create array
isActiveProcess = [mp.Value('i', 0) for i in range(len(libs))]
    
# set process array
prcs = [None] * len(libs)


def createProcess(token: str, flag: mp.Value, func) -> mp.Process:
    return mp.Process(target=func, args=(token, flag,))

def infoToFuncName(cls) -> str:
    return str(cls)[17:str(cls).find(" at ")] # launch_も取り除く

def showStatus(index: int):
    if isActiveProcess[index].value == 0 or not prcs[i].is_alive():  # if the process is stopped
        print("{0}: {1}".format(infoToFuncName(libs[index]), "Inactive"))
    elif isActiveProcess[index].value == 1:
        print("{0}: {1}".format(infoToFuncName(libs[index]), "Launching"))
    elif isActiveProcess[index].value == 2:
        print("{0}: {1}".format(infoToFuncName(libs[index]), "Active"))
    else:
        print("{0}: {1}".format(infoToFuncName(libs[index]), "Error (invalid process flag value)"))


def checkAlive():
    while True:
        for i in range(len(prcs)):
            if not prcs[i].is_alive():
                isActiveProcess[i].value = 0
        sleep(5)



def launchAll(token: str) -> None:
    for i in range(len(prcs)):
        launchOne(token, i)


def launchOne(token: str, index: int) -> None:
    if isActiveProcess[index].value == 0:
        # create process instance
        prcs[index] = createProcess(token, isActiveProcess[index], libs[index])
        # set daemon - Exit with the parent process when it exits
        prcs[index].daemon = True
        # launch process
        prcs[index].start()


    # get token
    with open("token.txt", "r") as f:
        token = f.read()

    while True:
        if firstFlg:
            print("Process Status ({0}) ----------------------------".format(time()))
        else:
            print("\033[{0}A\rProcess Status ({1}) ----------------------------".format((len(libs) + 1), time()))
        for i in range(len(prcs)):
            if isActiveProcess[i].value == 0 or not prcs[i].is_alive():  # プロセス停止中の時`
                print("\t{0:20}\t{1:50}".format(infoToFuncName(libs[i]), "INACTIVE"))
                isActiveProcess[i].value = 0
                # create process instance
                prcs[i] = createProcess(token, isActiveProcess[i], libs[i])
                # set daemon - 親プロセスが終了する時に一緒に消える
                prcs[i].daemon = True
                # launch process
                prcs[i].start()
            elif isActiveProcess[i].value == 1:
                print("\t{0:20}\t{1:50}".format(infoToFuncName(libs[i]), "LAUNCHING"))
            elif isActiveProcess[i].value == 2:
                print("\t{0:20}\t{1:50}".format(infoToFuncName(libs[i]), "ACTIVE"))
            else:
                print("\t{0:20}\t{1:50}".format(infoToFuncName(libs[i]), "ERROR (invalid process flag value)"))
        
        if firstFlg:
            firstFlg = False

        sleep(5)
