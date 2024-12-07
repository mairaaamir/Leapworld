import pygame 
import sys

pygame.init()

#Setting up the display
width, height = 1200, 640
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("LeapWorld")

#Jump variables 
jump_count = 0
is_double_jumping = False

#Loading the images
background = pygame.image.load("/Users/Maira2/Mypygame/Leapworld/Leapworld/bg.png")
background = pygame.transform.scale(background, (width, height))

#Adding main character
animal_idle = pygame.image.load("/Users/Maira2/Mypygame/Leapworld/Leapworld/run0001.png")
animal_idle_idle = pygame.transform.scale(animal_idle, (100, 100))

#Adding heart images
heart_image = pygame.image.load("/Users/Maira2/Mypygame/Leapworld/Leapworld/heart.png")
heart_image = pygame.transform.scale(heart_image, (60, 30)) #Sizing of heart images


#Adding running animations 
run_action = [
    pygame.image.load(f"/Users/Maira2/Mypygame/Leapworld/Leapworld/run{i:04d}.png")
    for i in [1, 2, 5, 7, 9, 11, 13, 15, 17, 19, 21]
]
run_action = [pygame.transform.scale(frame, (100, 100)) for frame in run_action]
current_run_action = 0 
run_action_delay = 5
run_action_timer = 0 

#Adding jump animations 
jump_action = [
    pygame.image.load(f"/Users/Maira2/Mypygame/Leapworld/Leapworld/jump{i:04d}.png")
    for i in range(1, 22, 2)
]
jump_action = [pygame.transform.scale(frame, (100, 100)) for frame in jump_action]
current_frame = 0
frame_delay = 5
frame_timer = 0

#Adding coin images
coin_images = [
    pygame.image.load(f"/Users/Maira2/Mypygame/Leapworld/Leapworld/goldCoin{i}.png")
    for i in range(1, 10)
]
coin_images = [pygame.transform.scale(coin, (50, 50)) for coin in coin_images]

#Adding and creating the platforms
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, moving=False, move_direction=None, speed=0):
        super().__init__()
        self.image = pygame.image.load("/Users/Maira2/Mypygame/Leapworld/Leapworld/grass_block.png")
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.moving = moving #Moving platforms
        self.move_direction = move_direction
        self.speed = speed
        self.initial_x = self.rect.x
        self.initial_y = self.rect.y

    def update(self):
        
        if self.moving:
            if self.move_direction == 'horizontal': #Moving the platforms horizontally 
                self.rect.x += self.speed
                if self.rect.x > width - self.rect.width or self.rect.x < 0:
                    self.speed = -self.speed
            elif self.move_direction == 'vertical':
                self.rect.y += self.speed
                if self.rect.y > height - self.rect.height or self.rect.y < 0:
                    self.speed = -self.speed
#Class for animation for coins and collision  
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = 0 

    #Roatating the coins
    def update(self):
        self.angle += 5
        if self.angle >= 360:
            self.angle = 0
        
        self.image = pygame.transform.rotate(coin_images[0], self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)



platforms = pygame.sprite.Group()
coins = pygame.sprite.Group()

platform_width, platform_height = 130,50
num_platforms = 8 #Amount of platforms added

