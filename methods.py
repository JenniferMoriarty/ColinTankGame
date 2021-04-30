# ======================================
# ==          I M P O R T S           ==
# ======================================
# Tell main where to find the libraries
# and other game code. It will search in
# this directory and in Thonny's directory.

#Import Pygame
import pygame
#Share all of Pygame's methods and variables
#so we can use them here without worrying about
#telling the code to look in pygame for them
#each time. I think. People online suggest that
#using the * function like this is generally bad
#practice because it makes confusing code when
#different files freely share their internal data.
from pygame.locals import *

# Import math functions
import math

#Import functions that let us read and write
#to .tmx files, which are what Tiled Map Editor
#creates. If you don't have pytmx, it can be
#added from within Thonny under Tools->Manage Packages.
import pytmx
#Share one of pytmx's methods.Note that we're not using
#the * function this time, so the only methods that
#get imported are those we expressly name.
from pytmx.util_pygame import load_pygame

#This file contains CONSTANTS. Technically, Python does
#not have a "constant" variable type. But, we just use
#regular old variables and treat them as constants. To
#remind us not to change them, we name them in all caps.
import constants
#More bad practice importing all of constant
from constants import *

# ============================================
# ==            GLOBAL METHODS              ==
# ============================================

#Play a sound
#--------------------------------

def play_sound(sound_to_play):
    pygame.mixer.Sound.play(sound_to_play)
    
#Load a new Tiled Map. Returns the new map.
#Also tells sprite handler to update sprite information
#--------------------------------
def load_new_map(map_name, sprite_handler, entrance_direction):

    #Clear sprites
    sprite_handler.prepare_for_new_map()
    
    #Map - This is loading the Tiled Map Editor map we used.
    tmxdata = load_pygame(map_name, pixelalpha=True)
    
    #Adjust sprites for new map
    sprite_handler.spawn_sprites_from_map(tmxdata)
    sprite_handler.player_enters_map(tmxdata, entrance_direction)

    return tmxdata

#Load a new Tiled Map. Returns the new map.
# Does NOT tell the Sprite Handler to do anything.
#--------------------------------
def preview_new_map(map_name):

    #Map - This is loading the Tiled Map Editor map we used.
    tmxdata = load_pygame(map_name, pixelalpha=True)
    return tmxdata

#Load a new map image based on currently loaded Tiled Map. Returns image.
#------------------------------
def load_map_image(tmxdata):
    map_width = tmxdata.width * TILESIZE
    map_height = tmxdata.height * TILESIZE
    map_image =  pygame.Surface((map_width, map_height))
    return map_image

#Draw the Tiled Map to the Screen
#--------------------------------
def blit_all_tiles(window, tmxdata, screen_offset):

    for layer in tmxdata.visible_layers:
        # Game will crash if we try to blit the object layer, so make sure we're
        # not doing that. Make sure it's a Tile Layer instead.
        if isinstance(layer, pytmx.TiledTileLayer):
            for tile in layer.tiles():
                #tiles[0] = z grid location
                #tiles[1] = y grid location
                #tiles[2] = image data for blitting
                x_pixel = tile[0] * TILESIZE + screen_offset[0]
                y_pixel = tile[1] * TILESIZE + screen_offset[1]
                window.blit( tile[2], (x_pixel, y_pixel))
            
#Get Tile Properties
#------------------------------
def get_tile_properties(tmxdata, x_to_check, y_to_check):
    
    world_x = x_to_check;
    world_y = y_to_check;
    tile_x = world_x // TILESIZE
    tile_y = world_y // TILESIZE
    
    # We need some error correction. What happens if the code asks for a tile
    # that is off the map? Let's supply some default information so we dont crash.
    try:
        properties = tmxdata.get_tile_properties(tile_x, tile_y, BLOCK_LAYER)
    except Exception:
        print("exception thrown; cant find tile data")
        properties = {"solid":True,"platform":False}
    # Also supply defaults if there are no properties at all, for some reason.
    if properties is None:
        print("exception thrown; no properties found")
        properties = {"solid":True,"platform":False}
    return properties

