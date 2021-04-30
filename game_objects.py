# ======================================
# ==          I M P O R T S           ==
# ======================================
# Tell main where to find the libraries
# and other game code. It will search in
# this directory and in Thonny's directory.

import pygame
from pygame.locals import *

import math
import random

import pytmx
from pytmx.util_pygame import load_pygame

import methods
from methods import blit_all_tiles
from methods import get_tile_properties
from methods import play_sound

import constants
from constants import *

# ============================================
# ==             SPRITE SHEET               ==
# ============================================
# Pygame may not itself handle sprite sheets
# all that well. Found a function that does.
# documentation at https://www.pygame.org/wiki/Spritesheet

# NOTE: Probably should make a master sprite sheet rather than
# each object having their own.

class Sprite_Sheet(object):
    
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename)
        except pygame.error:
            print ("Unable to load spritesheet image:", filename)
            return
        
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface((rect.size),pygame.SRCALPHA).convert_alpha()
        image.set_alpha(255)
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]

    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

# ============================================
# ==            SPRITE HANDLER              ==
# ============================================
# Creates and manages all sprites. Holds the lists
# of sprites in Pygame Groups.

class Sprite_Handler(object):
    
    def __init__(self):
        
        self.name = "Hello"
        self.soldier = Player("soldier",100,100,(0,0))
        self.tank = Player("tank", 100,100,(0,0))
        self.soldier.assign_partner(self.tank)
        self.tank.assign_partner(self.soldier)
        
        # Enemies collide with player and are damaged by player projectiles, in general.
        self.enemy_list = pygame.sprite.Group()
        # Items collide with player and then die, modifying player inventory.
        self.item_list = pygame.sprite.Group()
        # Enemy projectiles collide with player, dealing damage.
        self.enemy_projectile_list = pygame.sprite.Group()
        # Player projectiles collide with enemies, dealing damage.
        self.player_projectile_list = pygame.sprite.Group()
        # Doodads can interact with all other sprites. Switches, moving platforms, etc.
        self.doodad_list = pygame.sprite.Group()
        # Effects don't interact withodad anything; they are used for graphical flair.
        self.effect_list = pygame.sprite.Group()
        
        # HUD Displays information
        self.hud = Hud()
        
        # Communicate to main that control mode needs to change
        self.wants_to_change_control_mode = False
        
    def change_control_mode(self):
        temp_bool = self.wants_to_change_control_mode
        self.wants_to_change_control_mode = False
        return temp_bool
        
    def player_enemy_collision_check(self, control_state):
        
        # Check Tank collisions
        if(control_state == TANK_ACTIVE and self.tank.behavior_state != DYING):
            
            self.enemy_hit_list = pygame.sprite.spritecollide(self.tank, self.enemy_list, False)
            
            player_was_hit = False
            
            for enemy in self.enemy_hit_list:
                 if(enemy.state != DYING) and (enemy.state != DEAD):
                    if( (self.tank.rect.y<enemy.rect.y)and(self.tank.vector[1]>0)):
                         enemy.got_squished()
                         enemy_position = enemy.getpos()
                         enemy_x = enemy_position[0]
                         enemy_y = enemy_position[1]
                         explosion = Effect(enemy_x,enemy_y)
                         self.doodad_list.add(explosion)
                    else:
                        player_was_hit = True
                        
            if player_was_hit: self.tank.take_damage()
  
        # Check Soldier collisions
        elif(control_state == SOLDIER_ACTIVE and self.soldier.behavior_state != DYING):
                
            self.enemy_hit_list = pygame.sprite.spritecollide(self.soldier, self.enemy_list, False)
            
            player_was_hit = False
            
            for enemy in self.enemy_hit_list:
                 if(enemy.state != DYING) and (enemy.state != DEAD):
                    if( (self.soldier.rect.y<enemy.rect.y)and(self.soldier.vector[1]>0)):
                         enemy.got_squished()
                         enemy_position = enemy.getpos()
                         enemy_x = enemy_position[0]
                         enemy_y = enemy_position[1]
                         explosion = Effect(enemy_x,enemy_y)
                         self.doodad_list.add(explosion)
                    else:
                        player_was_hit = True
                        
            if player_was_hit: self.soldier.take_damage()           
                    
    def get_player(self, control_state):
        
        if(control_state == TANK_ACTIVE):
            return self.tank
        elif(control_state == SOLDIER_ACTIVE):
            return self.soldier
    
    def update(self, tmxdata, keys, control_state):
        
        # Remove sprites
        for enemy in self.enemy_list:
            if(enemy.behavior_state == DEAD): enemy.kill()
        for player_projectile in self.player_projectile_list:
            if(player_projectile.behavior_state == DEAD): player_projectile.kill()
        for effect in self.effect_list:
            if(effect.behavior_state == DEAD): effect.kill()
                      
        if(self.tank.behavior_state == DEAD): self.tank.kill()
        if(self.soldier.behavior_state == DEAD): self.soldier.kill()
        
        # Only the active player object get the keys
        
        if(control_state == SOLDIER_ACTIVE):
            self.soldier.apply_input(keys)
        elif(control_state == TANK_ACTIVE):
            self.tank.apply_input(keys)
            
        # See if we need to change control mode
        if(control_state == SOLDIER_ACTIVE):
            self.wants_to_change_control_mode = self.soldier.change_control_mode()        
        if(control_state == TANK_ACTIVE):
            self.wants_to_change_control_mode = self.tank.change_control_mode()
                    
        # Update
        self.soldier.update(tmxdata, keys)
        self.tank.update(tmxdata, keys)
        self.enemy_list.update(tmxdata, keys)
        self.player_projectile_list.update()
        self.effect_list.update()
        
        # See if a player object wants to spawn other objects
        spawn_tuple = self.tank.spawn()
        if(control_state == SOLDIER_ACTIVE):
            spawn_tuple = self.soldier.spawn()
        
        wants_to_spawn_sprite = spawn_tuple[0]
        type_of_sprite_to_spawn = spawn_tuple[1]
        name_of_sprite_to_spawn = spawn_tuple[2]
        coords_of_sprite_to_spawn = spawn_tuple[3]
        vector_of_sprite_to_spawn = spawn_tuple[4]
        
        # Spawn objects requested by player
        if(wants_to_spawn_sprite == True):
            if(type_of_sprite_to_spawn == "player_projectile"):    
                if(name_of_sprite_to_spawn == "small_bullet"):
                    # Spawn a bullet
                    new_player_projectile = Player_projectile(name_of_sprite_to_spawn,coords_of_sprite_to_spawn[0],coords_of_sprite_to_spawn[1],vector_of_sprite_to_spawn)
                    self.player_projectile_list.add(new_player_projectile)
                    # Spawn the pellet blast effect
                    new_direction = RIGHT
                    if(vector_of_sprite_to_spawn[0]<0): new_direction = LEFT
                    new_effect = Effect("pellet_burst",coords_of_sprite_to_spawn[0],coords_of_sprite_to_spawn[1],new_direction)
                    self.effect_list.add(new_effect)

            if(type_of_sprite_to_spawn == "effect"):
                if(name_of_sprite_to_spawn == "tank_jump"):
                    new_effect = Effect(name_of_sprite_to_spawn,coords_of_sprite_to_spawn[0],coords_of_sprite_to_spawn[1],vector_of_sprite_to_spawn)
                    self.effect_list.add(new_effect)
                    print(coords_of_sprite_to_spawn)

        #Update
        if(control_state == TANK_ACTIVE):
            self.hud.update(self.tank.get_hp())
        elif(control_state == SOLDIER_ACTIVE):
            self.hud.update(self.soldier.get_hp())
        
        # Check to see if map needs to change.
        self.check_for_map_exit(tmxdata, control_state)
    
    def draw(self, map_image):
        
        self.tank.draw(map_image)
        self.soldier.draw(map_image)
        self.player_projectile_list.draw(map_image)
        self.effect_list.draw(map_image)
    
    def draw_hud(self):
    
        return self.hud.draw()
        
    def get_player_pos(self, control_state):
        if(control_state == TANK_ACTIVE):
            return self.tank.getpos()
        elif(control_state == SOLDIER_ACTIVE):
            return self.soldier.getpos()
    
    # Function searches the Object layers of the TMXDATA you pass
    # and, if it finds any objects named "enemy," spawns an enemy
    # in that location.
    def spawn_sprites_from_map(self, tmxdata):
        
       for layer in tmxdata.visible_layers:
            if(isinstance(layer,pytmx.TiledTileLayer)):
                for tile_object in tmxdata.objects:
                    if (tile_object.name == "enemy_spawn"):
                        enemy = Enemy(tile_object.x,tile_object.y,(0,0))
                        self.enemy_list.add(enemy)

    # Clear all sprites other than players.
    def prepare_for_new_map(self):
        
        # Remove all non-player sprites
        self.enemy_list.empty()
        self.doodad_list.empty()
        
    def reset_player(self, tmxdata):
        self.tank.hit_points = 4
        self.tank.state = self.player.STANDING
        self.player.hit_points = 4
        self.player.state = self.player.STANDING
        self.player_enters_map(tmxdata, RIGHT)
        
    # Find the entrance object and put player there.
    # If there isnt a player yet, make one at the spawn point.
    def player_enters_map(self, tmxdata, entrance_direction):

        for layer in tmxdata.visible_layers:
            if(isinstance(layer,pytmx.TiledTileLayer)):
                for tile_object in tmxdata.objects:
                    if (tile_object.name == "entrance"):
                        if(tile_object.properties['dir'] == "RIGHT" and entrance_direction == RIGHT):
                            self.tank.setpos(tile_object.x,tile_object.y)
                            self.soldier.setpos(tile_object.x,tile_object.y)
                        elif(tile_object.properties['dir'] == "LEFT" and entrance_direction == LEFT):
                            self.tank.setpos(tile_object.x,tile_object.y)
                            self.soldier.setpos(tile_object.x,tile_object.y)
                        elif(tile_object.properties['dir'] == "UP" and entrance_direction == UP):
                            self.tank.setpos(tile_object.x,tile_object.y)
                            self.soldier.setpos(tile_object.x,tile_object.y) 
                        elif(tile_object.properties['dir'] == "DOWN" and entrance_direction == DOWN):
                            self.tank.setpos(tile_object.x,tile_object.y)
                            self.soldier.setpos(tile_object.x,tile_object.y)
                        else: print("No appropriate landing direction found!")
                            
    def check_for_map_exit(self, tmxdata, control_state):
        
        # Look for the screen exit object
        for tile_object in tmxdata.objects:
            if(tile_object.name == 'exit'):
                player_rect = Rect(self.tank.rect)
                if(control_state == SOLDIER_ACTIVE): player_rect = Rect(self.soldier.rect)
                exit_object_rect = Rect(tile_object.x,tile_object.y,tile_object.width,tile_object.height)
        
                # If the player is intersecting the exit object, need to load a new screen.
                if(pygame.Rect.colliderect(player_rect,exit_object_rect)):
                    print(tile_object.properties)
                    return tile_object.properties
                
        default_dict = {'dest':'none', 'dir':'none'}
        return default_dict

