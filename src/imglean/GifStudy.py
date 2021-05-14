import imageio


def create_gif(image_list, gif_name, duration=0.35):
    frames = []
    for image_name in image_list:
        frames.append(imageio.imread(image_name))
    imageio.mimsave(gif_name, frames, 'GIF', duration=duration)
    return


def main():
    image_list = ["C:\\Users\\Administrator\\Desktop\\p1.jpg",
                  "C:\\Users\\Administrator\\Desktop\\p2.jpg",
                  "C:\\Users\\Administrator\\Desktop\\p3.jpg",
                  "C:\\Users\\Administrator\\Desktop\\p4.jpg",
                  "C:\\Users\\Administrator\\Desktop\\p6.jpg",
                  "C:\\Users\\Administrator\\Desktop\\p7.jpg",
                  "C:\\Users\\Administrator\\Desktop\\p8.jpg"]
    gif_name = 'cat.gif'
    duration = 0.5
    create_gif(image_list, gif_name, duration)


if __name__ == '__main__':
    main()