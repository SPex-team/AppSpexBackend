import pandas as pd

s = "gLePr7XT5qDgr+p+ePYvXpO+s66lvX2LV1HKyeDrrRI="

if __name__ == '__main__':
    # df = pd.read_csv("/Users/mmt/Downloads/blockchair_ethereum_blocks_20180801.csv")
    count = 0
    all_count = 0
    for i in range(1, 6):
        print(i)
        with open(f"/Users/mmt/Downloads/blockchair_ethereum_blocks_2018080{i}.csv") as f:
            lines = f.readlines()

        print(len(lines))
        header = lines[0]
        data = lines[1:]

        ts = header.split(",")
        # print(ts)
        all_count += len(data)
        print(len(data))

        for line in data:
            if line in ["", "\n", None]:
                print("NNNNNNN")

            d = line.split(",")
            if d[7] in ["", "0", "0.0", None]:
                # print(d)
                count += 1


    print("count: ", all_count, count)