# ============================================
# ==             PLAYER CLASS               ==
# ============================================
# This class is the soldier player sprite.

class Player(pygame.sprite.Sprite):
    
    # Initialization
    def __init__ (self,name,init_x,init_y,init_vector):
        
        # Call the init function of the sprite class from which this inherets.
        pygame.sprite.Sprite.__init__(self)
        
        # ID ------------
        # So that other sprites can identify this one.
        self.name = name
        
        # HEALTH VARIABLES ----------
        self.hit_points = 16 # How many hit points this object has
        self.i_frames = 0 # If this is positive, object is temporarily invulnerable
        self.i_blink_counter = 0 # A counter to time how quickly the object blinks while invulnerable
        self.i_blink = False # A boolean to decide whether to display the sprite (for blinking).
        
        # MOVEMENT VARIABLES ----------
        # Jumping
        self.has_jumped = False #This makes sure you only jump once; resets when you touch the ground.
        self.on_ground = True #This makes sure you can only jump on the ground.
        self.holding_jump = False #This allows the player some control over jump height
        # Firing
        self.has_fired = True # Have you recently used the fire ability
        self.fire_cooldown = 0 #Can only fire if cooldown is back to 0
        self.holding_fire = False #allows player to hold the fire button for rapid fire weapons
        # Dashing
        self.has_dashed = False #Have you recently used dash ability
        self.dash_cooldown = 0 #Can only dash if the cooldown is back to 0
        self.holding_dash = False #This allows player some control over dash distance
        
        # Variables for handling swapping between modes
        self.partner = Player
        self.wants_to_change_control_mode = False
        
        # SOLDIER SETUP
        # =================================
        if(self.name == "soldier"):
            
            # GRAPHICS SETUP ------------        
            # Instead of loading an image directly we will use the
            # spritesheet object, defined below. 
            self.my_sprite_sheet = Sprite_Sheet("Assets\Graphics\Player\Soldier.png")
            # The sprites on the sprite sheet are 64x64, but only the middle 32x32 is checked
            # for collision. Need to keep track of the offset for the top left corner for drawing.
            # Assume that TILESIZE is 32. If this changes, so long as the sprite stays twice the size
            # of tiles, this should all still work alright.
            self.image = self.my_sprite_sheet.image_at((0,0,TILESIZE*2,TILESIZE*2))
            self.render_offset_vect = (-TILESIZE/2,-TILESIZE/2)
            
            # OBJECT STATES -----------
            # These control the behavior of the object. Correspond to index in Animation data
            self.STANDING = 0
            self.WALKING = 1
            self.CROUCHING = 2
            self.JUMPING = 3
            self.FIRING_HORIZ = 4
            self.FIRING_DOWN = 5
            self.FIRING_UP = 6
            self.DAMAGED = 7
            self.POGO_DOWN = 8
            self.POGO_UP = 9
            self.FIRING_BUBBLE = 10
            self.DYING = 11
            self.DASHING = 12
            self.WARPING = 13
            self.ROTATE_BARREL_UP = 14
            self.BARREL_UP = 15
            self.JUMP_WINDUP = 16
        
            # Starting State
            self.behavior_state = self.STANDING
            self.state_counter = 0
            
            # ANIMATION -----------
            # These control the animation state of the object.
            # Animations are indexed to the same number as the STATE of the object.
            # I can forsee some objects where the animation_state is not the same as the
            # behavior_state; but for player objects, they'll be the same.
            # Each tuple is: (start_frame, number of frames, animation speed)
            self.ANIM_START=0
            self.ANIM_FRAMES=1
            self.ANIM_SPEED=2
            self.animation_data = [
                [0,3,15], # STANDING
                [3,4,12], # WALKING
                [7,1,30], # CROUCHING
                [8,1,30], # JUMPING
                [9,3,10], #FIRING_HORIZ
                [12,3,8], #FIRING_DOWN
                [15,3,8], #FIRING_UP
                [18,1,8], #DAMAGED
                [19,1,30], #POGO_DOWN
                [20,1,30], #POGO_UP
                [21,5,20], #FIRING_BUBBLE
                [26,12,10], #DYING
                [38,1,30], #DASHING
                [39,8,10], #WARPING
            ]
            # Starting Animation
            self.animation_state = self.STANDING
            # Variables to control how many frames each state uses and how quickly they animate.
            self.animation_current_frame = 0
            self.animation_counter = 0
            
            # LOCATION -----------
            # Tuple is: (x position, y position, collision size horiz, collision size vert)
            # Note that these are TRUE POSITIONS. The sprite animation may be outside of this.
            self.rect = pygame.Rect(init_x,init_y,TILESIZE,TILESIZE)
            # The direction this sprite is moving is stored in a vector.
            self.vector = list(init_vector)
            # The direction this sprite is FACING when not moving.
            self.facing = RIGHT
            
            # SOUND_EFFECTS -----------
            self.sound_jump = pygame.mixer.Sound("Assets/Sounds/Jump.wav")
            self.sound_death= pygame.mixer.Sound("Assets/Sounds/Death.wav")
            self.sound_pellet_fire = pygame.mixer.Sound("Assets/Sounds/pellet_fire.wav")
         # =======================
         # End of Soldier Setup
        
        # TANK SETUP
        # =================================
        if(self.name == "tank"):
            
            # GRAPHICS SETUP ------------        
            # Instead of loading an image directly we will use the
            # spritesheet object, defined below. 
            self.my_sprite_sheet = Sprite_Sheet("Assets\Graphics\Player\Tank.png")
            # The sprites on the sprite sheet are 64x64, but only the middle 32x32 is checked
            # for collision. Need to keep track of the offset for the top left corner for drawing.
            # Assume that TILESIZE is 32. If this changes, so long as the sprite stays twice the size
            # of tiles, this should all still work alright.
            self.image = self.my_sprite_sheet.image_at((0,0,TILESIZE*5,TILESIZE*2.5))
            self.render_offset_vect = (-TILESIZE,-TILESIZE/2)
            
            # OBJECT STATES -----------
            # These control the behavior of the object. Correspond to index in Animation data
            self.STANDING = 0
            self.WALKING = 1
            self.CROUCHING = 2
            self.JUMPING = 3
            self.FIRING_HORIZ = 4
            self.FIRING_DOWN = 5
            self.FIRING_UP = 6
            self.DAMAGED = 7
            self.POGO_DOWN = 8
            self.POGO_UP = 9
            self.FIRING_BUBBLE = 10
            self.DYING = 11
            self.DASHING = 12
            self.WARPING = 13
            self.ROTATE_BARREL_UP = 14
            self.BARREL_UP = 15
            self.JUMP_WINDUP = 16
             
            # Starting State
            self.behavior_state = self.STANDING
            self.state_counter = 0
            
            # ANIMATION -----------
            # These control the animation state of the object.
            # Animations are indexed to the same number as the STATE of the object.
            # I can forsee some objects where the animation_state is not the same as the
            # behavior_state; but for player objects, they'll be the same.
            # Each tuple is: (start_frame, number of frames, animation speed)
            self.ANIM_START=0
            self.ANIM_FRAMES=1
            self.ANIM_SPEED=2
            self.animation_data = [
                [0,1,99], # STANDING
                [11,4,10], # WALKING
                [8,2,10], # CROUCHING
                [10,1,99], # JUMPING
                [15,5,10], #FIRING_HORIZ
                [0,1,99], #FIRING_DOWN
                [3,5,10], #FIRING_UP
                [0,1,99], #DAMAGED
                [0,1,99], #POGO_DOWN
                [0,1,99], #POGO_UP
                [0,1,99], #FIRING_BUBBLE
                [0,1,99], #DYING
                [0,1,99], #DASHING
                [0,1,90], #WARPING
                [1,2,15], #ROTATE_BARREL_UP
                [2,1,99], #ROTATE_BARREL_UP
                [8,2,10], #JUMP WINDUP
            ]
            # Starting Animation
            self.animation_state = self.STANDING
            # Variables to control how many frames each state uses and how quickly they animate.
            self.animation_current_frame = 0
            self.animation_counter = 0
            
            # LOCATION -----------
            # Tuple is: (x position, y position, collision size horiz, collision size vert)
            # Note that these are TRUE POSITIONS. The sprite animation may be outside of this.
            self.rect = pygame.Rect(init_x,init_y,TILESIZE*(1.75),TILESIZE*(1.75))
            # The direction this sprite is moving is stored in a vector.
            self.vector = list(init_vector)
            # The direction this sprite is FACING when not moving.
            self.facing = RIGHT
            
            # SOUND_EFFECTS -----------
            self.sound_jump = pygame.mixer.Sound("Assets/Sounds/Jump.wav")
            self.sound_death= pygame.mixer.Sound("Assets/Sounds/Death.wav")
            self.sound_pellet_fire = pygame.mixer.Sound("Assets/Sounds/pellet_fire.wav")
         # =======================
         # End of Tank Setup
        
        # SPAWNING GAME OBJECTS ---------------
        # This object does not have permission to make objects.
        # So, instead, it will announce to the sprite handler when it wants to make something.
        self.wants_to_spawn_sprite = False
        self.type_of_sprite_to_spawn = "none"
        self.name_of_sprite_to_spawn = "none"
        self.coords_of_sprite_to_spawn = [0,0]
        self.vector_of_sprite_to_spawn = [0,0]

    # Class Accessor Methods
    #-----------------------
    # Returns an ordered pair that defines this object's top left
    # corner [0] = x and [1] = y
    def getpos(self):
        temp_x=self.rect.x
        temp_y=self.rect.y
        return [temp_x,temp_y]
    
    # Set the position of this object.
    def setpos(self,new_x,new_y):
        self.rect.x = new_x
        self.rect.y = new_y
        
    # Set the hit points of this object
    def get_hp(self):
        return self.hit_points
    
    # Returns the image of this object
    def draw(self, map_image):
        if(self.i_blink==False):
            map_image.blit(self.image,(self.rect.x+self.render_offset_vect[0],self.rect.y+self.render_offset_vect[1]))

    def change_control_mode(self):
        temp_bool = self.wants_to_change_control_mode
        self.wants_to_change_control_mode = False
        print(temp_bool)
        return temp_bool

    def spawn(self):
        spawn_tuple = [self.wants_to_spawn_sprite, self.type_of_sprite_to_spawn, self.name_of_sprite_to_spawn,self.coords_of_sprite_to_spawn,self.vector_of_sprite_to_spawn]
        self.wants_to_spawn_sprite = False # Clear the spawn boolean so it only makes one 
        return spawn_tuple

    # Used to tell this object where it's partner is; tank versus soldier.
    def assign_partner(self, new_partner):
        partner = new_partner

    # ----------------------
    # Class Methods
    # ----------------------
 
    def tank_jump_effect(self):
        self.wants_to_spawn_sprite = True
        self.type_of_sprite_to_spawn = "effect"
        self.name_of_sprite_to_spawn = "tank_jump"
        self.coords_of_sprite_to_spawn = [self.rect.x,self.rect.y]
        self.vector_of_sprite_to_spawn = [0,0]
        
    def shoot_bullet(self, bullet_name, direction):
        self.wants_to_spawn_sprite = True
        self.type_of_sprite_to_spawn = "player_projectile"
        self.name_of_sprite_to_spawn = bullet_name
        new_x_coord = 0
        new_y_coord = 0
        new_vector = [0,0]
        
        if(bullet_name == "small_bullet"):
            if(direction == UP_LEFT):
                new_x_coord = self.rect.x-TILESIZE
                new_y_coord = self.rect.y-(TILESIZE/2)
                new_vector = [-6,-6]
            elif(direction == UP_RIGHT):
                new_x_coord = self.rect.x+TILESIZE
                new_y_coord = self.rect.y-(TILESIZE/2)                
                new_vector = [6,-6]
            elif(direction == DOWN_LEFT):
                new_x_coord = self.rect.x-TILESIZE
                new_y_coord = self.rect.y+(TILESIZE/2)
                new_vector = [-6,6]
            elif(direction == DOWN_RIGHT):
                new_x_coord = self.rect.x+TILESIZE
                new_y_coord = self.rect.y+(TILESIZE/2)                
                new_vector = [6,6]
            elif(direction == LEFT):
                new_x_coord = self.rect.x-TILESIZE
                new_y_coord = self.rect.y
                new_vector = [-8,0]
            elif(direction == RIGHT):
                new_x_coord = self.rect.x+TILESIZE
                new_y_coord = self.rect.y                
                new_vector = [8,0]              
                
        self.coords_of_sprite_to_spawn = [new_x_coord,new_y_coord]
        self.vector_of_sprite_to_spawn = new_vector
 
    def take_damage(self, damage):
        #Only react if object is not already in i_frames         
        if(self.i_frames<=0):
            
            #Knockback
            if(self.facing == RIGHT): self.vector[0] = -5
            elif(self.facing == LEFT): self.vector[0] = 5
            self.vector[1] = -2
            
            #Set state and i_frames
            self.behavior_state = self.DAMAGED;
            self.i_frames = 60
            self.i_blink_counter = 10
            
            #Reduce hit points
            self.hit_points -= damage

        if(self.hit_points <= 0): self.die()
        
    def die(self):
        # The "die" function just sets the state and prepares death animation.
        # The next update will take care of the rest.
        self.behavior_state = self.DYING
        self.animation_state = self.DYING
        self.state_counter = 0
        self.animation_counter = 0
        
    def apply_input(self, keys):
        
        # See if we need to change control state
        if(keys[TANK_DOOR] == True):
            self.wants_to_change_control_mode = True
            print("wants to swap!")
        
        # Accelerate left or right based on input
        if(keys[LEFT]) == True:
            self.vector[0] -= 0.2
        elif(keys[RIGHT]) == True:
            self.vector[0] += 0.2
        # If you're on the ground and not pushing a key, deccelerate.
        else: self.vector[0] = 0
        
        # Enforce speed limits
        if(self.name == "soldier"):
            if(self.vector[0] < -2): self.vector[0] = -2       
            if(self.vector[0] > 2): self.vector[0] = 2
        elif(self.name == "tank"):
            if(self.vector[0] < -3): self.vector[0] = -3       
            if(self.vector[0] > 3): self.vector[0] = 3           
        
        # Jump is allowed only after you are on the ground and not jumping for a frame.
        if(self.on_ground == True and keys[JUMP] == False and self.behavior_state != self.JUMP_WINDUP):
           self.has_jumped = False
                
        # Simple jump. You go higher if you hold the jump button.
        if(keys[JUMP] == True):
            if(self.on_ground == True and self.has_jumped == False):
                self.has_jumped = True
                self.holding_jump = True
                # Soldier jumps immediately
                if(self.name == "soldier"):
                    self.vector[1] = -4.5
                    play_sound(self.sound_jump)
                # Tank jump actually starts a short "windup" period before the actual jump
                if(self.name == "tank" and self.behavior_state != self.JUMP_WINDUP):
                    self.behavior_state = self.JUMP_WINDUP
                    self.state_counter = 0
                
        # Tell the object if you stopped holding the jump button after takeoff.
        else: self.holding_jump = False
        # If you're STILL holding it after takeoff, then counteract gravity a bit.
        if (self.holding_jump == True and self.on_ground == False):
            self.vector[1] -= GRAVITY_STRENGTH/2 #If you're still holding jump, counteract gravity a bit.
            
        if(keys[FIRE] == True and self.fire_cooldown <=0 and self.has_fired == False):
            self.has_fired = True
            #self.fire_cooldown = (self.animation_data[self.FIRING_UP][self.ANIM_SPEED]*self.animation_data[self.FIRING_UP][self.ANIM_FRAMES])+1
            self.fire_cooldown = 10
            play_sound(self.sound_pellet_fire)
            if(keys[UP] == True):
                self.animation_state = self.FIRING_UP
                if(self.facing == LEFT): self.shoot_bullet("small_bullet",UP_LEFT)
                else: self.shoot_bullet("small_bullet",UP_RIGHT)
            elif(keys[DOWN] == True):
                self.animation_state = self.FIRING_DOWN
                if(self.facing == LEFT): self.shoot_bullet("small_bullet",DOWN_LEFT)
                else: self.shoot_bullet("small_bullet",DOWN_RIGHT)
            else:
                self.animation_state = self.FIRING_HORIZ
                if(self.facing == LEFT): self.shoot_bullet("small_bullet",LEFT)
                else: self.shoot_bullet("small_bullet",RIGHT)
                
        if(keys[FIRE] == True): self.holding_fire = True
        else: self.holding_fire = False

    def apply_gravity(self, tmxdata):
        # Apply gravity by seeing what is on the tile below the player.
        # This is checking the TMX map for custom booleans named "solid"
        # or "platform"

        if(self.name == "soldier"):
            # Check three points under the soldier to ensure good-feeling collision
            tile_to_check1 = get_tile_properties(tmxdata, self.rect.x+1, self.rect.y+self.vector[1]+TILESIZE)
            tile_to_check2 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE/2), self.rect.y+self.vector[1]+TILESIZE)
            tile_to_check3 = get_tile_properties(tmxdata, self.rect.x+TILESIZE-1, self.rect.y+self.vector[1]+TILESIZE)
            if (
            tile_to_check1['solid'] == False and tile_to_check1['platform'] == False and
            tile_to_check2['solid'] == False and tile_to_check2['platform'] == False and
            tile_to_check3['solid'] == False and tile_to_check3['platform'] == False):
                self.on_ground = False
                self.vector[1]+= GRAVITY_STRENGTH
                if(self.vector[1]>4): self.vector[1]=TERMINAL_VELOCITY #speed limit
            else: self.on_ground = True
            
        elif(self.name == "tank"):
            # Tank has to check more areas underneath it because it's a larger sprite. If you don't check enough
            # areas, it will 
            tile_to_check1 = get_tile_properties(tmxdata, self.rect.x+1, self.rect.y+self.vector[1]+TILESIZE*(1.75)+1)
            tile_to_check2 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE), self.rect.y+self.vector[1]+TILESIZE*(1.75)+1)
            tile_to_check3 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE*2), self.rect.y+self.vector[1]+TILESIZE*(1.75)+1)
            tile_to_check4 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE*3)-1, self.rect.y+self.vector[1]+TILESIZE*(1.75)+1)
            if (
            tile_to_check1['solid'] == False and tile_to_check1['platform'] == False and
            tile_to_check2['solid'] == False and tile_to_check2['platform'] == False and
            tile_to_check3['solid'] == False and tile_to_check2['platform'] == False and
            tile_to_check4['solid'] == False and tile_to_check3['platform'] == False):
                self.on_ground = False
                self.vector[1]+= GRAVITY_STRENGTH
                if(self.vector[1]>4): self.vector[1]=TERMINAL_VELOCITY #speed limit
            else: self.on_ground = True          

    def apply_map_data(self, tmxdata):
        
        # Checks for interaction with the map including solidity, spikes, etc.
        
        # Solider Checks --------------------------------
        if(self.name == "soldier"):
            if (self.vector[0] < 0): #moving left
                tile_to_check1 = get_tile_properties(tmxdata, self.rect.x+self.vector[0], self.rect.y+(TILESIZE/4))
                tile_to_check2 = get_tile_properties(tmxdata, self.rect.x+self.vector[0], self.rect.y+(TILESIZE/2))
                tile_to_check3 = get_tile_properties(tmxdata, self.rect.x+self.vector[0], self.rect.y+TILESIZE-1)
                if (tile_to_check1['solid'] == True) or (tile_to_check2['solid'] == True) or (tile_to_check3['solid'] == True):
                    self.vector[0]=0
                    
            if (self.vector[0] > 0): #moving right
                tile_to_check1 = get_tile_properties(tmxdata, self.rect.x+self.vector[0]+TILESIZE, self.rect.y+(TILESIZE/4))
                tile_to_check2 = get_tile_properties(tmxdata, self.rect.x+self.vector[0]+TILESIZE, self.rect.y+(TILESIZE/2))
                tile_to_check3 = get_tile_properties(tmxdata, self.rect.x+self.vector[0]+TILESIZE, self.rect.y+TILESIZE-1)
                if (tile_to_check1['solid'] == True) or (tile_to_check2['solid'] == True) or (tile_to_check3['solid'] == True):
                    self.vector[0]=0
                    
            if (self.vector[1] < 0): #moving up.
                tile_to_check1 = get_tile_properties(tmxdata, self.rect.x+1, self.rect.y+self.vector[1]+(TILESIZE/4))
                tile_to_check2 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE/2), self.rect.y+self.vector[1]+(TILESIZE/4))
                tile_to_check3 = get_tile_properties(tmxdata, self.rect.x+TILESIZE-1, self.rect.y+self.vector[1]+(TILESIZE/4))
                if (tile_to_check1['solid'] == True) or (tile_to_check2['solid'] == True) or (tile_to_check3['solid'] == True):
                    self.vector[1]=0
                    
            # Moving down is a little more complicated. We want to not fall through the floor, but also "snap to" the floor
            # when we land on it. We accomplish this by calculating how much the character needs to move to snap to the next
            # grid location. Note that this assumes solidity is only applicable in full TILESIZE tiles.
            if (self.vector[1] > 0): #moving down
                tile_to_check1 = get_tile_properties(tmxdata, self.rect.x+1, self.rect.y+self.vector[1]+TILESIZE)
                tile_to_check2 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE/2), self.rect.y+self.vector[1]+TILESIZE)
                tile_to_check3 = get_tile_properties(tmxdata, self.rect.x+TILESIZE-1, self.rect.y+self.vector[1]+TILESIZE)
                if (tile_to_check1['solid'] == True) or (tile_to_check2['solid'] == True) or (tile_to_check3['solid'] == True or
                    tile_to_check1['platform'] == True) or (tile_to_check2['platform'] == True) or (tile_to_check3['platform'] == True):
                     snap_to_grid = TILESIZE - (self.rect.y%TILESIZE)
                     self.rect.y += snap_to_grid 
                     self.vector[1]=0
                     self.on_ground = True
                if (tile_to_check1['spike_small'] == True) or (tile_to_check2['spike_small'] == True) or (tile_to_check3['spike_small'] == True):
                     self.take_damage(1)
        # End of Solider Checks
        
        # Tank Checks
        # ---------------------------------
        if(self.name == "tank"):
            if (self.vector[0] < 0): #moving left
                tile_to_check1 = get_tile_properties(tmxdata, self.rect.x+self.vector[0], self.rect.y+(TILESIZE/2))
                tile_to_check2 = get_tile_properties(tmxdata, self.rect.x+self.vector[0], self.rect.y+(TILESIZE))
                tile_to_check3 = get_tile_properties(tmxdata, self.rect.x+self.vector[0], self.rect.y+(TILESIZE*1.75)-1)
                if (tile_to_check1['solid'] == True) or (tile_to_check2['solid'] == True) or (tile_to_check3['solid'] == True):
                    self.vector[0]=0
                    
            if (self.vector[0] > 0): #moving right
                tile_to_check1 = get_tile_properties(tmxdata, self.rect.x+self.vector[0]+(TILESIZE*3), self.rect.y+(TILESIZE/2))
                tile_to_check2 = get_tile_properties(tmxdata, self.rect.x+self.vector[0]+(TILESIZE*3), self.rect.y+(TILESIZE))
                tile_to_check3 = get_tile_properties(tmxdata, self.rect.x+self.vector[0]+(TILESIZE*3), self.rect.y+(TILESIZE*1.75)-1)
                if (tile_to_check1['solid'] == True) or (tile_to_check2['solid'] == True) or (tile_to_check3['solid'] == True):
                    self.vector[0]=0
                    
            # Again, tank is much wider than the solider. Needs to check more locations when moving vertically
            if (self.vector[1] < 0): #moving up.
                tile_to_check1 = get_tile_properties(tmxdata, self.rect.x+1, self.rect.y+self.vector[1]+(TILESIZE/4))
                tile_to_check2 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE), self.rect.y+self.vector[1]+(TILESIZE/4))
                tile_to_check3 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE*2), self.rect.y+self.vector[1]+(TILESIZE/4))
                tile_to_check4 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE*3)-1, self.rect.y+self.vector[1]+(TILESIZE/4))
               
                if (tile_to_check1['solid'] == True) or (tile_to_check2['solid'] == True) or (tile_to_check3['solid'] == True) or (tile_to_check4['solid'] == True):
                    self.vector[1]=0
                    
            # Moving down is a little more complicated. We want to not fall through the floor, but also "snap to" the floor
            # when we land on it. We accomplish this by calculating how much the character needs to move to snap to the next
            # grid location. Note that this assumes solidity is only applicable in full TILESIZE tiles.
            if (self.vector[1] > 0): #moving down
                tile_to_check1 = get_tile_properties(tmxdata, self.rect.x+1, self.rect.y+self.vector[1]+TILESIZE*(1.75)+1)
                tile_to_check2 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE), self.rect.y+self.vector[1]+TILESIZE*(1.75)+1)
                tile_to_check3 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE*2), self.rect.y+self.vector[1]+TILESIZE*(1.75)+1)
                tile_to_check4 = get_tile_properties(tmxdata, self.rect.x+(TILESIZE*3)-1, self.rect.y+self.vector[1]+TILESIZE*(1.75)+1)
                if ((tile_to_check1['solid'] == True) or (tile_to_check2['solid'] == True) or
                   (tile_to_check3['solid'] == True) or (tile_to_check4['solid'] == True) or
                   (tile_to_check1['platform'] == True) or (tile_to_check2['platform'] == True) or
                   (tile_to_check3['platform'] == True) or (tile_to_check4['platform'] == True)):
                         #snap_to_grid = TILESIZE - (self.rect.y%TILESIZE)
                         #self.rect.y += snap_to_grid
                         self.vector[1]=0
                         self.rect.y += 1
                         self.on_ground = True
                if ((tile_to_check1['spike_large'] == True) or (tile_to_check2['spike_large'] == True) or
                   (tile_to_check3['spike_large'] == True) or (tile_to_check4['spike_large'] == True)):
                         self.take_damage(1)
        
    def update_animation_state(self):
        # Using the sprites current situation, determine what the necessary
        # animation state is supposed to be.
        
        if(self.behavior_state == DYING):
            # Insert dying animation here
            if(self.state_counter >= self.animation_data[DYING][ANIM_SPEED]*self.animation_data[DYING][ANIM_FRAMES]):
                self.animation_state = DEAD
      
        elif(self.fire_cooldown<=0):
            
            if(self.behavior_state == self.JUMP_WINDUP and self.state_counter == 0):
                self.animation_state = JUMP_WINDUP
                self.animation_counter = 0
                self.animation_current_frame = 1
                
            elif(self.on_ground==True):
                if(self.vector[0] < 0):
                    self.facing = LEFT
                    self.animation_state = self.WALKING
                elif(self.vector[0] > 0):
                    self.facing = RIGHT
                    self.animation_state = self.WALKING
                else:
                    self.animation_state = self.STANDING
                    
            elif(self.on_ground==False):
                if(self.vector[0] < 0):
                    self.facing = LEFT
                    self.animation_state = self.JUMPING
                elif(self.vector[0] > 0):
                    self.facing = RIGHT
                    self.animation_state = self.JUMPING
                elif(self.vector[0]==0):
                    self.animation_state = self.JUMPING
        
    def update_animation_frame(self):
        
        # Calculate the current animation offset frame.
        self.animation_counter += 1
        if(self.animation_counter > self.animation_data[self.animation_state][self.ANIM_SPEED]):
            self.animation_current_frame += 1
            self.animation_counter = 0
        if(self.animation_current_frame >= self.animation_data[self.animation_state][self.ANIM_FRAMES]):
           self.animation_current_frame = 0 
        
        if(self.name == "soldier"):
            frame_adjustment = self.animation_data[self.animation_state][self.ANIM_START] * TILESIZE * 2
            frame_adjustment += self.animation_current_frame * TILESIZE * 2
            self.image = self.my_sprite_sheet.image_at((frame_adjustment,0,TILESIZE*2,TILESIZE*2)).convert_alpha()
            
        elif(self.name == "tank"):
            frame_adjustment = self.animation_data[self.animation_state][self.ANIM_START] * TILESIZE * 5
            frame_adjustment += self.animation_current_frame * TILESIZE * 5
            self.image = self.my_sprite_sheet.image_at((frame_adjustment,0,TILESIZE*5,TILESIZE*2.5)).convert_alpha()
            
        # IFRAMES
        # Blinking when you're damaged.
        if(self.i_frames>0):
            if(self.i_blink_counter<=0):
                if(self.i_blink==False):
                    self.i_blink=True
                    self.i_blink_counter=3
                else:
                    self.i_blink=False
                    self.i_blink_counter=3
            else: self.i_blink_counter -= 1

        # Image will be facing left by default, because that is how it is
        # draw. Flip it depending on direction.
        # Note that we don't use .self here. Why? B'c this is a global constant
        # coming from our constants file, not a class constant!
        if self.facing == RIGHT:
            # The flip function has three parameters: source image,
            # whether to flip horizonal, whether to flip vertical
            # Here, we flip horizontaly if facing left.
            self.image = pygame.transform.flip(self.image, True, False)
    
    # -----------------------                    
    # Update Method
    # ----------------------=
    def update(self, tmxdata, keys):
    
        # DYING STATE ------------------
        if(self.behavior_state == DYING) or (self.behavior_state == DEAD):
            self.vector[0] = 0

        # IN ALL STATES ---------------
        
        # Decrement firing cooldown
        if(self.fire_cooldown>0):
            self.fire_cooldown -= 1
        elif(self.has_fired == True and self.holding_fire == False):
            self.has_fired = False
            
        # Tank jumping windup concluded, results in a jump
        if(self.name == "tank"):
            if(self.behavior_state == self.JUMP_WINDUP):
                if(self.state_counter > self.animation_data[self.JUMP_WINDUP][self.ANIM_FRAMES]*self.animation_data[self.JUMP_WINDUP][self.ANIM_FRAMES]):
                    self.behavior_state = self.JUMPING
                    self.vector[1] = -6
                    play_sound(self.sound_jump)
                    self.tank_jump_effect()
                self.state_counter += 1
        
        # Decrement i frames
        if(self.i_frames>0): self.i_frames -= 1
        else: self.i_blink = False
        
        # Die if out of hp
        if(self.hit_points <= 0): self.die

        # Using the map data, modify movement according to situation.
        self.apply_gravity(tmxdata)
        self.apply_map_data(tmxdata)
                   
        # Update position based on vector
        self.rect.x = self.rect.x + self.vector[0]
        self.rect.y = self.rect.y + self.vector[1]
            
        # Update animation state and frame
        self.update_animation_state()
        self.update_animation_frame()    
           
