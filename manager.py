import enum
from lib_logger.main import launch_logger
import multiprocessing as mp
import threading as th
import sys
# import signal
from time import sleep

from lib_vcstatus.main import launch_vcstatus
from lib_logger.main import launch_logger
import processflag.pflag as pf

# set process launchers
libs = [
    launch_vcstatus, # voice chat status
    launch_logger,
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
    if isActiveProcess[index].value == pf.INACTIVE or not prcs[i].is_alive():  # if the process is stopped
        print("{0}: {1}".format(infoToFuncName(libs[index]), "Inactive"))
    elif isActiveProcess[index].value == pf.LAUNCHING:
        print("{0}: {1}".format(infoToFuncName(libs[index]), "Launching"))
    elif isActiveProcess[index].value == pf.ACTIVE:
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


def stopAll() -> None:
    for i in range(len(prcs)):
        stopOne(i)


def stopOne(index: int) -> None:
    if isActiveProcess[index].value != pf.INACTIVE:
        prcs[index].kill()
        isActiveProcess[index].value = pf.INACTIVE


# main
if __name__ == "__main__":
    # get token
    with open("token.txt", "r") as f:
        token = f.read()

    # create list of lib name
    plist = [infoToFuncName(f) for f in libs]
    
    # create thread
    th_pcheck: th.Thread = th.Thread(target=checkAlive)
    th_pcheck.daemon = True

    # launch all processes
    launchAll(token)

    # start thread
    th_pcheck.start()

    while True:
        try:
            buf = input("grapebot.console > ").split()
        except:
            print("\nExiting processes...")
            sys.exit(1)

        if buf[0] == "help":
            print("Commands:")
            print("  help                      Display this information.")
            print("  list                      Display the list of services.")
            print("  status [name...]          Display service's status. If no argument is given, all services will be displayed.")
            print("  launch [name...]          Launch services. If no argument is given, all services will be launched.")
            print("  stop [name...]            Stop services. If no argument is given, all services will be stopped.")
            print("  exit                      Exit program.")
        elif buf[0] == "list":
            for n in plist:
                print(n, end="\t")
            print("")
        elif buf[0] == "status":
            if len(buf) == 1:
                # show all process status
                for i in range(len(prcs)):
                    showStatus(i)
            else:
                for bf in buf[1:]: # loop by buf
                    try:
                        showStatus(plist.index(bf))
                    except:
                        print("Error: lib.{0} is not exist.".format(bf))
        elif buf[0] == "launch":
            if len(buf) == 1:
                launchAll(token)
                print("All processes have been launched.")
            else:
                for bf in buf[1:]:
                    try:
                        launchOne(token, plist.index(bf))
                        print("Process {0} has been launched.".format(bf))
                    except:
                        print("Error: lib.{0} is not exist.".format(bf))
        elif buf[0] == "stop":
            if len(buf) == 1:
                stopAll()
                print("All processes have been stopped successfully.")
            else:
                for bf in buf[1:]:
                    try:
                        stopOne(plist.index(bf))
                        print("Process {0} has been stopped successfully.".format(bf))
                    except:
                        print("Error: lib.{0} is not exist.".format(bf))
                    
                    # another way
                    # filtered processes
                    # fps = list(filter(lambda x: infoToFuncName(x) == bf, prcs))
                    # if fps: # if list is not empty
                    #     fps[0].terminate()
                    #     print("Process {0} has stopped successfully.".format(bf))
                    # else:
                    #     print("Error: lib.{0} is not exist.".format(bf))
        elif buf[0] == "exit":
            print("Exiting processes...")
            sys.exit(0)
        else:
            print("Error: Unknown command.")
