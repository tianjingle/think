from PIL import Image


filePath = "C:\\Users\\Administrator\\Desktop\\证件照.jpg"
newPath = "C:\\Users\\Administrator\\Desktop\\证件照1.jpg"

from PIL import Image


def blend_two_images():
    img1 = Image.open("C:\\Users\\Administrator\\Desktop\\me-removebg-preview-removebg-preview.png")
    img1 = Image.open("C:\\Users\\Administrator\\Desktop\\证件照1.jpg")
    img1 = Image.open("C:\\Users\\Administrator\\Desktop\\meng-removebg-preview.png")
    img1 = img1.resize((650,788))
    img1 = img1.convert('RGBA')
    transparence2white(img1)
    # img2 = Image.open("C:\\Users\\Administrator\\Desktop\\白底.png")
    # img2 = img2.resize((640, 930))
    # img2 = img2.convert('RGBA')
    #
    # img = Image.blend(img2, img1, 1)
    img1.show()
    img1.save("C:\\Users\\Administrator\\Desktop\\meng-removebg-preview-zhengjian.png")


def transparence2white(img):
    sp = img.size
    width = sp[0]
    height = sp[1]
    print(sp)
    for yh in range(height):
        for xw in range(width):
            dot = (xw, yh)
            color_d = img.getpixel(dot)  # 与cv2不同的是，这里需要用getpixel方法来获取维度数据
            if (color_d[3] == 0):
                color_d = (255, 255, 255, 255)
                img.putpixel(dot, color_d)  # 赋值的方法是通过putpixel
    return img


# img = Image.open('input.png')
# img = transparence2white(img)
# img.show()  # 显示图片


if __name__ == '__main__':
    blend_two_images()


