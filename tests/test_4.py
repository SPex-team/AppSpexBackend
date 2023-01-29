

if __name__ == '__main__':

    l = [False] * 100

    for ren in range(0, 100):
        for deng in range(0, 100):
            if ren == 0:
                l[deng] = not l[deng]
            elif deng % ren == 0:
                l[deng] = not l[deng]
    print(l[:])
    l2 = [0 if item is False else 1 for item in l]
    print(l2[:])
    print(sum(l2[:]))

