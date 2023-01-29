

if __name__ == '__main__':
    l = [False, True] * 50

    for i in range(2, 100):
        for index in range(100):
            if index % i == 0:
                l[index] = not l[index]
    l2 = [0 if item is False else 1 for item in l]
    print(l2)
    print(sum(l2))

