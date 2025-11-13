import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import re
import json
import html

def html_to_markdown(html_content):
    """
    Convert simple HTML content to Markdown format.
    Preserves links and basic formatting.
    
    Args:
        html_content (str): HTML string to convert
        
    Returns:
        str: Markdown formatted string
    """
    # Unescape HTML entities
    content = html.unescape(html_content)
    # Remove paragraph tags
    content = re.sub(r'<p>|</p>', '', content)
    # Convert <br> tags to newlines
    content = re.sub(r'<br\s*/?>', '\n', content)
    # Convert anchor tags to Markdown links
    # Pattern: <a href="url">text</a>
    content = re.sub(r'<a\s+href=["\']([^"\']+)["\']\s*>([^<]+)</a>', r'[\2](\1)', content)
    
    return content.strip()

def fetch_one_page_data(page):
    """获取单页论坛数据"""
    params = {
        'page': page,
        'no_definitions': True,
    }

    response = requests.get(
        'https://discuss.openubmc.cn/latest.json',
        params=params,
        timeout=10
    )
    response.raise_for_status()
    return response.json()

def extract_posts_data(posts_data):
    """提取帖子数据"""
    posts = []
    for post in posts_data:
        user_name = post['name']
        topic_closed = post['topic_accepted_answer']
        is_solution = post['accepted_answer']
        body_cooked = post['cooked']
        soup = BeautifulSoup(body_cooked, 'html.parser')
        # Extract text content
        text_content = soup.get_text()
        text_content = re.sub(r'\n{3,}', '\n\n', text_content)
        # Strip leading/trailing whitespace
        text_content = text_content.strip()
        # Extract all links
        links = []
        for link in soup.find_all('a', href=True):
            links.append(link['href'])
        
        if links:
            text = f'content: {text_content}\nlinks: {", ".join(links)}'
        else:
            text = text_content
        # print(f"Extracted text: {text}")
        post_url = post['post_url']
        posts.append({
            'user_name': user_name,
            'topic_closed': topic_closed,
            'is_solution': is_solution,
            'post_url': post_url,
            'text': text,
        })
    return posts

def get_one_topic_content(topic):
    """获取单条话题内容"""
    topic_id = topic['id']
    topic_title = topic['title']
    topic_url = f'https://discuss.openubmc.cn/t/{topic_id}'
    # Create a safer filename by replacing special characters
    safe_title = re.sub(r'[^\w\s-]', '', topic_title).strip()
    safe_title = re.sub(r'[-\s]+', '_', safe_title)  # Replace spaces and hyphens with underscores
    file_name = f'{safe_title}_{topic_id}.json'
    params = {
        'track_visit': True,
        'forceLoad': True,
    }
    try:
        response = requests.get(
            f'https://discuss.openubmc.cn/t/{topic_id}.json',
            params=params,
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"获取话题内容失败（话题ID {topic_id}）: {e}")

    post_json_data = response.json()
    question =  ''
    best_answer_url = ''
    topic_user_name = ''
    if post_json_data.get('post_stream'):
        post_data = post_json_data['post_stream']['posts']
        posts = extract_posts_data(post_data)
        question = f'{topic_title} - {posts[0]["text"]}' if posts else ''
        topic_user_name = posts[0]['user_name']
        repy_posts = posts[1:] if len(posts) > 1 else []
        for post in repy_posts:
            if post['is_solution']:
                best_answer_url = post['post_url']
                break

        # print(f"提取到 {len(posts)} 条帖子数据")
        # first_post = post_data[0]

    write_data = {
        'topic_id': topic_id,
        'question': question,
        'topic_user_name': topic_user_name,
        'best_answer_url': best_answer_url,
        'reply_posts': repy_posts,
    }
    
    # Ensure the directory exists
    import os
    rag_dir = '/home/workspace/easyhotopic/openumbc/data/rag'
    if not os.path.exists(rag_dir):
        os.makedirs(rag_dir)
    
    with open(f'{rag_dir}/{file_name}', 'w', encoding='utf-8') as f:
        json.dump(write_data, f, ensure_ascii=False, indent=4)

    return write_data

def extract_one_page_topic_data(page):
    """提取单页论坛话题数据"""
    data = fetch_one_page_data(page)
    topics = data.get('topic_list', {}).get('topics', [])
    # print(f"topics length: {len(topics)}, topics: {topics[0]}")
    for topic in topics:
        get_one_topic_content(topic)
    # topic_content = get_one_topic_content(topics[0])
    # print(f"topic_content: {topic_content}")
    return topics


if __name__ == '__main__':
    page = 0
    while True:
        try:
            topics = extract_one_page_topic_data(page)
            page += 1
            if not topics:
                print("No more topics found.")
                break
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            break
        print(f"Extracted {len(topics)} topics from page {page}.")
