import pygame
from pygame.locals import *

# physics
def CollisionTest(Object1,ObjectList):
    CollisionList = []
    for Object in ObjectList:
        if Object.colliderect(Object1):
            CollisionList.append(Object)
    return CollisionList

class PhysicsObject(object):
    
    def __init__(self,x,y,x_size,y_size):
        self.width = x_size
        self.height = y_size
        self.rect = pygame.Rect(x,y,self.width,self.height)
        self.x = x
        self.y = y
        self.hitbox = None

    def setup_hitbox(self,x_offset,y_offset,x_size,y_size):
        self.hitbox = [x_offset,y_offset,x_size,y_size]

    def get_hitbox(self):
        return pygame.Rect(self.x+self.hitbox[0],self.y+self.hitbox[1],self.hitbox[2],self.hitbox[3])
        
    def move(self,Movement,platforms,ramps):
        self.x += Movement[0]
        self.rect.x = int(self.x)
        block_hit_list = CollisionTest(self.rect,platforms)
        collision_types = {'top':False,'bottom':False,'right':False,'left':False,'slant_bottom':False}
        for block in block_hit_list:
            if Movement[0] > 0:
                self.rect.right = block.left
                collision_types['right'] = True
            elif Movement[0] < 0:
                self.rect.left = block.right
                collision_types['left'] = True
            self.x = self.rect.x
        self.y += Movement[1]
        self.rect.y = int(self.y)
        block_hit_list = CollisionTest(self.rect,platforms)
        for block in block_hit_list:
            if Movement[1] > 0:
                self.rect.bottom = block.top
                collision_types['bottom'] = True
            elif Movement[1] < 0:
                self.rect.top = block.bottom
                collision_types['top'] = True
            self.change_y = 0
            self.y = self.rect.y                #碰撞检测，此游戏按道理应该没有，可能使用继承的代码
                                                #TODO:去除冗余代码



        for ramp in ramps:
            rampR = pygame.Rect(ramp[0],ramp[1],20,20)
            if self.rect.colliderect(rampR):
                if ramp[2] == 1:
                    if self.rect.right-ramp[0]+self.rect.bottom-ramp[1] > 20:
                        self.rect.bottom = ramp[1]+20-(self.rect.right-ramp[0])
                        self.y = self.rect.y
                        collision_types['slant_bottom'] = True
                if ramp[2] == 2:
                    if ramp[0]+20-self.rect.left+self.rect.bottom-ramp[1] > 20:
                        self.rect.bottom = ramp[1]+20-(ramp[0]+20-self.rect.left)
                        self.y = self.rect.y
                        collision_types['slant_bottom'] = True
        return collision_types
            
    def Draw(self):
        pygame.draw.rect(screen,(0,0,255),self.rect)
        
    def CollisionItem(self):
        CollisionInfo = [self.rect.x,self.rect.y,self.width,self.height]
        return CollisionInfo

def flip(img,boolean=True):
    return pygame.transform.flip(img,boolean,False)

def blit_center(surf,surf2,pos):
    x = int(surf2.get_width()/2)
    y = int(surf2.get_height()/2)
    surf.blit(surf2,(pos[0]-x,pos[1]-y))

