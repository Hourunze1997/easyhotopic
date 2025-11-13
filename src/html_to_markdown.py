import re
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

# Test with the provided HTML content
if __name__ == "__main__":
    html_content = '<p>参考这个帖子<br>\n<a href="https://discuss.openubmc.cn/t/topic/2142">新增自定义ipmi命令方法 - bmc_core SIG - openUBMC 论坛</a></p>'
    
    markdown_result = html_to_markdown(html_content)
    
    print("HTML Content:")
    print(html_content)
    print("\nMarkdown Result:")
    print(markdown_result)