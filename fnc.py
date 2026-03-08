import pygame

def resize(img,x):
    size = round(img.get_width()*x),round(img.get_height()*x)
    return pygame.transform.scale(img,size)

def load_ig(path):
    path="./data/imgs/"+path
    p = pygame.image
    try:
        if path[-3:]=="png":
            return p.load(path).convert_alpha()
        else:
            return p.load(path).convert()
    except pygame.error:
        return p.load(path)


def bzw(a):
    return (a**2)**0.5

def rotate(win, image, corner, angle):
        rotated_img = pygame.transform.rotate(image, angle)
        new_box = rotated_img.get_rect(center=image.get_rect(topleft = corner).center)
        win.blit(rotated_img, new_box.topleft)