import os
import ujson

OLD = "./w_avg_data"
NEW = "./extracted/asset_textavg"

count = 0
for file_name in os.listdir(OLD):
    new_list = os.listdir(NEW)
    if file_name in new_list:
        if os.path.getsize(os.path.join(OLD, file_name)) != os.path.getsize(os.path.join(NEW, file_name)):
            print(file_name)
            count += 1


print(count)
