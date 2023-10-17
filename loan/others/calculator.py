

def calculate_interest(principal, annual_rate, duration):
    rate_base = 1000000
    t = duration / (86400 * 365)
    n = 1

    return principal * (1 + annual_rate/1) ** (1 * t)


if __name__ == '__main__':
    r = calculate_interest(1e5, 0.05, 86400)
    print("r: ", r)
