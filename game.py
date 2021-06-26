import pygame, sys, os, random, ctypes
import data.engine as e
from pygame.locals import *
from PIL import Image, ImageDraw

pygame.init()
pygame.font.init()
pygame.mixer.pre_init(44100, -16, 2, 512)

# LOADING STUFFS #

stone = pygame.image.load('data/images/blocks/stone.png')
bg_stone_dark = pygame.image.load('data/images/background/stone_dark.png')

fall_off_sound = pygame.mixer.Sound('data/audios/fall_off.wav')
jump_sound = pygame.mixer.Sound('data/audios/jump.wav')
stone_walk_sounds = [pygame.mixer.Sound('data/audios/stone_walk1.wav'),pygame.mixer.Sound('data/audios/stone_walk2.wav')]
stone_walk_sounds[0].set_volume(0.2)
stone_walk_sounds[1].set_volume(0.2)
fall_off_sound.set_volume(0.3)
pygame.mixer.music.load('data/audios/music.wav')
pygame.mixer.music.set_volume(0)
pygame.mixer.music.play(-1)

####################

# MAIN DEFİNİTİONS #

clock = pygame.time.Clock()
if os.name == 'nt':
    user32 = ctypes.windll.user32
    real_resolution = (user32.GetSystemMetrics(0),user32.GetSystemMetrics(1))
elif os.name == "posix":
    try:
        reslist = os.popen("xdpyinfo | awk '/dimensions/{print $2}'").read().strip("\n").split("x")
        real_resolution = (int(reslist[0]),int(reslist[1]))
    except Exception as err:
        print(f"Unexcepted error catched {err} on real_resolution. ")
        real_resolution = (1920,1090)
else:
    os.exit("Unsupported os!",os.name)
        
FPS = 90
window_width = 600
window_height = 400
WINDOW_SIZE = (window_width,window_height)
TILE_SIZE = stone.get_width()
window = pygame.display.set_mode(WINDOW_SIZE,0,32)
display = pygame.Surface((window_width/2,window_height/2))
pygame.display.set_caption('GameDev')
background_object = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[-20,40,40,400]],[0.5,[70,90,100,400]],[0.5,[250,80,120,400]],[0.5,[400,50,140,400]]]

e.load_animations('data/images/entities/')
e.load_animations('data/images/objects/')

stone_walk_sound_timer = 0
scroll_share = 6

background_image = Image.open("data/images/background/stone_dark.png")
draw = ImageDraw.Draw(background_image)

mode = background_image.mode
size = background_image.size
data = background_image.tobytes()

this_image = pygame.image.fromstring(data, size, mode)
this_image = pygame.transform.scale(this_image,(this_image.get_width()*2,this_image.get_height()*2))

block_amount_of_screen_x = (int((WINDOW_SIZE[0]) / bg_stone_dark.get_width())) + scroll_share
block_amount_of_screen_y = (int((WINDOW_SIZE[1]) / bg_stone_dark.get_height())) + scroll_share

 #print(block_amount_of_screen_x,block_amount_of_screen_y)

image1 = Image.open("data/images/background/stone_dark.png")

image1_size = (bg_stone_dark.get_width(),bg_stone_dark.get_height())

new_image = Image.new('RGB',(image1_size[0] * block_amount_of_screen_x, image1_size[0] * block_amount_of_screen_y), (250,250,250))

try:
    b = 0
    for y in range(block_amount_of_screen_y):
        a = 0
        for x in range(block_amount_of_screen_x):

            new_image.paste(image1,(a,b))
            new_image.save("data/images/background/merged_image.jpg","JPEG")
            a += 16

        b += 16

except PermissionError as error:
    #print("PERMISSION ERROR OCCURRED")
    python = sys.executable
    os.execl(python, python, * sys.argv)



background_image = pygame.image.load("data/images/background/merged_image.jpg")

#####################

# FUNCTIONS #

def circle_surf(radius, color):

    surf = pygame.Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0,0,0))

    return surf

def load_item_bar():

    image_name = "selected_"
    n = 0
    image_list = []

    while True:

        try:
            image_path = "assets/item_bar/"+image_name+str(n)+".png"
            image = pygame.image.load(image_path)
            image_list.append(image)
            print(image)
            n += 1

        except FileNotFoundError as error:
            break

    return image_list