# ============================================
# ==      PLAYER_PROJECTILE CLASS           ==
# ============================================
# This class handles projectiles fired by the
# player. They collide with enemies or certain
# objects on the map.

class Player_projectile(pygame.sprite.Sprite):
    
    def __init__(self,new_name,init_x,init_y,init_vector):
        
        # Call the init function of the sprite class from which this inherets.
        pygame.sprite.Sprite.__init__(self)
        self.name = new_name
         
        # GRAPHICS SETUP ------------        
        # Load the proper graphics for this kind of projectile
        if(self.name == "small_bullet"):
            self.my_sprite_sheet = Sprite_Sheet("Assets\Graphics\Projectiles\small_bullet.png")
            
        self.image = self.my_sprite_sheet.image_at((0,0,TILESIZE*2,TILESIZE*2))

        # As we set initial condition, understand the spawn point is going to be up
        # and to the right of where the initial x and y are because this is a larger sprite
        # And, remember, the Rect arguments are (x,y,h,w), not x1,y1 and x2,y2!
        self.rect = pygame.Rect(init_x-TILESIZE/2,init_y-TILESIZE/2,TILESIZE*2,TILESIZE*2)
        
        # Set up initial velocity
        self.vector = list(init_vector)
        
        # ANIMATION SETUP-----------
        # Starting Animation
        self.animation_state = 0
        # Variables to control how many frames each state uses and how quickly they animate.
        self.animation_current_frame = 0
        self.animation_counter = 0

        # These control the animation state of the object.
        # Animations are indexed to the same number as the STATE of the object.
        # I can forsee some objects where the animation_state is not the same as the
        # behavior_state; but for player objects, they'll be the same.
        # Each tuple is: (start_frame, number of frames, animation speed)
        self.ANIM_START=0
        self.ANIM_FRAMES=1
        self.ANIM_SPEED=2
        
        if(self.name == "small_bullet"):
            self.animation_data = [
                [0,2,8] # ACTIVE
            ]
            
        # MECHANICS SETUP
        self.ALIVE = 1
        self.behavior_state = self.ALIVE
        
        if(self.name == "small_bullet"):
            self.power = 1
            self.lifespan = 30
           
    # Returns the image of this object
    def draw(self, map_image):
        map_image.blit(self.image,(self.rect.x,self.rect.y))
        
    def update_animation(self):

        #All that the effect does is cycle through its animation and then die.
        self.animation_counter += 1
        if(self.animation_counter > self.animation_data[self.animation_state][self.ANIM_SPEED]):
            self.animation_counter = 0
            self.animation_current_frame += 1
        if(self.animation_counter > self.animation_data[self.animation_state][self.ANIM_FRAMES]):
            self.animation_current_frame = 0
        self.image = self.my_sprite_sheet.image_at((self.animation_current_frame*TILESIZE*2,0,TILESIZE*2,TILESIZE*2)).convert_alpha()
  
    def update(self):
        
        # Update position based on vector
        self.rect.x = self.rect.x + self.vector[0]
        self.rect.y = self.rect.y + self.vector[1]
        
        # Update the animation
        self.update_animation()
        
        # Decrement lifespan
        self.lifespan -= 1
        
        # Eliminate once dead
        if(self.lifespan <= 0):
            self.behavior_state = DEAD
            

