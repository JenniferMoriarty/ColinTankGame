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
import random

#Import functions that let us read and write
#to .tmx files, which are what Tiled Map Editor
#creates. If you don't have pytmx, it can be
#added from within Thonny under Tools->Manage Packages.
import pytmx
#Share one of pytmx's methods.Note that we're not using
#the * function this time, so the only methods that
#get imported are those we expressly name.
from pytmx.util_pygame import load_pygame

#Import other game files. These are in the same
#directory as Notmario and exist basically to help
#organize the code.
import methods
#Again, need to expressly share the methods to which
#we want to have access.
from methods import blit_all_tiles
from methods import get_tile_properties
from methods import play_sound

#This file contains CONSTANTS. Technically, Python does
#not have a "constant" variable type. But, we just use
#regular old variables and treat them as constants. To
#remind us not to change them, we name them in all caps.
import constants
#More bad practice importing all of constant
from constants import *

#Import the game classes
import game_objects

# ============================================
# ==             C A M E R A                ==
# ============================================

class Camera(object):
    
    def __init__ (self):
        
        # The (x,y) coordinates of the camera. Measured from the CENTER!
        # NOT MEASURED FROM TOP LEFT!
        self.x = 100
        self.y = 300
        
        # A pointer to the sprite the camera is following
        self.following = pygame.sprite
        # The (x,y) coordinates that the camera wants to move towards.
        self.target_x = 0
        self.target_y = 0
        
        self.zoom = STARTING_CAMERA_ZOOM
        self.target_zoom = 1
        self.view_width = SCREEN_W
        self.view_height = SCREEN_H
        
        self.camera_speed = 2
        
        self.camera_scaled = pygame.Surface

    def change_follow(self, target_sprite):

        self.following = target_sprite
        target_coords = self.following.getpos()
        self.target_x = target_coords[0]
        self.target_y = target_coords[1]
    
    def change_zoom(self, new_target_zoom):
        
        self.target_zoom = new_target_zoom
    
    def snap_to_target(self):

        target_coords = self.following.getpos()
        self.target_x = target_coords[0]
        self.target_y = target_coords[1]
        
        self.x = self.target_x
        self.y = self.target_y
        
    def snap_to_coords(self, new_x, new_y):
        
        self.x = new_x
        self.y = new_y
        
    def update(self, map_width, map_height, keys):
        
        #Change zoom based on keys
        if(self.zoom > self.target_zoom): self.zoom -= 1
        elif(self.zoom < self.target_zoom): self.zoom += 1
            
        #Determine size of camera view based on zoom.
        self.view_width = SCREEN_W/self.zoom
        self.view_height = SCREEN_H/self.zoom
        
        # Move towards the sprite target
        # Currently, assumes that the sprite is one tile wide.
        target_coords = self.following.getpos()
        self.target_x = target_coords[0]
        self.target_y = target_coords[1]       
        
        if(self.x < (self.target_x+TILESIZE/2)): self.x += self.camera_speed
        if(self.x > (self.target_x+TILESIZE/2)): self.x -= self.camera_speed   
        if(self.y < (self.target_y+TILESIZE/2)): self.y += self.camera_speed
        if(self.y > (self.target_y+TILESIZE/2)): self.y -= self.camera_speed
        
        # Don't show area outside the map. This varies depending on size of window.
        if(self.x<self.view_width/2):
            self.x = self.view_width/2
        if(self.x>map_width-(self.view_width/2)):
            self.x = map_width-(self.view_width/2)
        if(self.y<self.view_height/2):
            self.y = self.view_height/2
        if(self.y>map_height-(self.view_height/2)):
            self.y = map_height-(self.view_height/2)

    def draw(self,pre_render_image):
        
        # Figure out how much of map image to draw based on zoom
        # We're looking at how much of the map we want to actually see.
        x1 = self.x - self.view_width/2
        y1 = self.y - self.view_height/2
        x2 = self.view_width
        y2 = self.view_height
        
        # Now, calculate round integers. We're about to make a temporary
        # image that is exactly as large as the section of the screen
        # that we want to display. Pygame surfaces only use integers, so
        # we need to round off the view sizes, which can be floats.
        approx_width = round(self.view_width,0)
        approx_height = round(self.view_height,0)
        # Create a temporary image just big enough for the part of the map we want.
        camera_view = pygame.Surface((approx_width,approx_height))
        
        # Grab the portion of the map_image caculated by the zoom and load it
        # into our custom-sized image.
        camera_view.blit( (pre_render_image), #Start with the pre-render image
                               (0,0), # draw it to the camera starting at corner 0,0
                               (x1,y1,x2,y2) # Draw the section at the camera view            
            )

        # Lastly, scale the image back to match the size of the screen showing to
        # the player.
        self.camera_scaled = pygame.transform.smoothscale(camera_view, (SCREEN_W, SCREEN_H))
        
        self.camera_scaled.convert
        return self.camera_scaled

            
    