def load_map(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

def save_edited_map():

    saved_map = open("data/levels/saved_map.txt","w")

    for row in game_map:

        for tile in row:

            saved_map.write(tile)
            #print(tile, end='')

        #print()
        saved_map.write('\n')

def move_particle(rects, tiles):
    collision_types_of_particles = {'top': False, 'bottom': False, 'right': False, 'left': False}

    
    for momentum in momentum_list:
        for rect in rects:    
            rect.x += momentum[0]
            hit_list = collision_test(rect, tiles)
            for tile in hit_list:
                if momentum[0] > 0:
                    rect.right = tile.left
                    collision_types_of_particles['right'] = True
                elif momentum[0] < 0:
                    rect.left = tile.right
                    collision_types_of_particles['left'] = True

    for momentum in momentum_list:
        for rect in rects:
            rect.y += momentum[1]
            hit_list = collision_test(rect, tiles)
            for tile in hit_list:
                if momentum[1] > 0:
                    rect.bottom = tile.top
                    collision_types_of_particles['bottom'] = True
                elif momentum[1] < 0:
                    rect.top = tile.bottom
                    collision_types_of_particles['top'] = True

    return rects, collision_types_of_particles

def restart_game():
    python = sys.executable
    os.execl(python, python, * sys.argv)


def remove_block(block_index):

    for y in range(len(game_map)):


        try:
            if block_index >= len(game_map[y]):

                block_index -= len(game_map[y])

            else:

                game_map[y][block_index] = '0'
                break

        except IndexError as e:
            pass

def add_block(block_index,block_id):

    for y in range(len(game_map)):

        try:
            if block_index >= len(game_map[y]):

                block_index -= len(game_map[y])

            elif game_map[y][block_index] == '0' and item_bar_empty == False:
                game_map[y][block_index] = block_id
                break

        except IndexError as e:
            pass
def print_1():

    print("SLOT SELECTED")

def left_click():


    if inventory_is_open == False:
        for i in range(len(tile_rects)):

            tile_coor_x1 = tile_rects[i][0] - scroll[0]
            tile_coor_x2 = tile_rects[i][0] - scroll[0] + TILE_SIZE

            tile_coor_y1 = tile_rects[i][1] - scroll[1]
            tile_coor_y2 = tile_rects[i][1] - scroll[1] + TILE_SIZE

            if mouse_pos[0] / mouse_share > tile_coor_x1 and mouse_pos[0] / mouse_share < tile_coor_x2 and mouse_pos[1] / mouse_share > tile_coor_y1 and mouse_pos[1] / mouse_share < tile_coor_y2:
                
                if [tile_rects[i][0],tile_rects[i][1]] not in torch_coors:
                    remove_block(i)

    if inventory_is_open:

        for i in range(len(slot_list_with_coors)):

            for i2 in range(len(slot_list_with_coors[i])):
                slot_coor_x1 = slot_list_with_coors[i][i2][0]
                slot_coor_x2 = slot_list_with_coors[i][i2][0] + TILE_SIZE

                slot_coor_y1 = slot_list_with_coors[i][i2][1]
                slot_coor_y2 = slot_list_with_coors[i][i2][1] + TILE_SIZE

                if mouse_pos[0] > slot_coor_x1 and mouse_pos[0] < slot_coor_x2 and mouse_pos[1] > slot_coor_y1 and mouse_pos[1] < slot_coor_y2:
                    selected_slot[0] = i
                    selected_slot[1] = i2
                    print("SELECTED SLOT: ",i,i2)
                    break

def mouse_on_inventory():

    if inventory_is_open:

        for i in range(len(slot_list_with_coors)):

            for i2 in range(len(slot_list_with_coors[i])):
                slot_coor_x1 = slot_list_with_coors[i][i2][0]
                slot_coor_x2 = slot_list_with_coors[i][i2][0] + TILE_SIZE

                slot_coor_y1 = slot_list_with_coors[i][i2][1]
                slot_coor_y2 = slot_list_with_coors[i][i2][1] + TILE_SIZE

                if mouse_pos[0] > slot_coor_x1 and mouse_pos[0] < slot_coor_x2 and mouse_pos[1] > slot_coor_y1 and mouse_pos[1] < slot_coor_y2:
                    mouse_on_slot[0] = i
                    mouse_on_slot[1] = i2
                    #print("SELECTED: ",i,i2)
                    break

def left_click_pressing():

    if inventory_is_open:

        for i in range(len(slot_list_with_coors)):

            for i2 in range(len(slot_list_with_coors[i])):
                slot_coor_x1 = slot_list_with_coors[i][i2][0]
                slot_coor_x2 = slot_list_with_coors[i][i2][0] + TILE_SIZE

                slot_coor_y1 = slot_list_with_coors[i][i2][1]
                slot_coor_y2 = slot_list_with_coors[i][i2][1] + TILE_SIZE

                if mouse_pos[0] > slot_coor_x1 and mouse_pos[0] < slot_coor_x2 and mouse_pos[1] > slot_coor_y1 and mouse_pos[1] < slot_coor_y2:
                    #print("SELECTED: ",i,i2)
                    selected_item[0] = i
                    selected_item[1] = i2
                    drag_item(i,i2)


def drag_item(i1_x,i2_x):

    index1 = i1_x
    index2 = i2_x
    selected2 = False
    global bool1, bool2

    for i in range(len(slot_coors)):

        for i2 in range(len(slot_coors[i])):

            try:

                if i == index1 and i2 == index2:
                    #print(slot_coors[i][i2][0],slot_coors[i][i2][1])


                    if slot_list_with_item_id[i][i2] in item_list:
                        #print("SELECTED ITEM: ", slot_list_with_coors[i])
                        if slot_list_with_item_id[i][i2] == 'dirt' and bool2 == False:
                            slot_coors[i][i2][0] = mouse_pos[0] - 16
                            slot_coors[i][i2][1] = mouse_pos[1] - 16
                            bool1 = True
                            selected2 = True

                        elif slot_list_with_item_id[i][i2] != 'dirt' and bool1 == False:
                            slot_coors[i][i2][0] = mouse_pos[0] - 16
                            slot_coors[i][i2][1] = mouse_pos[1] - 16
                            bool2 = True
                            selected2 = True

                        else:
                            pass

                    break

            except IndexError as error:
                pass
                # SLOT COORS DEGİSECEK CUNKU ONA GORE ITEM CIZILIYOR

        if selected2:
            break



def right_click(block_id):


    if inventory_is_open == False:
        for i in range(len(tile_rects)):

            tile_coor_x1 = tile_rects[i][0] - scroll[0]
            tile_coor_x2 = tile_rects[i][0] - scroll[0] + TILE_SIZE

            tile_coor_y1 = tile_rects[i][1] - scroll[1]
            tile_coor_y2 = tile_rects[i][1] - scroll[1] + TILE_SIZE

            tile_middle_coor = [tile_coor_x1 + 16, tile_coor_y1 + 16]


            if mouse_pos[0] / mouse_share > tile_coor_x1 and mouse_pos[0] / mouse_share < tile_coor_x2 and mouse_pos[1] / mouse_share > tile_coor_y1 and mouse_pos[1] / mouse_share < tile_coor_y2:
                
                if block_id in blocks:

                    if [tile_rects[i][0],tile_rects[i][1]] not in torch_coors:
                        add_block(i,block_id)

    else:
        #print(slot_list)
        pass

def draw_item_bar(x,y):

    x_pos = x
    y_pos = y
    for i in range(9):

        if i == pressed_number - 1:
            window.blit(selected_bar,(x_pos,y_pos))
        else:
            window.blit(empty_bar,(x_pos,y_pos))
        x_pos += TILE_SIZE

def put_item_on_item_bar(x,y):

    x_pos = x
    y_pos = y
    scale_x = 20
    scale_y = 20
    grass_image = pygame.transform.scale(grass, (scale_x,scale_y))
    dirt_image = pygame.transform.scale(dirt, (scale_x,scale_y))

    for i in range(9):

        if i == 0:
            window.blit(dirt_image,(x_pos + (empty_bar.get_width() - scale_x) / 2, y_pos + (empty_bar.get_height() - scale_y) / 2))

        if i == 1:
            window.blit(grass_image,(x_pos + (empty_bar.get_width() - scale_x) / 2, y_pos + (empty_bar.get_height() - scale_y) / 2))

        else:
            pass
        x_pos += TILE_SIZE

def create_inventory_list_with_coors(x,y,slot_list_with_coors):

    x_pos = x
    y_pos = y
    for i in range(6):

        for i2 in range(9):

            if len(slot_list_with_coors[i]) < 9:
                slot_list_with_coors[i].append([x_pos,y_pos])

            x_pos += TILE_SIZE

        x_pos = x
        y_pos += TILE_SIZE

def create_inventory(x,y,slot_list):

    for i in range(6):

        for i2 in range(9):

            if len(slot_list[i]) < 9:
                slot_list[i].append(0)

def open_inventory(x,y):

    x_pos = x
    y_pos = y
    for i in range(len(slot_list)):

        for i2 in range(len(slot_list[i])):

            if slot_list[i][i2] == 0:
                window.blit(empty_bar,(x_pos,y_pos))
                x_pos += TILE_SIZE
            elif slot_list[i][i2] == 1:
                window.blit(selected_bar,(x_pos,y_pos))
                x_pos += TILE_SIZE


            try:
                if i == selected_slot[0] and i2 == selected_slot[1]:

                    slot_list[i][i2] = 1
                    selected_last_slot[0] = selected_slot[0]
                    selected_last_slot[1] = selected_slot[1]

                else:
                    slot_list[i][i2] = 0

            except IndexError as error:
                print(selected_slot)

        x_pos = x
        y_pos += TILE_SIZE

"""def put_item_on_inventory(x,y):
    x_pos = x # X VE Y PARAMETRE OLARAK GELEN OBJENİN KOORDİNATLARI OLACAK VE SOL TIK İLE SÜRÜKLENDİĞİ ZAMAN OBJENİN KOORDİNATLARI DEĞİŞECEK LİSTEDEN
    y_pos = y
    scale_x = 20
    scale_y = 20
    grass_image = pygame.transform.scale(grass, (scale_x,scale_y))
    dirt_image = pygame.transform.scale(dirt, (scale_x,scale_y))
    for i in range(len(slot_list_with_item_id)):
        for i2 in range(len(slot_list_with_item_id[i])):
            if slot_list_with_item_id[i][i2] == 'dirt':
                window.blit(dirt_image,(x_pos + (empty_bar.get_width() - scale_x) / 2, y_pos + (empty_bar.get_height() - scale_y) / 2))
                x_pos += TILE_SIZE
            elif slot_list_with_item_id[i][i2] == 'grass':
                window.blit(grass_image,(x_pos + (empty_bar.get_width() - scale_x) / 2, y_pos + (empty_bar.get_height() - scale_y) / 2))
                x_pos += TILE_SIZE
            else:
                pass"""

def put_item_on_inventory(x,y):

    scale_x = 20
    scale_y = 20
    grass_image = pygame.transform.scale(grass, (scale_x,scale_y))
    dirt_image = pygame.transform.scale(dirt, (scale_x,scale_y))


    for i in range(len(slot_list_with_item_id)):

        for i2 in range(len(slot_list_with_item_id[i])):



            try:
                if slot_list_with_item_id[i][i2] == 'dirt':
                    window.blit(dirt_image,(slot_list_with_coors[i][i2][0] + (empty_bar.get_width() - scale_x) / 2 , slot_list_with_coors[i][i2][1] + (empty_bar.get_height() - scale_y) / 2))


                elif slot_list_with_item_id[i][i2] == 'grass':
                    window.blit(grass_image,(slot_list_with_coors[i][i2][0] + (empty_bar.get_width() - scale_x) / 2 , slot_list_with_coors[i][i2][1] + (empty_bar.get_height() - scale_y) / 2))

                else:
                    pass

            except IndexError as error:
                pass


def add_item_to_inventory_list(id):

    added = False
    for i in range(len(slot_list_with_item_id)):

        for i2 in range(len(slot_list_with_item_id[i])):


            if slot_list_with_item_id[i][i2] == '0':

                slot_list_with_item_id[i][i2] = id
                #print("EKLENDI")
                added = True
                break

        if added:
            break


def create_slot_list_with_item_id():

    for i in range(len(slot_list_with_item_id)):

        for i2 in range(9):

            slot_list_with_item_id[i].append("0")

    #print(slot_list_with_item_id)


def change_items_slot(i2_x,i2_y):

    i1_x = selected_item[0]
    i1_y = selected_item[1]

        
    try:
        slot_list_with_coors[i1_x][i1_y][0] = slot_list_with_coors[i2_x][i2_y][0]
        slot_list_with_coors[i1_x][i1_y][1] = slot_list_with_coors[i2_x][i2_y][1]

    except:
        pass


def control_mouse_on_blocks():

    for i in range(len(non_air_tile_rects)):

            tile_coor_x1 = non_air_tile_rects[i][0] - scroll[0]
            tile_coor_x2 = non_air_tile_rects[i][0] - scroll[0] + TILE_SIZE

            tile_coor_y1 = non_air_tile_rects[i][1] - scroll[1]
            tile_coor_y2 = non_air_tile_rects[i][1] - scroll[1] + TILE_SIZE

            global mouse_on_blocks

            if mouse_pos[0] / mouse_share > tile_coor_x1 and mouse_pos[0] / mouse_share < tile_coor_x2 and mouse_pos[1] / mouse_share > tile_coor_y1 and mouse_pos[1] / mouse_share < tile_coor_y2:
                
                mouse_on_blocks = True
                break

            else:

                mouse_on_blocks = False
#############

# VARIABLES & BOOLEANS #

moveRight = False
moveLeft = False
falling = True
grass_sound_control = False
first_time = True
item_bar_empty = True
inventory_is_open = False
bool1 = False
bool2 = False
dragging = False
particle_bool = False
mouse_on_blocks = False
fullscreen = False
particle_light = False

camera_share = 20
fullscreen_share = 4
screen_share = 2
mouse_share = screen_share
fullscreen_difference = fullscreen_share / screen_share
playerYMomentum = 0 # Player Vertical Momentum
airTimer = 0
global_slot_index = 2
dragging_items = 1
selected_slot = [50,50]
selected_last_slot = [50,50]
mouse_on_slot = [50,50]
selected_item = [50,50]

true_scroll = [0,0]

######################

# SECOND DEFINITIONS #

player = e.entity(100,100,17,22,'player','idle')

game_map = load_map('data/levels/level_0')
game_map.pop()
object_map = load_map('data/levels/object_map')
object_map.pop()
mouse_pos = [0,0]
slot_list = [[],[],[],[],[],[]]
slot_list_with_item_id = [[],[],[],[],[],[]]
slot_list_with_coors = [[],[],[],[],[],[]]
particles = []
item_list = ['dirt','grass']
block_type = '1'
pressed_number = 0
current_FPS = FPS

blocks = ['1']

#mini_map = pygame.transform.scale(display, (150,100))

#frame_difference = (map_frame.get_width() - mini_map.get_width()) / 2

#item_bar_length = empty_bar.get_width() * 9
#x_pos_of_item_bar = (WINDOW_SIZE[0] / 2) - (item_bar_length / 2)
#y_pos_of_item_bar = WINDOW_SIZE[1] - empty_bar.get_height()

#x_pos_of_inventory = (WINDOW_SIZE[0] / 2) - (item_bar_length / 2)
#y_pos_of_inventory = (WINDOW_SIZE[1] / 2) - (item_bar_length / 2)

#create_inventory_list_with_coors(x_pos_of_inventory-100,y_pos_of_inventory,slot_list_with_coors)
#create_inventory(x_pos_of_inventory-100,y_pos_of_inventory,slot_list)

#slot_coors = slot_list_with_coors

#create_slot_list_with_item_id()

#add_item_to_inventory_list("dirt")
#print(slot_list_with_item_id[0])
#add_item_to_inventory_list("grass")
#print(slot_list_with_item_id[0])
#print(slot_coors[0])


myfont = pygame.font.SysFont('Arial', 15)

torch_list = []
torch_coors = []
y =  0
for row in object_map:
    x = 0
    for tile in row:

        if tile == '3':
            torch = e.entity(x * TILE_SIZE, y * TILE_SIZE,16,16,'walltorch1','open')
            if torch not in torch_list:
                torch_list.append(torch)
                torch_coors.append([x * TILE_SIZE, y * TILE_SIZE])

        x += 1
    y += 1

######################

while True:

    if fullscreen:
        #print("FS")
        WINDOW_SIZE = (real_resolution)
        window = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN, vsync = 0)
        display = pygame.Surface((real_resolution[0]/fullscreen_share,real_resolution[1]/fullscreen_share))
        true_scroll[0] += (player.x-true_scroll[0]-((WINDOW_SIZE[0]/(fullscreen_share ** 2)) - (player.size_x / 2))) / (camera_share / fullscreen_difference)
        true_scroll[1] += (player.y-true_scroll[1]-((WINDOW_SIZE[1]/(fullscreen_share ** 2)) - (player.size_y / 2))) / (camera_share / fullscreen_difference)

        #mini_map = pygame.transform.scale(display, (150,100))

        #frame_difference = (map_frame.get_width() - mini_map.get_width()) / 2

        #item_bar_length = empty_bar.get_width() * 9
        #x_pos_of_item_bar = (WINDOW_SIZE[0] / 2) - (item_bar_length / 2)
        #y_pos_of_item_bar = WINDOW_SIZE[1] - empty_bar.get_height()

       
    elif fullscreen == False:
        true_scroll[0] += (player.x-true_scroll[0]-((WINDOW_SIZE[0]/4) - (player.size_x / 2)))/20
        true_scroll[1] += (player.y-true_scroll[1]-((WINDOW_SIZE[1]/4) - (player.size_y / 2)))/20
        #print("NOT FS")
        window_width = 600
        window_height = 400
        WINDOW_SIZE = (window_width,window_height)
        window = pygame.display.set_mode(WINDOW_SIZE,pygame.RESIZABLE)
        display = pygame.Surface((window_width/2,window_height/2))

        #mini_map = pygame.transform.scale(display, (150,100))

        #frame_difference = (map_frame.get_width() - mini_map.get_width()) / 2

        #item_bar_length = empty_bar.get_width() * 9
        #x_pos_of_item_bar = (WINDOW_SIZE[0] / 2) - (item_bar_length / 2)
        #y_pos_of_item_bar = WINDOW_SIZE[1] - empty_bar.get_height()

      

    clock.tick(FPS)
    
    current_FPS = int(clock.get_fps())
    current_FPS = "FPS: " + str(current_FPS)
    textsurface = myfont.render(current_FPS,False,(255,255,255))

    display.fill((46,124,180))

    mouse_pos = list(pygame.mouse.get_pos())

    if stone_walk_sound_timer > 0:
        stone_walk_sound_timer -= 1