class Effect(pygame.sprite.Sprite):
    
    def __init__(self,new_name,init_x,init_y,new_facing):
        
        # Call the init function of the sprite class from which this inherets.
        pygame.sprite.Sprite.__init__(self)
        self.name = new_name
         
        # GRAPHICS SETUP ------------        
        # Load the proper graphics for this kind of projectile
        if(self.name == "pellet_burst"):
            self.my_sprite_sheet = Sprite_Sheet("Assets\Graphics\Effects\pellet_burst.png")
            self.image = self.my_sprite_sheet.image_at((0,0,TILESIZE*2,TILESIZE*2))
            self.rect = pygame.Rect(init_x-TILESIZE/2,init_y-TILESIZE/2,TILESIZE*2,TILESIZE*2)
        if(self.name == "tank_jump"):
            self.my_sprite_sheet = Sprite_Sheet("Assets\Graphics\Effects\jumpy.png")
            self.image = self.my_sprite_sheet.image_at((0,0,TILESIZE*4,TILESIZE*4))
            self.rect = pygame.Rect(init_x-TILESIZE/2,init_y-TILESIZE/2,TILESIZE*4,TILESIZE*4)

        # As we set initial condition, understand the spawn point is going to be up
        # and to the right of where the initial x and y are because this is a larger sprite
        # And, remember, the Rect arguments are (x,y,h,w), not x1,y1 and x2,y2!
        
        self.facing = new_facing
        
        # ANIMATION SETUP-----------
        # Starting Animation
        self.animation_state = 0
        # Variables to control how many frames each state uses and how quickly they animate.
        self.animation_current_frame = 0
        self.animation_counter = 0

        # These control the animation state of the object.
        # Animations are indexed to the same number as the STATE of the object.
        # I can forsee some objects where the animation_state is not the same as the
        # behavior_state; but for player objects, they'll be the same.
        # Each tuple is: (start_frame, number of frames, animation speed)
        self.ANIM_START=0
        self.ANIM_FRAMES=1
        self.ANIM_SPEED=2
        
        if(self.name == "pellet_burst"):
            self.animation_data = [
                [0,6,3] # ACTIVE
            ]
            self.lifespan = self.animation_data[self.animation_state][self.ANIM_FRAMES] * self.animation_data[self.animation_state][self.ANIM_SPEED]
        if(self.name == "tank_jump"):
            self.animation_data = [
                [0,6,3] # ACTIVE
            ]
            self.lifespan = self.animation_data[self.animation_state][self.ANIM_FRAMES] * self.animation_data[self.animation_state][self.ANIM_SPEED]
                       
        # MECHANICS SETUP
        self.ALIVE = 1
        self.behavior_state = self.ALIVE
        
        print("new effect spawned:")
        print(self.name)
        
    # Returns the image of this object
    def draw(self, map_image):
        print("drawing effect")
        map_image.blit(self.image,(self.rect.x,self.rect.y))
            
    def update(self):
        #All that the effect does is cycle through its animation and then die.
        self.animation_counter += 1
        if(self.animation_counter > self.animation_data[self.animation_state][self.ANIM_SPEED]):
            self.animation_counter = 0
            self.animation_current_frame += 1
        
        if(self.name == "pellet_burst"):
            self.image = self.my_sprite_sheet.image_at((self.animation_current_frame*TILESIZE*2,0,TILESIZE*2,TILESIZE*2)).convert_alpha()
        elif(self.name == "tank_jump"):
            self.image = self.my_sprite_sheet.image_at((self.animation_current_frame*TILESIZE*4,0,TILESIZE*4,TILESIZE*4)).convert_alpha()
        if(self.facing == RIGHT): 
            self.image = pygame.transform.flip(self.image, True, False)
            
        self.lifespan -= 1
        if(self.lifespan <= 0): self.behavior_state = DEAD