#-------------------------------
#Screen Transition
#-------------------------------

def get_landing_coords(tmxdata, direction):
     # Look for the screen entrance objects
        for tile_object in tmxdata.objects:
            if(tile_object.name == 'entrance' and tile_object.properties["dir"] == direction):
                return (tile_object.x,tile_object.y)
        
        # Default return top left corner if nothing located.
        print("No entrance location found moving" + direction)
        return (0,0)

def create_transition_screen(tmxdata1, #The first map, and the camera's loc 
                       tmxdata2, #The second map, and where the camera needs to go
                       new_camera_x, new_camera_y, # The coords on the new map where the camera should be
                       direction_to_scroll, #Which way are we scrolling; UP, DOWN, LEFT, or RIGHT.
                       game_camera,#The camera objects
                       keys): # b'c camera needs this to update
    
    # Save an image of the existing map.
    old_map_image = load_map_image(tmxdata1)
    blit_all_tiles(old_map_image, tmxdata1, (0,0))
    old_map_width = tmxdata1.width*TILESIZE 
    old_map_height = tmxdata1.height*TILESIZE
    old_map_screen = pygame.Surface((SCREEN_W,SCREEN_H))
    old_map_screen.blit(game_camera.draw(old_map_image),(0,0))
    
    # Save an image of the new map at same zoom, focused on the new coordinates passed to this method.
    new_map_image = load_map_image(tmxdata2)
    blit_all_tiles(new_map_image, tmxdata2, (0,0))
    new_map_width = tmxdata2.width*TILESIZE 
    new_map_height = tmxdata2.height*TILESIZE
    game_camera.snap_to_coords(new_camera_x, new_camera_y)
    game_camera.update(new_map_width,new_map_height,keys)
    new_map_screen = pygame.Surface((SCREEN_W,SCREEN_H))
    new_map_screen.blit(game_camera.draw(new_map_image),(0,0))
     
    # Create a composite image based on the direction
    
    composite_screen = pygame.Surface((SCREEN_W,SCREEN_H))

    if(direction_to_scroll == LEFT):
        composite_screen = pygame.transform.smoothscale(composite_screen, (SCREEN_W*2,SCREEN_H))
        print(composite_screen)
        composite_screen.blit(new_map_screen,(0,0))
        composite_screen.blit(old_map_screen,(SCREEN_W,0)) 
    elif(direction_to_scroll == RIGHT):
        composite_screen = pygame.transform.smoothscale(composite_screen, (SCREEN_W*2,SCREEN_H))
        print(composite_screen)
        composite_screen.blit(old_map_screen,(0,0))
        composite_screen.blit(new_map_screen,(SCREEN_W,0))  
    elif(direction_to_scroll == UP):
        composite_screen = pygame.transform.smoothscale(composite_screen, (SCREEN_W,SCREEN_H*2))
        print(composite_screen)
        composite_screen.blit(new_map_screen,(0,0))
        composite_screen.blit(old_map_screen,(0,SCREEN_H)) 
    elif(direction_to_scroll == DOWN):
        composite_screen = pygame.transform.smoothscale(composite_screen, (SCREEN_W,SCREEN_H*2))
        print(composite_screen)
        composite_screen.blit(old_map_screen,(0,0))
        composite_screen.blit(new_map_screen,(0,SCREEN_H))
        
    #return composite_screen
    return composite_screen

