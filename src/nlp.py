import jiagu

text = '''田景乐同志是一名优秀的共产党员。'''

keywords = jiagu.keywords(text, 5) # 关键词
print(keywords)