# SCROLL & PARALLAX #

    true_scroll[0] += (player.x-true_scroll[0]-((WINDOW_SIZE[0]/(screen_share ** 2)) - (player.size_x / 2))) / camera_share
    true_scroll[1] += (player.y-true_scroll[1]-((WINDOW_SIZE[1]/(screen_share ** 2)) - (player.size_y / 2))) / camera_share

    scroll = true_scroll.copy()
    scroll[1] = int(scroll[1])
    scroll[0] = int(scroll[0])

    display.blit(background_image,((-(scroll_share/2) * 16) - scroll[0] * 0.25, (-(scroll_share/2) * 16) - scroll[1] * 0.25))

    """a = -100
                for y in range(int((WINDOW_SIZE[1]) / bg_stone_dark.get_height())):
                    b = -100
                    for x in range(int((WINDOW_SIZE[0]) / bg_stone_dark.get_width())):
            
                        display.blit(bg_stone_dark,(b - scroll[0] * 0.25, a - scroll[1] * 0.25))
                        b += 16
            
                    a += 16"""
    

    """for bg_object in background_object:
                    obj_rect = pygame.Rect(bg_object[1][0]-scroll[0]*bg_object[0], bg_object[1][1]-scroll[1]*bg_object[0],bg_object[1][2],bg_object[1][3])
                    if bg_object[0] == 0.5:
                        pygame.draw.rect(display, (14,222,150),obj_rect)
                    else:
                        pygame.draw.rect(display, (9,100,95),obj_rect)"""

