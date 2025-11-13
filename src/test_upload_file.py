import requests
import time

def upload_document(file_path, api_url="http://192.168.0.160:9621", api_key=None):
    """
    上传文档到LightRAG系统
      
    Args:
        file_path: 要上传的文件路径
        api_url: API服务器地址
        api_key: API密钥（如果需要认证）
      
    Returns:
        dict: 包含状态和跟踪ID的响应
    """
    url = f"{api_url}/documents/upload"
      
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
      
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files, headers=headers)
      
    return response.json()

def check_processing_status(track_id, api_url="http://192.168.0.160:9621", api_key=None):
    """检查文档处理状态"""
    url = f"{api_url}/track_status/{track_id}"
      
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
      
    response = requests.get(url, headers=headers)
    return response.json()

def upload_all_documents_from_file(file_list_path="filtered_rag_files.txt", api_url="http://192.168.0.160:9621", api_key=None):
    """
    从文件列表中读取所有文件路径并上传
    
    Args:
        file_list_path: 包含文件路径列表的文本文件路径
        api_url: API服务器地址
        api_key: API密钥（如果需要认证）
    """
    uploaded_documents = []
    
    with open(file_list_path, 'r', encoding='utf-8') as f:
        file_paths = [line.strip() for line in f.readlines() if line.strip()]
    
    print(f"找到 {len(file_paths)} 个文件需要上传")
    
    for i, file_path in enumerate(file_paths, 1):
        if i < 132:
            continue
        print(f"正在上传 ({i}/{len(file_paths)}): {file_path}")
        try:
            result = upload_document(file_path, api_url, api_key)
            if result.get("status") == "success":
                track_id = result.get("track_id")
                print(f"  上传成功, 跟踪ID: {track_id}")
                uploaded_documents.append({
                    "file_path": file_path,
                    "track_id": track_id,
                    "status": "success"
                })
                
                # 可选：检查处理状态
                # print(f"  检查处理状态...")
                # status_result = check_processing_status(track_id, api_url, api_key)
                # print(f"  处理状态: {status_result}")
            else:
                print(f"  上传失败: {result}")
                uploaded_documents.append({
                    "file_path": file_path,
                    "error": result,
                    "status": "failed"
                })
        except Exception as e:
            print(f"  上传出错: {str(e)}")
            uploaded_documents.append({
                "file_path": file_path,
                "error": str(e),
                "status": "error"
            })
        
        # 添加小延迟避免请求过于频繁
        time.sleep(0.1)
    
    # 打印汇总信息
    success_count = sum(1 for doc in uploaded_documents if doc["status"] == "success")
    failed_count = sum(1 for doc in uploaded_documents if doc["status"] == "failed")
    error_count = sum(1 for doc in uploaded_documents if doc["status"] == "error")
    
    print(f"\n上传完成汇总:")
    print(f"  成功: {success_count}")
    print(f"  失败: {failed_count}")
    print(f"  错误: {error_count}")
    print(f"  总计: {len(uploaded_documents)}")
    
    return uploaded_documents

# 使用示例
if __name__ == "__main__":
    # 上传所有文档
    results = upload_all_documents_from_file(api_key="your-api-key")
    
    # 如果需要检查处理状态，可以取消下面的注释
    # for doc in results:
    #     if doc["status"] == "success":
    #         print(f"检查 {doc['file_path']} 的处理状态...")
    #         status_result = check_processing_status(doc["track_id"], api_key="your-api-key")
    #         print(f"  状态: {status_result}")
