import jieba as jieba
from stylecloud import gen_stylecloud


def gen_wd(file_path):
    myFile=open(file_path,"r",encoding="UTF-8")
    wds = jieba.cut(myFile.read().replace("的","").replace("了","").replace("一个","").replace("是","").replace("null","").replace("使用","").replace("rental","").replace("actor",""))
    result = ' '.join(wds)
    gen_stylecloud(text = result,font_path = 'C:\\Windows\\Fonts\\simhei.ttf',background_color = 'black',output_name = 'ok2.png',
                   icon_name='fas fa-question-circle',
            # 设置梯度方向
            gradient='horizontal',
)

if __name__ == "__main__":
    gen_wd("C:\\Users\\Administrator\\Downloads\\tianjingle.txt")