####################

    mouse_on_inventory()
    if pygame.mouse.get_pressed()[0]:

        left_click_pressing()

    else:
        bool1 = False
        bool2 = False



# DRAW MAP #

    tile_rects = []
    non_air_tile_rects = []
    non_air_tile_rects_with_scroll = []
    y =  0
    for row in game_map:
        x = 0
        for tile in row:

            if tile == '1':
                display.blit(stone, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            
            if tile == '1': #  or tile == '2'
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                non_air_tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                non_air_tile_rects_with_scroll.append(pygame.Rect(x * TILE_SIZE - scroll[0] , y * TILE_SIZE - scroll[1] , TILE_SIZE, TILE_SIZE))

            if tile == '0':
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE , 0, 0))
            x += 1
        y += 1

#############

    control_mouse_on_blocks()

    #print(mouse_on_blocks)
    particles.append([[mouse_pos[0] / mouse_share,mouse_pos[1] / mouse_share],[random.randint(0,20) / 10 - 1, -2], random.randint(4,6)])
    particle_tiles = []
    particle_momentum = []

    if mouse_on_blocks:
        particles = []

    for particle in particles:

        particle_momentum.append(particle[1])


    for particle in particles:

        if particle_bool and mouse_on_blocks == False:

            pygame.draw.circle(display, (255,255,255), [int(particle[0][0]),int(particle[0][1])], int(particle[2]))
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.035
            particle[1][1] += 0.3

            particle_tiles.append(pygame.Rect(particle[0][0],particle[0][1],particle[2],particle[2]))

            if particle_light:
                radius = particle[2] * 2
                display.blit(circle_surf((radius + 5), (20,20,20)), (int(particle[0][0] - (radius + 5)), int(particle[0][1] - (radius + 5))), special_flags=BLEND_RGB_ADD)

            if particle[2] <= 0:
                particles.remove(particle)

    if particle_bool:

        for i in range(len(non_air_tile_rects_with_scroll)):

            tile_coor_x1 = non_air_tile_rects_with_scroll[i][0] - scroll[0]
            tile_coor_x2 = non_air_tile_rects_with_scroll[i][0] - scroll[0] + TILE_SIZE

            tile_coor_y1 = non_air_tile_rects_with_scroll[i][1] - scroll[1]
            tile_coor_y2 = non_air_tile_rects_with_scroll[i][1] - scroll[1] + TILE_SIZE

            for particle in particles:

                if particle_bool:
                    
                    if particle[0][0] > tile_coor_x1 and particle[0][0] < tile_coor_x2 and particle[0][1] > tile_coor_y1 and particle[0][1] < tile_coor_y2:
                     pass

                     """       
                                                                                       particle[1][0] = -0.7 * particle[1][0]
                                                                                       particle[1][1] *= 0.95
                                                                                       particle[0][0] += particle[1][0] * 2
                                                               
                                                                                       particle[1][1] = -0.7 * particle[1][1]
                                                                                       particle[1][0] *= 0.95
                                                                                       particle[0][1] += particle[1][1] * 2
                                                                                       """
