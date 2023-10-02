import pygame
pygame.init()
score_value=0
font=pygame.font.Font("freesansbold.ttf",20)
textX=10
textY=10
def show_score(x,y):
    score = font.render ("Score : " + str(score_value), True, (255, 255, 255))
    pygame.screen.blit(score,(x,y))
show_score() 