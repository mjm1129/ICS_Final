#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 19 20:26:00 2019

@author: lisamoon98
"""

import pygame
import random
import os
import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
from client_state_machine import *
import argparse
from chat_client_class import *


pygame.init()
screen = pygame.display.set_mode((450, 270))
COLOR_INACTIVE = (0, 0, 0)
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font('font/a≈•∫ÍG.otf', 25)

class InputBox():

    def __init__(self, x, y, w, h, which, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.which = which

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    if self.which == 1:
                        self_name = self.text
                    else:
                        partner_name = self.text
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, (0, 0, 0))

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)
        
class game_setting():
    def __init__(self):
        pygame.init() # in case of the settings
        os.getcwd()
        
        # Board info
        self.board_width = 1000
        self.board_height = 650
        self.board_rgb = (209, 224, 229)
        
        self.treeMode = [None] * 11
        self.progressBar = [None] * 11
        
        # Load tree images
        for i in range(11):
            self.treeMode[i] = pygame.image.load("images/treeImage" + str(i) + ".png")
            self.progressBar[i] = pygame.image.load("images/ProgressBar" + str(i) + ".png")
            
        self.childMode = [pygame.image.load("images/player1_childMode1.png"),
                          pygame.image.load("images/player1_childMode2.png"),
                          pygame.image.load("images/player2_childMode1.png"),
                          pygame.image.load("images/player2_childMode2.png")]
        
        self.back_tree = pygame.image.load("images/background_tree.png")
        
        
        self.cursor = pygame.image.load("images/Cursor.png")
        
        # Fonts
        self.instruction_font = pygame.font.Font('font/a≈•∫ÍG.otf', 40) 
        self.progressBar_font = pygame.font.Font('font/a≈•∫ÍG.otf', 30) 
        
        # Audio
        self.carol = "audios/we-wish-you-a-merry-christmas.mp3"
        pygame.mixer.init()
        pygame.mixer.music.load(self.carol)
        self.hittingSound = pygame.mixer.Sound("audios/hit.mp3")
        
        pygame.mixer.music.play(-1)
        
        # Instruction info
        self.textX = 40
        self.textY = 300
        
        # Tree info
            # Size
        self.sizeX = 400
        self.sizeY = (425//405) * self.sizeX
        # 0.95330220146765 is the ratio between X and Y of the original image. 

            # Position
        self.treeX1 = self.board_width // 2 - 200
        self.treeX2 = self.treeX1 + self.sizeX
        self.treeY1 = self.board_height // 2 - 200
        self.treeY2 = self.treeY1 + self.sizeY
        
            # background tree
        self.first_row_pos = [(15, 232), (259, 201), (764, 233), (526, 202)]
        self.second_row_pos = [(162, 317), (676, 312), (902, 359), (719, 341), 
                               (-50, 365), (117, 364), (865, 380)]

        # Progress Bar info
            # Position
        self.progressBarX = 777
        self.progressBarY = 50
  
        # Size
        self.progressBarSizeX = 200
        self.progressBarSizeY = (425//405) * self.progressBarSizeX
  
    
        # hitting adjustment
        self.hit_amount = [5]
        self.level = 5
        
        for i in range(1, 10):
            self.hit_amount.append(self.hit_amount[i-1] + self.level)
            
        # Click flag info
        self.clickNum = 0
        self.current_mode = 0
        self.player1_win_amt = self.level * 9
        self.player2_win_amt = 0
        self.current_state = self.player1_win_amt // 2
            
        # snowing
            # Create an empty array
        self.snow_list = []
         
        # Loop 50 times and add a snow flake in a random x,y position
        for i in range(500):
            self.x = random.randrange(0, self.board_width)
            self.y = random.randrange(0, self.board_height)
            self.snow_list.append([self.x, self.y])
        
    def snowing(self):
        # Process each snow flake in the list
        for i in range(len(self.snow_list)):
     
            # Draw the snow flake
            pygame.draw.circle(self.gamepad, (255, 255, 255), self.snow_list[i], 2)
     
            # Move the snow flake down one pixel
            self.snow_list[i][1] += 1
     
            # If the snow flake has moved off the bottom of the screen
            if self.snow_list[i][1] > self.board_height:
                # Reset it just above the top
                self.y = random.randrange(-50, -10)
                self.snow_list[i][1] = self.y
                # Give it a new x position
                self.x = random.randrange(0, self.board_width)
                self.snow_list[i][0] = self.x
                
    def check_mouse_pos(self):
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        
        return self.mouse_x, self.mouse_y  
        
    def draw_ground(self):
        pygame.draw.ellipse(self.gamepad, (255, 255, 255), [-150, self.board_height//2 + 100, 1300, 300], 0)
        
        self.second_row_tree = pygame.transform.scale(self.back_tree, (150, 188))
        
        for i in self.first_row_pos:
            self.gamepad.blit(self.back_tree, i)
            
        for i in self.second_row_pos:
            self.gamepad.blit(self.second_row_tree, i)
                

    def draw_board(self):
        # color the pad
        self.gamepad.fill(self.board_rgb)
        
        self.draw_ground()
        self.instruction = self.instruction_font.render("TAP THE TREE", True, (0, 0, 0))
        self.progressBar_msg = self.progressBar_font.render("Progress Bar", True, (0, 0, 0))
        self.gamepad.blit(self.instruction, (self.textX, self.textY))
        self.gamepad.blit(self.progressBar_msg, (770, 8))

class Hit_The_Tree(game_setting):
    def __init__(self, username, player_num):
        super().__init__()
        self.username = username
        self.player_num = player_num
#        self.msg = json.loads(myrecv(sock))
        
    def initGame(self):      
        pygame.init()
        self.gamepad = pygame.display.set_mode((self.board_width, self.board_height))    # Board setting
        pygame.display.set_caption("Hit the tree")   # Set caption for the game
        
        self.clock = pygame.time.Clock()
        self.runGame()
    
    def runGame(self):
        self.crashed = False
        self.game_ended = False
        
        while not self.crashed and not self.game_ended:
            for event in pygame.event.get():
                # End the game
                if event.type == pygame.QUIT:
                    self.crashed = True
                    
                # mouse click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(self.check_mouse_pos())

                    if (self.mouse_x >= 347 and self.mouse_x <= 661 and 
                    self.mouse_y >= 125 and self.mouse_y <= 472):
#                        self.msg = myrecv(from_sock)
                        if self.player_num == 1:
                            self.me = 1
                            self.current_state += 1
                        elif self.player_num == 2:
                            self.me = 2
                            self.current_state -= 1
                            
                        self.clickNum += 1
                        self.hittingSound.play()
                    
            self.draw_board()
            self.snowing()
            self.draw_tree()
            self.draw_child()
            
            # FINALLY update the display
            pygame.display.update()
            
        pygame.quit()
        
    def draw_tree(self):
        if self.current_state <= self.player2_win_amt:
            self.current_mode = 0
        elif self.current_state < self.hit_amount[0]:
            self.current_mode = 1
        elif self.current_state < self.hit_amount[1]:
            self.current_mode = 2
        elif self.current_state < self.hit_amount[2]:
            self.current_mode = 3
        elif self.current_state < self.hit_amount[3]:
            self.current_mode = 4
        elif self.current_state < self.hit_amount[4]:
            self.current_mode = 5
        elif self.current_state < self.hit_amount[5]:
            self.current_mode = 6
        elif self.current_state < self.hit_amount[6]:
            self.current_mode = 7
        elif self.current_state < self.hit_amount[7]:
            self.current_mode = 8
        elif self.current_state < self.hit_amount[8]:
            self.current_mode = 9
        elif self.current_state >= self.player1_win_amt:
            self.current_mode = 10
            
        self.tree_image = pygame.transform.scale(self.treeMode[self.current_mode], (self.sizeX, self.sizeY))
        self.progressBar_image = pygame.transform.scale(self.progressBar[self.current_mode], (self.progressBarSizeX, self.progressBarSizeY))
        
        self.gamepad.blit(self.tree_image, (self.treeX1, self.treeY1))
        self.gamepad.blit(self.progressBar_image, (self.progressBarX, self.progressBarY)) 
        
    def draw_child(self):
        if self.player_num == 1:
            self.gamepad.blit(self.childMode[2], (382, 345))
            if self.clickNum % 2:
                self.gamepad.blit(self.childMode[0], (500, 365))
            else:
                self.gamepad.blit(self.childMode[1], (500, 365))
                
        if self.player_num == 2:
            self.gamepad.blit(self.childMode[0], (500, 365))
            if self.clickNum % 2:
                self.gamepad.blit(self.childMode[2], (382, 345))
            else:
                self.gamepad.blit(self.childMode[3], (382, 345))


def main():
    global self_name, partner_name
    self_name, partner_name = "Player 1", "Player2"
    clock = pygame.time.Clock()
    name_box = InputBox(170, 80, 140, 32, 1)
    partner_box = InputBox(170, 125, 140, 32, 2)
    
    login_font = pygame.font.Font('font/a≈•∫ÍG.otf', 40)
    name_font = pygame.font.Font('font/a≈•∫ÍG.otf', 30)
    login_msg = login_font.render("Login", True, (0, 0, 0))
    name_msg = name_font.render("Name:", True, (0, 0, 0))
    partner_msg = name_font.render("Partner:", True, (0, 0, 0))
    start_msg = name_font.render("Start", True, (0, 0, 0))
    
    name_playerN = pygame.Rect(380, 80, 32, 32)
    partner_playerN = pygame.Rect(380, 125, 32, 32)
    
    input_boxes = [name_box, partner_box]
    done = False
    start_button = pygame.Rect(160, 175, 120, 50)
    start = False
    
    player1_rgb = (255, 153, 153)
    player2_rgb = (204, 255, 153)
    
    name_color = player1_rgb
    partner_color = player2_rgb
    
    name_player_N = 1
    
    while not done and not start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(pygame.mouse.get_pos())
                
                if event.button == 1:
                    if start_button.collidepoint(event.pos):
                        # Increment the number.
                        start = True
                        print("pressed")
                        peer = partner_name
                        peer = peer.strip()
                        pygame.time.wait(2000)
                        
                    if name_playerN.collidepoint(event.pos):
                        if name_color == player1_rgb:
                            name_color = player2_rgb
                            partner_color = player1_rgb
                            name_player_N = 2
                        else:
                            name_color = player1_rgb
                            partner_color = player2_rgb
                            name_player_N = 1
                            
                    if partner_playerN.collidepoint(event.pos):
                        if partner_color == player1_rgb:
                            name_color = player1_rgb
                            partner_color = player2_rgb
                        else:
                            name_color = player2_rgb
                            partner_color = player1_rgb
            
            for box in input_boxes:
                box.handle_event(event)

        for box in input_boxes:
            box.update()

        screen.fill((255, 255, 255))
#        screen.fill((209, 224, 229))
        for box in input_boxes:
            box.draw(screen)
            
        screen.blit(login_msg, (155, 20))
        screen.blit(name_msg, (59, 81))
        screen.blit(partner_msg, (15, 128))
        pygame.draw.rect(screen, (153, 204, 255), start_button)
        
        pygame.draw.rect(screen, name_color, name_playerN)
        pygame.draw.rect(screen, partner_color, partner_playerN)
        
        screen.blit(start_msg, (172, 183))

        pygame.display.flip()
        clock.tick(30)
        
    if start:
        game = Hit_The_Tree("Lisa", name_player_N)
        game.initGame()
    
main()