# ============================================
# ==                 HUD                    ==
# ============================================
# HUD is the object that stores things that
# get drawn on top of the screen, like life bars.

class Hud(object):
    
    def __init__(self):
        
         # Call the init function of the sprite class from which this inherets.
        pygame.sprite.Sprite.__init__(self)
        
        # GRAPHICS SETUP ------------        
        # Instead of loading an image directly we will use the
        # spritesheet object, defined below. 
        self.lifebar_sprite_sheet = Sprite_Sheet("Assets\Graphics\HUD\Heart.png")

        # Now we will initially set the image of this sprite
        # to be the first image on the sprite sheet.
        # Why do we use two paratheses? Because the .image_at function
        # expects to get a single parameter: an array of 4 numbers.
        self.lifebar_image = self.lifebar_sprite_sheet.image_at((0,0,16,16))

        # Name. This game object needs a name so others can identify it.
        self.name = "HUD"
        # Starting hit points to display
        self.hit_points = 4
    
    def update(self, player_life):
        
        self.hit_points = player_life
        
    def draw(self):
        
        lifebar = pygame.Surface((16,16))
        lifebar = pygame.transform.scale(lifebar,(16*self.hit_points,16))
        for i in range(0,self.hit_points):
            lifebar.blit(self.lifebar_image,(16*i,0))
        lifebar.convert_alpha()
        return lifebar
        
    