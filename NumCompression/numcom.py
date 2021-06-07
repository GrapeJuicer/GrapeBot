class numcom:
    def __init__(self, num) -> None:
        self.__numcomList = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.__numcomLength = len(self.__numcomList)

        if type(num) is str:
            if not self.__isNumcom(num):
                raise Exception("ValueError")
            self.__nvalue = num
            self.__SetInteger()
        else:
            self.__ivalue = int(num)
            self.__SetNumcom()
    
    def __repr__(self) -> str:
        return "<numcom nvalue:%s ivalue:%d>" % self.__nvalue, self.__ivalue

    def __str__(self) -> str:
        return "%s" % self.__nvalue

    def __int__(self) -> int:
        return self.__ivalue
    
    def __eq__(self, o: object) -> bool:
        return self.__ivalue == int(o)

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)
    
    def __lt__(self, o: object) -> bool:
        return self.__ivalue < int(o)

    def __le__(self, o: object) -> bool:
        return self.__eq__(o) or self.__lt__(o)

    def __gt__(self, o: object) -> bool:
        return not self.__le__(o)

    def __ge__(self, o: object) -> bool:
        return not self.__lt__(o)

    def __SetNumcom(self):
        if self.__ivalue == 0:
            self.__nvalue = self.__numcomList[0]
            return
        
        if self.__ivalue < 0:
            num = - self.__ivalue
            flg = True
        else:
            num = self.__ivalue
            flg = False
        
        reg = ""
        while num > 0:
            reg = self.__numcomList[num % self.__numcomLength] + reg
            num = num // self.__numcomLength
        
        self.__nvalue = reg if not flg else "-%s" % reg

    def __SetInteger(self):
        flg = True if self.__nvalue[0] == "-" else False

        num = 0
        for i, n in enumerate(reversed(self.__nvalue[1:] if flg else self.__nvalue)):
            num = num + self.__numcomList.index(n) * (self.__numcomLength ** i)

        self.__ivalue = num if not flg else -num
    
    def __isNumcom(self, num: str):
        if type(num) != str:
            return False
        for i in num:
            if not i in self.__numcomList:
                return False
        return True
