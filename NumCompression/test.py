import numcom as nc

while True:
    a = int(input("value (int) > "))
    print("int    : %d" % a)
    print("numcom : %s" % nc.numcom(a))
    print("n -> i : %d" % int(nc.numcom(a)))