#  PLAYER MOVEMENT & PHYSICS #
    
    for tile in non_air_tile_rects_with_scroll:
        
        for index, particle_tile in enumerate(particle_tiles):
            
            #if pygame.Rect.contains(tile,particle_tile):
                #print("COLLIDE")

            if pygame.Rect.colliderect(particle_tile,tile):
                #print("COLLIDE 2")
                try:
                    particles.pop(index)
                except:
                    pass


    #particle_tiles, collision_types_of_particles = move_particle(particle_tiles, non_air_tile_rects_with_scroll, particle_momentum)


    player_movement = [0,0]

    if moveRight:
        player_movement[0] += 2

    if moveLeft:
        player_movement[0] -= 2
    player_movement[1] += playerYMomentum

    playerYMomentum += 0.2

    if playerYMomentum > 5:
        playerYMomentum = 5

    if player_movement[0] == 0:
        player.set_action('idle')

    if player_movement[0] > 0:
        player.set_action('run')
        player.set_flip(False)

    if player_movement[0] < 0:
        player.set_action('run')
        player.set_flip(True)

    collision_types = player.move(player_movement, tile_rects)

    if collision_types['right'] == True or collision_types['left'] == True:
        grass_sound_control = False
    else:
        grass_sound_control = True

    if collision_types['bottom']:
        playerYMomentum = 0
        airTimer = 0
        if grass_sound_control:
            if player_movement[0] != 0:
                if stone_walk_sound_timer == 0:
                    stone_walk_sound_timer = 30
                    random.choice(stone_walk_sounds).play()
    else:
        airTimer += 1

    if collision_types['top']:
        playerYMomentum = 0


    if airTimer > 10 and airTimer < 20:
        falling = True

    if collision_types['bottom'] == True and falling == True and first_time == False:
        fall_off_sound.play()
        falling = False

    if player.y > 500:
        player.x = 50
        player.y = 179
        airTimer = 0

