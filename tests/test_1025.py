import pandas as pd

s = "gLePr7XT5qDgr+p+ePYvXpO+s66lvX2LV1HKyeDrrRI="

if __name__ == '__main__':
    # df = pd.read_csv("/Users/mmt/Downloads/blockchair_ethereum_blocks_20180801.csv")
    count = 0
    all_count = 0
    all_gas_used = 0
    for i in range(1, 6):
        print("i", i)
        with open(f"/Users/mmt/Downloads/blockchair_ethereum_blocks_2018080{i}.csv") as f:
            lines = f.readlines()

        header = lines[0]
        data = lines[1:]

        ts = header.split(",")
        print(ts)
        all_count += len(data)
        for line in data:

            d = line.split(",")
            if d[7] in ["", "0", "0.0", None]:
                continue
            gas_used = int(d[7])
            all_gas_used += gas_used
    print("all_gas_used: ", all_gas_used)