class entity(object):
    global animation_database, animation_higher_database
    
    def __init__(self,x,y,size_x,size_y,e_type): # x, y, size_x, size_y, type
        self.x = x
        self.y = y
        self.size_x = size_x
        self.size_y = size_y
        self.obj = PhysicsObject(x,y,size_x,size_y)
        self.animation = None
        self.image = None
        self.animation_frame = 0
        self.animation_tags = []
        self.flip = False
        self.offset = [0,0]
        self.rotation = 0
        self.type = e_type # used to determine animation set among other things
        self.action_timer = 0
        self.action = ''
        self.set_action('idle') # overall action for the entity
        self.entity_data = {}
        self.alpha = None

    def set_pos(self,x,y):
        self.x = x
        self.y = y
        self.obj.x = x
        self.obj.y = y
        self.obj.rect.x = x
        self.obj.rect.y = y

    def move(self,momentum,platforms,ramps):
        collisions = self.obj.move(momentum,platforms,ramps)
        self.x = self.obj.x
        self.y = self.obj.y
        return collisions

    def rect(self):
        return pygame.Rect(self.x,self.y,self.size_x,self.size_y)

    def get_center(self):
        return [self.x+int(self.size_x/2),self.y+int(self.size_y/2)]

    def set_flip(self,boolean):
        self.flip = boolean

    def set_animation_tags(self,tags):
        self.animation_tags = tags

    def set_animation(self,sequence):
        self.animation = sequence
        self.animation_frame = 0

    def set_action(self,action_id,force=False):
        if (self.action == action_id) and (force == False):
            pass
        else:
            self.action = action_id
            anim = animation_higher_database[self.type][action_id]
            self.animation = anim[0]
            self.set_animation_tags(anim[1])
            self.animation_frame = 0

    def clear_animation(self):
        self.animation = None

    def set_image(self,image):
        self.image = image

    def set_offset(self,offset):
        self.offset = offset

    def set_frame(self,amount):
        self.animation_frame = amount

    def handle(self):
        self.action_timer += 1
        self.change_frame(1)

    def change_frame(self,amount):
        self.animation_frame += amount
        if self.animation != None:
            #TODO:删除多余代码
            # while self.animation_frame < 0:
            #     if 'loop' in self.animation_tags:
            #         self.animation_frame += len(self.animation)
            #     else:
            #         self.animation = 0
            while self.animation_frame >= len(self.animation):
                if 'loop' in self.animation_tags:
                    self.animation_frame -= len(self.animation)
                else:
                    self.animation_frame = len(self.animation)-1

    def get_current_img(self):
        if self.animation == None:
            if self.image != None:
                return flip(self.image,self.flip)
            else:
                return None
        else:
            return flip(animation_database[self.animation[self.animation_frame]],self.flip)

    def display(self,surface,scroll):
        image_to_render = None
        if self.animation == None:
            if self.image != None:
                image_to_render = flip(self.image,self.flip).copy()
        else:
            image_to_render = flip(animation_database[self.animation[self.animation_frame]],self.flip).copy()
        if image_to_render != None:
            center_x = image_to_render.get_width()/2
            center_y = image_to_render.get_height()/2
            image_to_render = pygame.transform.rotate(image_to_render,self.rotation)
            if self.alpha != None:
                image_to_render.set_alpha(self.alpha)
            blit_center(surface,image_to_render,(int(self.x)-scroll[0]+self.offset[0]+center_x,int(self.y)-scroll[1]+self.offset[1]+center_y))

# animation stuff
global animation_database
animation_database = {}

global animation_higher_database
animation_higher_database = {}

# a sequence looks like [[0,1],[1,1],[2,1],[3,1],[4,2]]
# the first numbers are the image name(as integer), while the second number shows the duration of it in the sequence
def animation_sequence(sequence,base_path,colorkey=(255,255,255),transparency=255):
    global animation_database
    result = []
    for frame in sequence:
        image_id = base_path + base_path.split('/')[-2] + '_' + str(frame[0])
        image = pygame.image.load(image_id + '.png').convert()
        image.set_colorkey(colorkey)
        image.set_alpha(transparency)
        animation_database[image_id] = image.copy()
        for _ in range(frame[1]):
            result.append(image_id)
    return result


def get_frame(ID):
    global animation_database
    return animation_database[ID]

def load_animations(path):
    global animation_higher_database
    f = open(path + 'entity_animations.txt','r')
    data = f.read()
    f.close()
    for animation in data.split('\n'):
        sections = animation.split(' ')
        anim_path = sections[0]
        entity_info = anim_path.split('/')
        entity_type = entity_info[0]
        animation_id = entity_info[1]
        timings = sections[1].split(';')
        tags = sections[2].split(';')  #TODO: clear unused code
        sequence = []
        n = 0
        for timing in timings:
            sequence.append([n,int(timing)])
            n += 1
        anim = animation_sequence(sequence,path + anim_path)
        if entity_type not in animation_higher_database:
            animation_higher_database[entity_type] = {}
        animation_higher_database[entity_type][animation_id] = [anim.copy(),tags]
