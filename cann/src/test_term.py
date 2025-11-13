import requests
from bs4 import BeautifulSoup
import openpyxl
import pandas as pd


def fetch_glossary(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        soup = BeautifulSoup(response.text, 'html.parser')
        glossary_items = []
        # print(soup)
        
        # 根据实际网页结构调整选择器
        items = soup.find_all('table')
        # print(items)
        
        for item in items:
             # 获取所有行
            rows = item.find_all('tr')

            # 遍历行并提取术语和含义
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    term = cols[0].text.strip()
                    desc = cols[1].text.strip()
                    # print(f"术语/缩略语: {term}\n含义: {desc}\n")
                    glossary_items.append({
                        'term': term,
                        'description': desc
                    })
        
        return glossary_items
    
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return []

if __name__ == "__main__":
    target_url = "https://www.hiascend.com/document/detail/zh/Glossary/gls/gls_0001.html"
    glossary = fetch_glossary(target_url)
    
    if glossary:
        print(f"共找到 {len(glossary)} 个术语:")
        # for idx, item in enumerate(glossary, 1):
        #     print(f"\n术语 {idx}: {item['term']}")
        #     print(f"描述: {item['description']}")
        df = pd.DataFrame(glossary)
        df.to_excel('../data/cann_terms.xlsx', index=False, engine='openpyxl')
    else:
        print("未找到术语表")