# ======================================
# ==          I M P O R T S           ==
# ======================================
# Tell main where to find the libraries
# and other game code. It will search in
# this directory and in Thonny's directory.

#Import Pygame (Library with all the pygame classes and methods)
import pygame

#Make all pygame variables, classes, and methods available without needing to use ".pygame"
#Bad practice to do this generally in imports.
from pygame.locals import *

#Import math functions
import math
import random

#Import OS functions to see directory
import os

#Import Pytmx (Library with all the methods that let us read Tiled maps) 
import pytmx

#Make a specific method from pytmx available without needing to use ".pytmx"
#Better practice than importing everything becuase less chance of conflicts.
from pytmx.util_pygame import load_pygame

#Import global methods. Basically all designed to work with main, so fine to important all of them.
import methods
from methods import *

#Import global constants. Note that these are not REALLY constants and the code
#could change them in theory. In practice, dont. Let me easily switch certain
#values used to run the game.
import constants
from constants import *

#Import game objects. Handles all sprites.
import game_objects
#Import game camera. Handles displaying screen.
import camera

# ============================================
# ==     I N I T I A L I Z A T I O N        ==
# ============================================
# This section sets up the objects and variables
# I will need in the game loop later.

#Screen - This is the game screen we'll see
# in windows.
pygame.init()
width, height = SCREEN_W, SCREEN_H
screen=pygame.display.set_mode((width, height))

#Input - This is an array that will hold
# information about what keys we pressed.
# Keys needed: Up, Down, Left, Right, Jump, Fire, Item, Pause.
keys = [False, False, False, False, False, False, False, False, False]

pygame.joystick.init()
try joystick = pygame.joystick.Joystick(0)
joystick.init()

# Create a new sprite handler object.
sprite_handler=game_objects.Sprite_Handler()

# Set the starting map
current_map = "Maps\Mapdata\Mars05.tmx"
screen_transition = False # A variable to tell us if we're in the middle of transitioning screens.
screen_transition_counter = 0

# Loading a new map and associated information
tmxdata = load_new_map(current_map, sprite_handler, RIGHT) # Load new map and ask Sprite Handler to redo sprites
                                                           # Use "RIGHT" as default entrance tile.
                            
map_width = tmxdata.width*TILESIZE # Save the size of the incoming map
map_height = tmxdata.height*TILESIZE
map_image = load_map_image(tmxdata) # Set up an image size for the new map

loaded_map_image =  pygame.Surface((map_width, map_height)) # Save a copy of the new map's appareance
loaded_oldmap_image = pygame.Surface((SCREEN_W, SCREEN_H)) # Used during screen transitions
loaded_newmap_image = pygame.Surface((SCREEN_W, SCREEN_H)) # Used during screen transitions
blit_all_tiles(loaded_map_image, tmxdata, (0, 0))

# Variables to control the state of the game.
game_state = MAIN_MENU
control_state = SOLDIER_ACTIVE
player_has_died = False
player_death_counter = 0

# Set up the game music track.
current_directory = os.getcwd()
song_to_load = current_directory + '/' + 'Assets/Music/blastermaster.wav'
background_music = pygame.mixer.Sound(song_to_load)
background_music.set_volume(0.25)

# Create a game camera to handle rendering.
game_camera=camera.Camera()
# Tell camera to follow the player sprite
game_camera.change_follow(sprite_handler.get_player(control_state))
game_camera.snap_to_target()

# A variable to track if our code should exit
done = False

# A clock. This will make our game run the same speed regardless of hardware.
clock = pygame.time.Clock()

# Set up the menus
pygame.font.init()
myfont = pygame.font.SysFont('Times New Roman', 30)

# Start music once menu is done
background_music.play(-1)

# Oh boy it's the
# =========================================
# ==        G A M E  L O O P             ==
# =========================================
# This is the main function that runs the game

while(done == False):
    # ----------------------------
    # Updating
    # ----------------------------
    # This section handles the games logic about updating all the
    # "under the hood" information like moving sprites around, checking
    # for input, changing states, etc.
    
    # Check for input in all states.
    
    for event in pygame.event.get():
        
        if event.type==pygame.QUIT:
            done = True
            
        # When I'm changing the keys array, see how I'm using UP, DOWN, LEFT, RIGHT
        # as my indexes? It makes it super easy to understand what each element in the
        # keys array is used for, right? That's why I used them as global constants!
        if event.type == pygame.KEYDOWN:
            if event.key==K_w:
                keys[UP]=True
            elif event.key==K_s:
                keys[DOWN]=True
            elif event.key==K_a:
                keys[LEFT]=True
            elif event.key==K_d:
                keys[RIGHT]=True
            elif event.key==K_SPACE:
                keys[JUMP]=True
            elif event.key==K_g:
                keys[FIRE]=True
            elif event.key==K_h:
                keys[ITEM]=True
            elif event.key==K_ESCAPE:
                keys[PAUSE] = True
                
        if event.type == pygame.KEYUP:
            if event.key==K_w:
                keys[UP]=False
            elif event.key==K_s:
                keys[DOWN]=False
            elif event.key==K_a:
                keys[LEFT]=False
            elif event.key==K_d:
                keys[RIGHT]=False
            elif event.key==K_SPACE:
                keys[JUMP]=False
            elif event.key==K_g:
                keys[FIRE]=False
            elif event.key==K_h:
                keys[ITEM]=False
            elif event.key==K_ESCAPE:
                keys[PAUSE] = False
        
        if event.type == pygame.JOYHATMOTION:
            hat = joystick.get_hat(0)
            if(hat[0] < 0):
                keys[LEFT] = True
                keys[RIGHT] = False
            elif(hat[0] > 0):
                keys[RIGHT] = True
                keys[LEFT] = False
            else:
                keys[RIGHT] = False
                keys[LEFT] = False
            if(hat[1] > 0):
                keys[UP] = True
                keys[DOWN] = False
            elif(hat[1] < 0):
                keys[DOWN] = True
                keys[UP] = False
            else:
                keys[UP] = False
                keys[DOWN] = False
                
        if event.type == pygame.JOYBUTTONDOWN or JOYBUTTONUP:
            if(joystick.get_button(0)):
                keys[JUMP] = True
            else: keys[JUMP] = False
            if(joystick.get_button(2)):
                keys[FIRE] = True
            else: keys[FIRE] = False
            if(joystick.get_button(6)):
                keys[TANK_DOOR] = True
            else: keys[TANK_DOOR] = False
                
    # Main menu state just displays the main menu until the state ends.
    if(game_state == MAIN_MENU):
