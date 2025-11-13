import requests

url = 'https://hotopic-data.test.osinfra.cn/internal/v1/hot-topic/openubmc/to-review'

headers = {
    "Content-Type": "application/json"
}

payload = {
    "data": [
        {
            "summary": "BMC开发者如何实现Power资源的Redfish新标准适配",
            "discussion": [
                [
                    {
                        "id": 348,
                        "title": "【需求】Power相关资源支持redfish新标准",
                        "url": "https://gitcode.com/openUBMC/power_mgmt/issues/19",
                        "created_at": "2025-05-08T21:06:25+08:00",
                        "source_type": "issue",
                        "source_id": "3085661",
                        "source_closed": True,  # 注意：Python中使用布尔值 True/False
                        "cosine": 0.687,
                        "closed_cosine": 1.0
                    },
                    {
                        "id": 563,
                        "title": "【需求】Power资源支持redfish新标准",
                        "url": "https://gitcode.com/openUBMC/rackmount/issues/113",
                        "created_at": "2025-06-04T15:07:32+08:00",
                        "source_type": "issue",
                        "source_id": "3153434",
                        "source_closed": False,
                        "cosine": 0.0,
                        "closed_cosine": 0.896
                }
                ]
            ]
        },
        {
            "summary": "社区镜像中BMC工具QEMU与Bingo的一键部署配置",
            "discussion_count": 3,
            "discussion": [
                [
                    {
                        "id": 279,
                        "title": "社区镜像支持集成BMCStudio和Bingo工具",
                        "url": "https://gitcode.com/openUBMC/manifest/issues/13",
                        "created_at": "2025-04-28T19:31:33+08:00",
                        "source_type": "issue",
                        "source_id": "3070350",
                        "source_closed": True,
                        "cosine": 0.0,
                        "closed_cosine": 0.0
                    },
                    {
                        "id": 260,
                        "title": "支持Qemu工具和仿真镜像的本地一键部署",
                        "url": "https://gitcode.com/openUBMC/qemu/issues/2",
                        "created_at": "2025-04-27T17:49:10+08:00",
                        "source_type": "issue",
                        "source_id": "3067030",
                        "source_closed": True,
                        "cosine": 0.0,
                        "closed_cosine": 0.0
                    },
                    {
                        "id": 194,
                        "title": "支持Qemu工具和仿真镜像的本地一键部署",
                        "url": "https://gitcode.com/openUBMC/manifest/issues/9",
                        "created_at": "2025-04-16T16:00:03+08:00",
                        "source_type": "issue",
                        "source_id": "3055665",
                        "source_closed": True,
                        "cosine": 0.0,
                        "closed_cosine": 0.0
                    }
                ]
            ]
        }
    ]
}

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload  # 自动序列化为JSON并设置Content-Type
    )
    
    # 输出响应结果
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:\n{response.text}")
    
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")