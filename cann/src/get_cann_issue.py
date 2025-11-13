import requests
import json
from pathlib import Path


def fetch_issues():
    url = "https://beta.datastat.osinfra.cn/server/customization/cann/detail?"
    params = {
        "page": 1,
        "page_size": 20
    }

    body = {"community": "cann", "dim": [], "name": "", "page": 1, "page_size": 20,
            "filters": [{"column": "is_issue", "operator": "=", "value": "1"},
                        {"column": "created_at", "operator": ">", "value": "2025-05-30 00:00:00"}],
            "conditonsLogic": "AND", "order_field": "uuid", "order_dir": "ASC"}
    cookie = ""
    token = ""
    headers = {
        "Cookie": cookie,
        "token": token,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, params=params, headers=headers, json=body)
        response.raise_for_status()

        data = response.json()
        if data.get("code") != 1:
            raise Exception(f"API返回错误: {data.get('message', '未知错误')}")

        # 保存结果到当前目录
        save_path = Path(__file__).parent / "../data/cann_issues.json"
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data["data"], f, ensure_ascii=False, indent=2)

        print(f"成功获取{len(data['data'])}条数据，已保存至: {save_path}")
        return data["data"]

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {str(e)}")
    except Exception as e:
        print(f"处理数据时出错: {str(e)}")


if __name__ == "__main__":
    fetch_issues()
