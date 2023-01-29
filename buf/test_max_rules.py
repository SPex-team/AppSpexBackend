
import yaml

group_map = {

}

for index in range(100000):
    group_id = index % 10
    group_name = f"group_{group_id}"
    if group_name not in group_map.keys():
        group_map[group_name] = []
    item = {
        "alert": str(index),
        "expr": f'operator_status{{id="{index}", project="ssv"}}=={index}',
        "for": "1m"
    }
    group_map[group_name].append(item)
    print("index: ", index)

# groups = {key: value for key, value in group_map.items()}
groups = [{"name": key, "rules": value} for key, value in group_map.items()]
data = {"groups": groups}
with open("/Users/mmt/Downloads/rules.yml", "w") as f:
    yaml.dump(data, f)
