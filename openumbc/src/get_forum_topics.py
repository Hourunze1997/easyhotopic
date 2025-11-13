import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup


def fetch_forum_data():
    # 设置时间范围（注意：2024年12月2日尚未到来，这里按用户输入处理）
    start_date = datetime(2024, 12, 2)
    end_date = datetime.now()

    all_topics = []
    page = 1
    per_page = 30  # 根据API性能调整

    while True:
        # 请求API
        params = {
            'page': page,
            'no_definitions': True,
        }

        try:
            response = requests.get(
                'https://discuss.openubmc.cn/latest.json?no_definitions=true',
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            topics = data.get('topic_list',{}).get('topics', [])
            # 过滤时间范围内的数据
            for topic in topics:
                created_at = datetime.strptime(topic['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                if topic ['category_id'] == 40:
                    continue
                if start_date <= created_at <= end_date:
                    topic_id = topic['id']
                    body = ""
                    url = ""
                    try:
                        post_response = requests.get(
                            f'https://discuss.openubmc.cn/t/{topic_id}.json?track_visit=true&forceLoad=true',
                            timeout=10
                        )
                        post_response.raise_for_status()
                        post_data = post_response.json()
                        if post_data.get('post_stream'):
                            first_post = post_data['post_stream']['posts'][0]
                            # 新增HTML清洗逻辑
                            html_content = first_post.get('cooked', "")
                            post_url = first_post.get('post_url', "")
                            url = f'https://discuss.openubmc.cn/{post_url}'
                            soup = BeautifulSoup(html_content, 'html.parser')
                            body = soup.get_text(separator=' ', strip=True)
                    except Exception as e:
                        print(f"获取帖子正文失败（话题ID {topic_id}）: {e}")

                    all_topics.append({
                        'id': topic['id'],
                        'title': topic['title'],
                        'author': topic.get('author', {}).get('username', ''),
                        'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'views': topic['views'],
                        'reply_count': topic['reply_count'],
                        'body': body,
                        'url': url,
                        'type': 'forum',

                    })
                elif created_at < start_date:
                    return all_topics

            # 判断是否还有下一页
            if len(topics) < per_page:
                break

            page += 1

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            break

    return all_topics


def save_to_excel(data):
    df = pd.DataFrame(data)
    df.to_excel('../data/forum_topics.xlsx', index=False)


if __name__ == '__main__':
    forum_data = fetch_forum_data()
    if forum_data:
        save_to_excel(forum_data)
        print(f"成功保存{len(forum_data)}条数据到 forum_topics.xlsx")
    else:
        print("没有获取到符合条件的数据")