#Positioning the platforms
for i in range(num_platforms):
    x = (i % 4) * (width // 4) + 50
    y = height - ((i + 1) * 75)

    moving = False
    if i == 3 or i == 6:
        moving = True
    
    #Making some platforms move
    platform = Platform(x, y, platform_width, platform_height, moving=moving, move_direction='horizontal', speed=2)
    platforms.add(platform)

    #Adding each coin to a platform for the animal to collect
    coin_x = x + (platform_width // 2) - 25
    coin_y = y - 50
    coins.add(Coin(coin_x, coin_y))

#Animal starting position on the starting platform
animal_rect = animal_idle.get_rect()
animal_rect.x = platforms.sprites()[0].rect.x + (platform_width // 2) - (animal_rect.width //2)
animal_rect.y = platforms.sprites()[0].rect.top - animal_rect.height #Ensuring the raccoon is placed on the platform

animal_speed = 5
gravity = 1
is_jumping = False 
jump_strength = 15 
jump_velocity = jump_strength 

on_moving_platform = None
is_falling = False
jump_count = 0 

# Adding in the lava images
lava_image = pygame.image.load('/Users/Maira2/Mypygame/Leapworld/Leapworld/lava.png')
lava_image = pygame.transform.scale(lava_image, (1200, 40)) #Scaling the lava to 600pixels (width) x 20pixels (height)
lava_x = (width - 1200) //2 
lava_y = height - 40

clock = pygame.time.Clock()

#Setting up score and lives
score = 0 
lives = 2
running = True

#Gaming loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
    
    keys = pygame.key.get_pressed()

    #Using left and right keys for the movement
    if keys[pygame.K_LEFT]:
        animal_rect.x -= animal_speed
        

    if keys[pygame.K_RIGHT]:
        animal_rect.x += animal_speed
    
    #Jump key
    if keys[pygame.K_UP] and not is_jumping and not is_falling:
        is_jumping = True
        jump_velocity = -jump_strength

    if is_jumping:
        animal_rect.y += jump_velocity
        jump_velocity += gravity

    if jump_velocity >= 0:
        is_jumping = False
        is_falling = True

    if is_falling:
        animal_rect.y += jump_velocity
        jump_velocity += gravity

        landed_on_platform = False
        
        #Checking if the character collides with any platforms
        for platform in platforms:
            if animal_rect.colliderect(platform.rect):
                    if animal_rect.bottom - jump_velocity <= platform.rect.top -1 and jump_velocity >= 0: #Checking if the character is falling and lands on the platforms properly
                       animal_rect.y = platform.rect.top - animal_rect.height #Postioning the character on top of all the platforms
                       is_falling = False 
                       jump_velocity = 0
                       landed_on_platform = True
                       break
        if not landed_on_platform:
            is_falling = True

          #Making sure the character is on a moving platform    
        if on_moving_platform:
                #If platforms are moving vertically and horizonally update the characters y and x positions
                if on_moving_platform.move_direction == 'horizontal':
                    animal_rect.x += on_moving_platform.speed
                elif on_moving_platform.move_direction == 'vertical':
                   animal_rect.y += on_moving_platform.speed
    #Coin collision
    for coin in coins:
        if animal_rect.colliderect(coin.rect):
            coins.remove(coin)
            score += 1

    if animal_rect.x >= width - animal_rect.width and animal_rect.y <= 50:
        #Level done message display
        font = pygame.font.SysFont("Roboto", 50) #Font of message displayed 
        win_message = font.render("Level 1 Completed!", True, (255, 0, 0)) #Red font
        screen.blit(win_message, (width // 2 - win_message.get_width() // 2, height // 2))  #Placing message in the middle of screen
        pygame.display.flip() 
        pygame.time.wait(1000) #Waiting 1 second before stopping 
        running = False 
    
    last_safe_position = (platforms.sprites()[0].rect.x, platforms.sprites()[0].rect.top - animal_rect.height) 


    if animal_rect.y > width:
        lives -= 1 #1 life lost if raccoon falls off
        if lives == 1: #After 1st death reset to place where raccoon died from
            animal_rect.x, animal_rect.y = last_safe_position
            is_jumping = False
            is_falling = False
            jump_velocity = 0

        elif lives == 0:
            animal_rect.x = platform.sprites()[0].rect.x
            animal_rect.y = platform.sprites()[0].rect.top - animal_rect.height
            last_safe_position = (animal_rect.x, animal_rect.y) 
            is_jumping = False
            is_falling = False
            jump_velocity = 0
        elif lives < 0:
            #The game is over, therfore reset score and lives
            print("Game over, restarting" )

            lives = 2
            score = 0
            animal_rect.x = platforms.sprites()[0].rect.x
            animal_rect.y = platforms.sprites()[0].rect.top - animal_rect.height
            last_safe_position = (animal_rect.x, animal_rect.y)
            is_jumping = False
            is_falling = False
            jump_velocity = 0

    animal_rect.x = max(0, min(width - animal_rect.width, animal_rect.x))
    if animal_rect.y > height: 
        animal_rect.x = platforms.sprites()[0].rect.x
        animal_rect.y = platforms.sprites()[0].rect.top - animal_rect.height
        is_jumping = False
        is_falling = False
        jump_velocity = 0


    platforms.update()
    coins.update()

    run_action_timer += 1
    if run_action_timer >= run_action_delay:
        current_run_frame = (current_run_frame + 1) % len(run_action)
        run_action_timer = 0

    frame_timer += 1
    if frame_timer >= frame_delay:
        current_frame = (current_frame + 1) % len(jump_action)
        frame_timer = 0

    screen.blit(background, (0, 0))
    platforms.draw(screen)
    coins.draw(screen)

    #Adding in hearts to represent the lives
    for i in range(lives):
        screen.blit(heart_image, (10 + i * 35, 40))

    
    if is_jumping:
        screen.blit(jump_action[current_frame], animal_rect)
    elif keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
        screen.blit(run_action[current_run_frame], animal_rect)
    else:
        screen.blit(animal_idle, animal_rect)

    #Lava will be at the bottom of the screen
    screen.blit(lava_image, (lava_x, lava_y))


    font = pygame.font.SysFont("Roboto", 45) 
    score_text = font.render(f"Score: {score}", True, (255, 0, 0)) #Red font
    screen.blit(score_text, (10, 10))

    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()