#         
#         background_music.stop()
#         main_menu(screen, clock, myfont)
          game_state = PLAYING
          background_music.play(-1)
        
    elif(game_state == GAME_OVER):  
        
        background_music.stop()
        game_over_menu(screen, clock, myfont)
        
        # Add code to reload game from save (once save is made)        
        player_has_died = False
        player_death_counter = 0
        sprite_handler.reset_player(tmxdata)
        game_state = PLAYING
        background_music.play(-1)      
        
    # Paused state renders the background and but doesn't update sprites
    elif(game_state == PAUSED):
        
        print("paused!")
        if(keys[PAUSE] == True):
            game_state = PLAYING
            keys[PAUSE] = False

    # Playing state gives control of character        
    elif(game_state == PLAYING):
    
        # Pause if necessary
        if(keys[PAUSE] == True):
            game_state = PAUSED
            keys[PAUSE] = False
    
        # Check to see if we need to load a new map.
        checked_exit_dict = sprite_handler.check_for_map_exit(tmxdata, control_state)
        
        # Save the last image of the map in case we screen transition.
        # Important to do this before we update and redraw next frame.
        loaded_oldmap_image = game_camera.draw(map_image)
        
        # If player is on an exit tile, transition to new screen and start playing there.
        if(checked_exit_dict["dest"] != "none"):
            
            proposed_map = checked_exit_dict["dest"]
            new_tmxdata = preview_new_map(proposed_map) # Load new map and ask Sprite Handler to redo sprites
            landing_coords = get_landing_coords(new_tmxdata, checked_exit_dict["dir"])
            landing_x = landing_coords[0]
            landing_y = landing_coords[1]

            # Convert the direction of the transition to one of the globals. The map data will be in STRING format.
            direction = 0
            if(checked_exit_dict["dir"] == "UP"): direction = UP
            elif(checked_exit_dict["dir"] == "DOWN"): direction = DOWN
            elif(checked_exit_dict["dir"] == "LEFT"): direction = LEFT
            elif(checked_exit_dict["dir"] == "RIGHT"): direction = RIGHT
                             
            # Actually carry out the transition
            composite_screen = create_transition_screen(tmxdata, new_tmxdata,landing_x,landing_y,
                                                        direction,game_camera, keys)
            scroll_transition_screen(composite_screen, direction, screen, clock)
            
            # Load the new map and get ready to play on it.        
            current_map = proposed_map
            tmxdata = load_new_map(current_map, sprite_handler,direction) # Load new map and ask Sprite Handler to redo sprites
            game_camera.snap_to_target()
            map_width = tmxdata.width*TILESIZE # Save the size of the incoming map
            map_height = tmxdata.height*TILESIZE
            map_image = load_map_image(tmxdata) # Set up an image size for the new map
            loaded_map_image =  pygame.Surface((map_width, map_height)) # Save a copy of the new map's appareance
            blit_all_tiles(loaded_map_image, tmxdata, (0, 0))

        # Update game objects
        sprite_handler.update(tmxdata, keys, control_state)
        if(sprite_handler.change_control_mode()):
            if(control_state == TANK_ACTIVE):
                control_state = SOLDIER_ACTIVE
                print("switching to soldier")
            elif(control_state == SOLDIER_ACTIVE):
                control_state = TANK_ACTIVE
                print("switching to tank")
                
        # Check for collisions
        sprite_handler.player_enemy_collision_check(control_state)
        
        # Update the camera
        game_camera.update(map_width,map_height,keys)
        if(control_state == TANK_ACTIVE):
            game_camera.change_follow(sprite_handler.tank)
            game_camera.change_zoom(1)
        elif(control_state == SOLDIER_ACTIVE):
            game_camera.change_follow(sprite_handler.soldier)
            game_camera.change_zoom(3)
            
        # Stop music if player died.
        check_player = sprite_handler.get_player(control_state)
        if check_player.behavior_state == DEAD:
            background_music.stop()
            player_has_died = True
            
        if(player_has_died == True):
            player_death_counter += 1
            if(player_death_counter >= 200): game_state = GAME_OVER
        
    # ----------------------------
    # Rendering (Do this in all states)
    # ----------------------------
    # This section handles actually preparing and drawing the screen
    # based on what the currently updated state of the game is.

    # Build the map_image
    # Note that we're applying camera offsets because, if we draw the whole map at once
    # first, it starts to slow down dramatically.
    map_image.fill(0)
    map_image.blit((loaded_map_image),(0,0))
        
    # Draw sprites on map
    sprite_handler.draw(map_image)
    map_image.convert()
        
    # Draw the right portion of the map to the screen    
    screen.fill(0)
    screen.blit(game_camera.draw(map_image),(0,0))
    screen.blit(sprite_handler.draw_hud(),(16,16))

    # No matter what state we are in, flip the screen.
    #Update the screen
    pygame.display.flip()
    
    # Set the game to run at 60fps
    clock.tick(60)