###########################
    
    player.change_frame(1)
    player.display(display,scroll)

    for i in range(len(torch_list)):
        torch_list[i].change_frame(1)
        torch_list[i].display(display,scroll)

     ###LIGHTING OBJECT###
    radius0 = torch.size_x - 5
    radius1 = torch.size_x + 5
    radius2 = torch.size_x + 15
    for torch in torch_list:
        radius0 -= random.randint(2,8)/1.5
        display.blit(circle_surf((radius0 + torch.size_x / 2), (20,20,20)), (float(torch.x - (radius0)) - scroll[0], float(torch.y - (radius0)) - scroll[1]), special_flags=BLEND_RGB_ADD)
        radius1 -= random.randint(2,8)/1.5
        display.blit(circle_surf((radius1 + torch.size_x / 2), (20,20,20)), (float(torch.x - (radius1)) - scroll[0], float(torch.y - (radius1)) - scroll[1]), special_flags=BLEND_RGB_ADD)
        radius2 -= random.randint(2,8)/1.5
        display.blit(circle_surf((radius2 + torch.size_x / 2), (20,20,20)), (float(torch.x - (radius2)) - scroll[0], float(torch.y - (radius2)) - scroll[1]), special_flags=BLEND_RGB_ADD)

    ###############


# EVENT LISTENING #

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:

            if event.key == K_RIGHT:
                moveRight = True
            if event.key == K_LEFT:
                moveLeft = True
            if event.key == K_UP:
                if airTimer < 5:
                    playerYMomentum = -5
                    jump_sound.play()
                    first_time = False
                    falling = True

            if event.key == K_d:
                moveRight = True

            if event.key == K_a:
                moveLeft = True

            if event.key == K_w:
                if airTimer < 5:
                    playerYMomentum = -5
                    jump_sound.play()
                    first_time = False
                    falling = True

            if event.key == K_p:

                if particle_bool:
                    particle_bool = False
                    particles = []

                else:
                    if mouse_on_blocks == False:
                        particle_bool = True

            if event.key == K_m:
                if pygame.mixer.music.get_volume() < 0.6:
                    pygame.mixer.music.set_volume(0.7)
                    break

                if pygame.mixer.music.get_volume() > 0:
                    pygame.mixer.music.set_volume(0)
                    break

            if event.key == K_x:

                save_edited_map()

            if event.key == K_l:

                if particle_light:
                    particle_light = False

                else:
                    particle_light = True

            if event.key == K_F5:
                print("Restart")
                restart_game()

            if event.key == K_F11:

                if fullscreen:
                    ###WINDOWED###
                    fullscreen = False
                    mouse_share = screen_share

                elif fullscreen == False:
                    ###FULLSCREEN###
                    fullscreen = True
                    mouse_share = fullscreen_share

                    #print("SCROLL SHARE MULTIPILIER: ",(int(real_resolution[0]/window_width) + int(real_resolution[1]/window_height)))


            if event.key == K_e:
                if inventory_is_open == False:
                    inventory_is_open = True
                elif inventory_is_open:
                    inventory_is_open = False

            if event.key == K_1:
                block_type = '1'
                pressed_number = 1
                item_bar_empty = False

            if event.key == K_2:
                block_type = '2'
                pressed_number = 2
                item_bar_empty = False

            if event.key == K_3:
                pressed_number = 3
                item_bar_empty = True

            if event.key == K_4:
                pressed_number = 4
                item_bar_empty = True

            if event.key == K_5:
                pressed_number = 5
                item_bar_empty = True

            if event.key == K_6:
                pressed_number = 6
                item_bar_empty = True

            if event.key == K_7:
                pressed_number = 7
                item_bar_empty = True

            if event.key == K_8:
                pressed_number = 8
                item_bar_empty = True

            if event.key == K_9:
                pressed_number = 9
                item_bar_empty = True

        if event.type == MOUSEBUTTONDOWN:

            if event.button == 3:
                right_click(block_type)

            if event.button == 1:
                left_click()
                pass

        if event.type == MOUSEBUTTONUP:

            if event.button == 1:
                #print("RELEASED")
                mouse_on_inventory()

                change_items_slot(mouse_on_slot[0],mouse_on_slot[1])

        if event.type == KEYUP:

            if event.key == K_RIGHT:
                moveRight = False
            if event.key == K_LEFT:
                moveLeft = False

            if event.key == K_d:
                moveRight = False

            if event.key == K_a:
                moveLeft = False

####################


# UPDATE #

    surface = pygame.transform.scale(display, WINDOW_SIZE)
    #mini_map = pygame.transform.scale(display, (150,100)) # 150 100 first
    #current_image = empty_bar
    #map_frame = pygame.transform.scale(map_frame, (170,120))
    window.blit(surface,(0,0))
    #window.blit(mini_map,(WINDOW_SIZE[0]-mini_map.get_width()- frame_difference, frame_difference))
    #window.blit(map_frame,(WINDOW_SIZE[0]-map_frame.get_width(),0))
    #draw_item_bar(x_pos_of_item_bar,y_pos_of_item_bar)
    #put_item_on_item_bar(x_pos_of_item_bar,y_pos_of_item_bar)
    window.blit(textsurface,(0,0))
    #window.blit(this_image,(250,250))
    """if inventory_is_open:
                    open_inventory(x_pos_of_inventory-100,y_pos_of_inventory)
                    put_item_on_inventory(slot_coors[0][0][0],slot_coors[0][0][1])
                else:
                    selected_slot = [50,50]"""

    #print(clock.get_fps())
    #window.blit(empty_bar,(227,368))
##########

    pygame.display.update()