def scroll_transition_screen(composite_image, direction_to_scroll, screen, clock):

    scroll_counter = 0
    image_position_x = 0
    image_position_y = 0
    scroll_limit = 0
    
    if(direction_to_scroll == LEFT or direction_to_scroll == RIGHT):
        scroll_limit = SCREEN_W
    else:
        scroll_limit = SCREEN_H
    
    while scroll_counter < scroll_limit:

        # Moving left? We start at (WIDTH,0) and decrement X.
        if(direction_to_scroll == LEFT):
            if scroll_counter <= 0:
                image_position_x = SCREEN_W
            else:
                image_position_x = SCREEN_W - scroll_counter
                
         # Moving right? We start at (0,0) and increment X.
        elif(direction_to_scroll == RIGHT):
            if scroll_counter <= 0:
                image_position_x = 0
            else:
                image_position_x = scroll_counter
                
         # Moving up? We start at (0,HEIGHT) and decrement Y.
        elif(direction_to_scroll == UP):
            if scroll_counter <= 0:
                image_position_y = SCREEN_H
            else:
                image_position_y = SCREEN_H - scroll_counter
                
        # Moving up? We start at (0,0) and increment Y.
        elif(direction_to_scroll == DOWN):
            if scroll_counter <= 0:
                image_position_y = 0
            else:
                image_position_y = scroll_counter   
    
        # Display the proper part of the composite screen image
        screen.fill(0)
        screen.blit(composite_image, (0,0), (image_position_x,image_position_y,SCREEN_W,SCREEN_H))

        #Update the screen
        pygame.display.flip()
        
        # Set the game to run at 60fps
        clock.tick(60)
        
        scroll_counter = scroll_counter + 40
    

#-------------------------------
# Menus
#-------------------------------

def main_menu(screen, clock, myfont):
    
    menu_running = True
    
    while menu_running:
        
        screen.fill((0,0,0)) # Fill screen with black
        
        # Draw title of menu to screen
        textsurface = myfont.render('NOT MARIO', True, (255,255,255))
        screen.blit(textsurface,(SCREEN_W/3,SCREEN_H/9))
        
        textsurface = myfont.render('A Game To Play', True, (255,255,255))
        screen.blit(textsurface,(SCREEN_W/3.2,SCREEN_H/6))
        
        mx, my = pygame.mouse.get_pos()
        
        button_1 = pygame.Rect(SCREEN_W/3,SCREEN_H/3,200,50)           
        button_2 = pygame.Rect(SCREEN_W/3,SCREEN_H/2,200,50)
                  
        if button_1.collidepoint((mx,my)):
            if click:
                menu_running = False
        if button_2.collidepoint((mx,my)):
            if click:
                menu_running = False
                
        pygame.draw.rect(screen, (255,0,0), button_1)
        textsurface = myfont.render('Begin', True, (255,255,255))
        screen.blit(textsurface,(SCREEN_W/3+20,SCREEN_H/3))
        
        pygame.draw.rect(screen, (255,0,0), button_2)
        textsurface = myfont.render('Nope', True, (255,255,255))
        screen.blit(textsurface,(SCREEN_W/3+20,SCREEN_H/2))
        
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                
        pygame.display.update()
        clock.tick(60)
        
def game_over_menu(screen, clock, myfont):
    
    menu_running = True
    sound_game_over = pygame.mixer.Sound("game_over_yah.wav")
    play_sound(sound_game_over)
    
    while menu_running:
        
        screen.fill((0,0,0)) # Fill screen with black
        
        # Draw title of menu to screen
        textsurface = myfont.render('WHAT DID YOU DO', True, (255,255,255))
        screen.blit(textsurface,(SCREEN_W/3,SCREEN_H/9))
        
        textsurface = myfont.render('P.S. Lost the Game', True, (255,255,255))
        screen.blit(textsurface,(SCREEN_W/3.2,SCREEN_H/6))
        
        mx, my = pygame.mouse.get_pos()
        
        button_1 = pygame.Rect(SCREEN_W/3,SCREEN_H/3,200,50)           
        button_2 = pygame.Rect(SCREEN_W/3,SCREEN_H/2,200,50)
                  
        if button_1.collidepoint((mx,my)):
            if click:
                menu_running = False
        if button_2.collidepoint((mx,my)):
            if click:
                menu_running = False
                
        pygame.draw.rect(screen, (255,0,0), button_1)
        textsurface = myfont.render('Try Again', True, (255,255,255))
        screen.blit(textsurface,(SCREEN_W/3+20,SCREEN_H/3))
        
        pygame.draw.rect(screen, (255,0,0), button_2)
        textsurface = myfont.render('End It', True, (255,255,255))
        screen.blit(textsurface,(SCREEN_W/3+20,SCREEN_H/2))
        
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                
        pygame.display.update()
        clock.tick(60)