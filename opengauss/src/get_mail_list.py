import base64

import requests
import json
from openpyxl import Workbook
from datetime import datetime


def get_all_data():
    url = "https://beta.datastat.osinfra.cn/server/customization/opengauss/detail"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "",
        "token": ""
        }
    params = {
        "page": 1,
        "page_size": 100
    }
    body = {
        "community": "opengauss",
        "dim": [],
        "name": "fact_opengauss_email",
        "page": 1,
        "page_size": 100,
        "filters": [],
        "conditonsLogic": "AND",
        "order_field": "uuid",
        "order_dir": "ASC"
    }

    all_data = []

    while True:
        response = requests.post(url, params=params, json=body, headers=headers)

        if response.status_code == 200:
            result = response.json()

            if result["code"] == 1 and result["message"] == "success":
                all_data.extend(result["data"])

                # 检查是否还有更多数据
                if len(result["data"]) < params["page_size"]:
                    break

                # 更新页码，获取下一页数据
                params["page"] += 1
            else:
                print(f"Error: {result['message']}")
                break
        else:
            print(f"HTTP Error: {response.status_code}")
            break

    return {
        "code": 1,
        "message": "success",
        "data": all_data
    }


def is_safe_for_excel(value):
    try:
        # 尝试将值转换为JSON字符串，然后再解析回来
        # 这将过滤掉任何不能安全序列化的数据
        json.loads(json.dumps(value))
        return True
    except:
        return False


def safe_str(value):
    if isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return value[:32767]  # Excel单元格的最大长度
    elif is_safe_for_excel(value):
        return str(value)[:32767]
    else:
        return "[不支持的数据类型]"


def save_to_excel(data, filename):
    wb = Workbook()
    ws = wb.active
    ws.title = "OpenGauss Email Data"

    # 写入表头
    headers = list(data["data"][0].keys())
    ws.append(headers)

    # 写入数据
    for row in data["data"]:
        try:
            safe_row = [safe_str(row.get(header, "")) for header in headers]
            ws.append(safe_row)
        except Exception as e:
            print(f"跳过一行数据，因为: {str(e)}")
            continue

    try:
        wb.save(filename)
        print(f"数据已成功保存到 {filename}")
    except Exception as e:
        print(f"保存Excel文件时出错: {str(e)}")
        # 如果保存失败，尝试保存为CSV
        csv_filename = filename.rsplit('.', 1)[0] + '.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in data["data"]:
                safe_row = [safe_str(row.get(header, "")) for header in headers]
                writer.writerow(safe_row)
        print(f"数据已保存为CSV文件: {csv_filename}")


# 获取所有数据
result = get_all_data()
# 生成时间戳
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 保存为JSON
json_filename = f"../data/opengauss_email_data_{timestamp}.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 保存为Excel
excel_filename = f"../data/opengauss_email_data_{timestamp}.xlsx"
save_to_excel(result, excel_filename)

print(f"Total records retrieved: {len(result['data'])}")
print(f"Data has been saved to {json_filename} and {excel_filename}")