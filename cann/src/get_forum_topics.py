import time
import pandas as pd
import requests
from bs4 import BeautifulSoup


headers = {
    'Referer': 'https://www.hiascend.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def fetch_forum_topics(section_id, page_index=1, page_size=100):
    base_url = 'https://www.hiascend.com/ascendgateway/ascendservice/devCenter/bbs/servlet/get-topic-list'

    params = {
        'sectionId': section_id,
        'filterCondition': '1',
        'pageIndex': str(page_index),
        'pageSize': str(page_size)
    }

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None


def fetch_topic_detail(topic_id):
    detail_url = 'https://www.hiascend.com/ascendgateway/ascendservice/devCenter/bbs/servlet/get-topic-detail'

    params = {'topicId': topic_id}

    try:
        response = requests.get(detail_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('data', {}).get('result', {}).get('content', '')
    except Exception as e:
        print(f"获取详情失败 [{topic_id}]: {e}")
        return ''


def export_to_excel(data):
    df = pd.DataFrame(data)

    def clean_html(html):
        if pd.isna(html) or not html:
            return ''
        # 改用内置的html.parser
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text

    df['content'] = df['content'].apply(clean_html)

    df.to_excel('../data/cann_forum_topics.xlsx', index=False,
                columns=['id', 'source', 'title', 'url', 'content'],
                header=['id', 'source', 'title', 'url', 'body'])
    print(f"成功导出 {len(df)} 条数据到 cann_forum_topics.xlsx")


if __name__ == '__main__':
    all_data = []
    page_size = 100  # 每页数量与函数默认值保持一致
    section_ids = ['0106101385921175004', '0163125572293226003']

    for section_id in section_ids:
        first_page = fetch_forum_topics(section_id, page_index=1)
        if not first_page or first_page.status_code != 200:
            print("获取第一页数据失败")
            exit()

        data = first_page.json()['data']
        total_count = data['totalCount']
        total_pages = (total_count + page_size - 1) // page_size  # 计算总页数

        print(f"总数据量: {total_count} 条，共 {total_pages} 页")

        # 处理第一页数据
        for topic in data['resultList']:
            if topic['solved'] == 1:
                continue
            topic_id = topic['topicId']
            content = fetch_topic_detail(topic_id)
            all_data.append({
                'id': topic_id,
                'title': topic['title'],
                'url': f'https://www.hiascend.com/forum/thread-{topic_id}-1-1.html',
                'body': content,
                'created_at': topic['createTime'].strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'forum',
            })

        # 从第二页开始循环获取
        for page in range(2, total_pages + 1):
            print(f"正在获取第 {page}/{total_pages} 页...")
            response = fetch_forum_topics(section_id, page_index=page)

            if response and response.status_code == 200:
                page_data = response.json().get('data', {})
                for topic in page_data.get('resultList', []):
                    if topic['solved'] == 1:
                        continue
                    topic_id = topic['topicId']
                    content = fetch_topic_detail(topic_id)
                    all_data.append({
                        'id': topic_id,
                        'source': 'cann-forum',
                        'title': topic['title'],
                        'url': f'https://www.hiascend.com/forum/thread-{topic_id}-1-1.html',
                        'content': content
                    })
            else:
                print(f"第 {page} 页获取失败")

            time.sleep(1)  # 添加请求延迟防止封禁

    if all_data:
        export_to_excel(all_data)
    else:
        print("没有获取到有效数据")
