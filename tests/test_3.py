

if __name__ == '__main__':

    l = [False] * 101

    for ren in range(1, 101):
        for deng in range(1, 101):
            if deng % ren == 0:
                l[deng] = not l[deng]
    print(l[1:])
    l2 = [0 if item is False else 1 for item in l]
    print(l2[1:])
    print(sum(l2[1:]))

