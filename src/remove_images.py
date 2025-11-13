import re

def remove_image_content(text):
    """
    Remove image-related content from text.
    
    Removes content within <div class="lightbox-wrapper">...</div> blocks
    and other image-related HTML tags.
    
    Args:
        text (str): Input text containing image content
        
    Returns:
        str: Text with image content removed
    """
    # Remove div blocks with class="lightbox-wrapper" and everything inside them
    # This pattern matches <div class="lightbox-wrapper">...</div> blocks
    text = re.sub(r'<div class="lightbox-wrapper">.*?</div>', '', text, flags=re.DOTALL)
    
    # Also remove any remaining img tags
    text = re.sub(r'<img[^>]*>', '', text)
    
    # Remove any empty lines that might have been left behind
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Strip leading/trailing whitespace
    return text.strip()

# Test with the provided content
if __name__ == "__main__":
    sample_text = '''简要概述

1.在组件ipmi.json中定义新增命令

2.自动生成代码

3.上板调试
<ol>
<li></li>
</ol>
<div class="lightbox-wrapper"><a class="lightbox" href="https://discuss.openubmc.cn/uploads/default/original/2X/6/6e7a7077a40062b6ffa62af7b7d3cd8f36735f96.png" data-download-href="https://discuss.openubmc.cn/uploads/default/6e7a7077a40062b6ffa62af7b7d3cd8f36735f96" title="image"><img src="https://discuss.openubmc.cn/uploads/default/optimized/2X/6/6e7a7077a40062b6ffa62af7b7d3cd8f36735f96_2_690x254.png" alt="image" data-base62-sha1="fLkQv4RyJXx4KUwzz2wphHBPfWS" width="690" height="254" srcset="https://discuss.openubmc.cn/uploads/default/optimized/2X/6/6e7a7077a40062b6ffa62af7b7d3cd8f36735f96_2_690x254.png, https://discuss.openubmc.cn/uploads/default/optimized/2X/6/6e7a7077a40062b6ffa62af7b7d3cd8f36735f96_2_1035x381.png 1.5x, https://discuss.openubmc.cn/uploads/default/optimized/2X/6/6e7a7077a40062b6ffa62af7b7d3cd8f36735f96_2_1380x508.png 2x" data-dominant-color="232323"><div class="meta"><svg class="fa d-icon d-icon-far-image svg-icon" aria-hidden="true"><use href="#far-image"></use></svg><span class="filename">image</span><span class="informations">1604×592 58.3 KB</span><svg class="fa d-icon d-icon-discourse-expand svg-icon" aria-hidden="true"><use href="#discourse-expand"></use></svg></div></a></div>

在ipmi.json新增ipmi命令定义，确保通过netfn+cmd+req拼接成的ipmi命令唯一，如果无法确保唯一，请联系对应项目支持人员

2.自动生成代码

<div class="lightbox-wrapper"><a class="lightbox" href="https://discuss.openubmc.cn/uploads/default/original/2X/a/aa033960173d8199c8311c12d12fd9d821661797.png" data-download-href="https://discuss.openubmc.cn/uploads/default/aa033960173d8199c8311c12d12fd9d821661797" title="image"><img src="https://discuss.openubmc.cn/uploads/default/original/2X/a/aa033960173d8199c8311c12d12fd9d821661797.png" alt="image" data-base62-sha1="og04OoF2OYca6GP6pWGaD2tqewv" width="690" height="319" data-dominant-color="242729"><div class="meta"><svg class="fa d-icon d-icon-far-image svg-icon" aria-hidden="true"><use href="#far-image"></use></svg><span class="filename">image</span><span class="informations">986×457 35.7 KB</span><svg class="fa d-icon d-icon-discourse-expand svg-icon" aria-hidden="true"><use href="#discourse-expand"></use></svg></div></a></div>

2.1 直接执行bingo gen后

<div class="lightbox-wrapper"><a class="lightbox" href="https://discuss.openubmc.cn/uploads/default/original/2X/e/e4c685395edd05a432a9c64808a1b89693274118.png" data-download-href="https://discuss.openubmc.cn/uploads/default/e4c685395edd05a432a9c64808a1b89693274118" title="image"><img src="https://discuss.openubmc.cn/uploads/default/original/2X/e/e4c685395edd05a432a9c64808a1b89693274118.png" alt="image" data-base62-sha1="wDQbRfu5ZtjTmkz5j4QqKc70Ubu" width="690" height="214" data-dominant-color="252A2D"><div class="meta"><svg class="fa d-icon d-icon-far-image svg-icon" aria-hidden="true"><use href="#far-image"></use></svg><span class="filename">image</span><span class="informations">873×271 27.3 KB</span><svg class="fa d-icon d-icon-discourse-expand svg-icon" aria-hidden="true"><use href="#discourse-expand"></use></svg></div></a></div>

2.2 保留本次自动生成和ipmi有关的代码

2.3 实现本次新增ipmi命令的接口

在fructrl的pwr_powerctrl_ipmi.lua的register_ipmi函数中注册新回调
<div class="lightbox-wrapper"><a class="lightbox" href="https://discuss.openubmc.cn/uploads/default/original/2X/0/0aa159e7b53a5f6b14de07de6641007a9f1e9ff2.png" data-download-href="https://discuss.openubmc.cn/uploads/default/0aa159e7b53a5f6b14de07de6641007a9f1e9ff2" title="image"><img src="https://discuss.openubmc.cn/uploads/default/optimized/2X/0/0aa159e7b53a5f6b14de07de6641007a9f1e9ff2_2_690x133.png" alt="image" data-base62-sha1="1w2t18IERTrBYMikmrSdOT1nLYS" width="690" height="133" srcset="https://discuss.openubmc.cn/uploads/default/optimized/2X/0/0aa159e7b53a5f6b14de07de6641007a9f1e9ff2_2_690x133.png, https://discuss.openubmc.cn/uploads/default/optimized/2X/0/0aa159e7b53a5f6b14de07de6641007a9f1e9ff2_2_1035x199.png 1.5x, https://discuss.openubmc.cn/uploads/default/original/2X/0/0aa159e7b53a5f6b14de07de6641007a9f1e9ff2.png 2x" data-dominant-color="282828"><div class="meta"><svg class="fa d-icon d-icon-far-image svg-icon" aria-hidden="true"><use href="#far-image"></use></svg><span class="filename">image</span><span class="informations">1227×238 29 KB</span><svg class="fa d-icon d-icon-discourse-expand svg-icon" aria-hidden="true"><use href="#discourse-expand"></use></svg></div></a></div>

3. 升级环境后，先通过busctl --user tree bmc.kepler.fructrl 查看是否新增了自定义的ipmi命令

确认新增后，即可通过ipmi命令发送请求
如以上步骤执行后仍无法新增自定义ipmi命令，请联系对应项目技术支持人员'''

    cleaned_text = remove_image_content(sample_text)
    
    print("Original text:")
    print(sample_text)
    print("\n" + "="*50 + "\n")
    print("Cleaned text:")
    print(cleaned_text)