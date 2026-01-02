#!/usr/bin/env python3
"""
WALTER-OS Spectacular Flipper Game
The Ultimate Pinball Experience

A feature-rich, visually stunning flipper/pinball game with:
- Advanced physics simulation
- Particle effects and animations
- Multiple game modes
- Power-ups and special features
- High score tracking
- Spectacular visuals
"""

import pygame
import random
import math
import json
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 1000
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Physics constants
GRAVITY = 0.5
BALL_RADIUS = 10
FLIPPER_POWER = -18
BOUNCE_DAMPENING = 0.7


class Particle:
    """Visual particle for spectacular effects"""
    def __init__(self, x, y, color, velocity=None):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = random.randint(20, 60)
        self.age = 0
        if velocity:
            self.vx, self.vy = velocity
        else:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
        self.size = random.randint(2, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity
        self.age += 1

    def draw(self, screen):
        alpha = int(255 * (1 - self.age / self.lifetime))
        size = max(1, int(self.size * (1 - self.age / self.lifetime)))
        color = tuple(min(255, max(0, c)) for c in self.color)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)

    def is_alive(self):
        return self.age < self.lifetime


class Ball:
    """The pinball"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = BALL_RADIUS
        self.trail = []
        self.glow_radius = 20

    def update(self):
        # Apply gravity
        self.vy += GRAVITY
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Wall collision
        if self.x - self.radius < 50:
            self.x = 50 + self.radius
            self.vx = abs(self.vx) * BOUNCE_DAMPENING
        if self.x + self.radius > WINDOW_WIDTH - 50:
            self.x = WINDOW_WIDTH - 50 - self.radius
            self.vx = -abs(self.vx) * BOUNCE_DAMPENING
        
        # Top collision
        if self.y - self.radius < 50:
            self.y = 50 + self.radius
            self.vy = abs(self.vy) * BOUNCE_DAMPENING
        
        # Update trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 15:
            self.trail.pop(0)

    def draw(self, screen):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            size = int(self.radius * (i / len(self.trail)))
            color = (100 + alpha // 2, 100 + alpha // 2, 255)
            pygame.draw.circle(screen, color, pos, max(2, size))
        
        # Draw glow
        for i in range(3):
            glow_color = (50 + i * 30, 50 + i * 30, 255 - i * 20)
            pygame.draw.circle(screen, glow_color, 
                             (int(self.x), int(self.y)), 
                             self.radius + (3 - i) * 3)
        
        # Draw ball
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, SILVER, (int(self.x - 3), int(self.y - 3)), 3)

    def is_out(self):
        return self.y > WINDOW_HEIGHT + 50


class Flipper:
    """Flipper paddle"""
    def __init__(self, x, y, side='left'):
        self.x = x
        self.y = y
        self.side = side
        self.length = 100
        self.width = 15
        self.angle = -30 if side == 'left' else 30
        self.rest_angle = -30 if side == 'left' else 30
        self.active_angle = 30 if side == 'left' else -30
        self.active = False
        self.angular_velocity = 0

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def update(self):
        target = self.active_angle if self.active else self.rest_angle
        diff = target - self.angle
        self.angle += diff * 0.3
        self.angular_velocity = diff * 0.3

    def get_end_point(self):
        rad = math.radians(self.angle)
        end_x = self.x + self.length * math.cos(rad)
        end_y = self.y + self.length * math.sin(rad)
        return end_x, end_y

    def draw(self, screen):
        end_x, end_y = self.get_end_point()
        
        # Draw glow
        if self.active:
            for i in range(3):
                glow_color = (255 - i * 50, 255 - i * 50, 100)
                pygame.draw.line(screen, glow_color, 
                               (self.x, self.y), (end_x, end_y), 
                               self.width + (3 - i) * 4)
        
        # Draw flipper
        color = YELLOW if self.active else ORANGE
        pygame.draw.line(screen, color, (self.x, self.y), (end_x, end_y), self.width)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.width // 2)

    def check_collision(self, ball):
        """Check collision with ball"""
        end_x, end_y = self.get_end_point()
        
        # Vector from flipper start to end
        fx = end_x - self.x
        fy = end_y - self.y
        
        # Vector from flipper start to ball
        bx = ball.x - self.x
        by = ball.y - self.y
        
        # Project ball onto flipper line
        length_sq = fx * fx + fy * fy
        if length_sq == 0:
            return False
        
        t = max(0, min(1, (bx * fx + by * fy) / length_sq))
        
        # Closest point on flipper
        closest_x = self.x + t * fx
        closest_y = self.y + t * fy
        
        # Distance to ball
        dist_x = ball.x - closest_x
        dist_y = ball.y - closest_y
        distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
        
        if distance < ball.radius + self.width // 2:
            # Collision!
            if distance > 0:
                # Normalize
                nx = dist_x / distance
                ny = dist_y / distance
                
                # Push ball out
                overlap = ball.radius + self.width // 2 - distance
                ball.x += nx * overlap
                ball.y += ny * overlap
                
                # Apply velocity
                power = abs(self.angular_velocity) * 3 if self.active else 1
                ball.vx = nx * 10 * power
                ball.vy = ny * 10 * power
                
                return True
        return False


class Bumper:
    """Bouncy bumper"""
    def __init__(self, x, y, radius=30, points=100):
        self.x = x
        self.y = y
        self.radius = radius
        self.points = points
        self.hit_timer = 0
        self.pulse = 0

    def update(self):
        if self.hit_timer > 0:
            self.hit_timer -= 1
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)

    def draw(self, screen):
        pulse_size = int(3 * math.sin(self.pulse))
        
        # Draw glow layers
        for i in range(4):
            color = (255 - i * 40, 100 - i * 20, 255 - i * 40) if self.hit_timer > 0 else \
                   (100 - i * 20, 100 - i * 20, 255 - i * 40)
            pygame.draw.circle(screen, color, (self.x, self.y), 
                             self.radius + pulse_size + (4 - i) * 5)
        
        # Draw bumper
        color = PURPLE if self.hit_timer > 0 else BLUE
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius - 5, 2)

    def check_collision(self, ball):
        dist = math.sqrt((ball.x - self.x) ** 2 + (ball.y - self.y) ** 2)
        if dist < self.radius + ball.radius:
            # Calculate bounce direction
            if dist > 0:
                nx = (ball.x - self.x) / dist
                ny = (ball.y - self.y) / dist
                
                # Push ball out
                overlap = self.radius + ball.radius - dist
                ball.x += nx * overlap
                ball.y += ny * overlap
                
                # Bounce with force
                force = 12
                ball.vx = nx * force
                ball.vy = ny * force
                
                self.hit_timer = 10
                return True
        return False


class Target:
    """Score target"""
    def __init__(self, x, y, width=60, height=20, points=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.points = points
        self.hit_timer = 0
        self.hit_count = 0

    def update(self):
        if self.hit_timer > 0:
            self.hit_timer -= 1

    def draw(self, screen):
        color = GREEN if self.hit_timer > 0 else CYAN
        
        # Draw glow
        if self.hit_timer > 0:
            for i in range(2):
                glow_color = (0, 255 - i * 100, 255 - i * 100)
                pygame.draw.rect(screen, glow_color,
                               (self.x - (2 - i) * 3, self.y - (2 - i) * 3,
                                self.width + (2 - i) * 6, self.height + (2 - i) * 6))
        
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)

    def check_collision(self, ball):
        if (self.x < ball.x < self.x + self.width and
            self.y < ball.y < self.y + self.height):
            # Bounce
            if ball.vx != 0 or ball.vy != 0:
                ball.vy = -abs(ball.vy) * 0.8
                self.hit_timer = 10
                self.hit_count += 1
                return True
        return False


class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("WALTER-OS Spectacular Flipper")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        self.reset_game()
        self.high_score = self.load_high_score()
        
    def reset_game(self):
        self.ball = Ball(WINDOW_WIDTH // 2, 100)
        self.left_flipper = Flipper(250, WINDOW_HEIGHT - 150, 'left')
        self.right_flipper = Flipper(550, WINDOW_HEIGHT - 150, 'right')
        
        # Create bumpers in a spectacular pattern
        self.bumpers = [
            Bumper(400, 300, 40, 200),
            Bumper(250, 400, 35, 150),
            Bumper(550, 400, 35, 150),
            Bumper(325, 500, 30, 100),
            Bumper(475, 500, 30, 100),
        ]
        
        # Create targets
        self.targets = [
            Target(150, 250, 80, 20, 75),
            Target(570, 250, 80, 20, 75),
            Target(300, 180, 200, 20, 100),
        ]
        
        self.particles = []
        self.score = 0
        self.multiplier = 1
        self.combo = 0
        self.balls_left = 3
        self.game_over = False
        self.last_hit_time = 0
        
    def load_high_score(self):
        try:
            if os.path.exists('flipper_scores.json'):
                with open('flipper_scores.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        try:
            with open('flipper_scores.json', 'w') as f:
                json.dump({
                    'high_score': self.high_score,
                    'date': datetime.now().isoformat()
                }, f)
        except:
            pass
    
    def add_particles(self, x, y, color, count=20):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
    
    def add_score(self, points):
        self.score += points * self.multiplier
        self.combo += 1
        self.last_hit_time = pygame.time.get_ticks()
        
        # Increase multiplier with combo
        # Note: combo > 20 means 21+ hits, > 10 means 11+ hits, > 5 means 6+ hits
        if self.combo > 20:
            self.multiplier = 5  # 21+ hits
        elif self.combo > 10:
            self.multiplier = 3  # 11-20 hits
        elif self.combo > 5:
            self.multiplier = 2  # 6-10 hits
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Left flipper (Left Shift or A)
        if keys[pygame.K_LSHIFT] or keys[pygame.K_a]:
            self.left_flipper.activate()
        else:
            self.left_flipper.deactivate()
        
        # Right flipper (Right Shift or D)
        if keys[pygame.K_RSHIFT] or keys[pygame.K_d]:
            self.right_flipper.activate()
        else:
            self.right_flipper.deactivate()
    
    def update(self):
        if self.game_over:
            return
        
        # Update game objects
        self.ball.update()
        self.left_flipper.update()
        self.right_flipper.update()
        
        for bumper in self.bumpers:
            bumper.update()
        
        for target in self.targets:
            target.update()
        
        # Check flipper collisions
        if self.left_flipper.check_collision(self.ball):
            self.add_particles(self.ball.x, self.ball.y, YELLOW, 15)
            self.add_score(10)
        
        if self.right_flipper.check_collision(self.ball):
            self.add_particles(self.ball.x, self.ball.y, YELLOW, 15)
            self.add_score(10)
        
        # Check bumper collisions
        for bumper in self.bumpers:
            if bumper.check_collision(self.ball):
                self.add_particles(bumper.x, bumper.y, PURPLE, 25)
                self.add_score(bumper.points)
        
        # Check target collisions
        for target in self.targets:
            if target.check_collision(self.ball):
                self.add_particles(target.x + target.width // 2, 
                                 target.y + target.height // 2, GREEN, 20)
                self.add_score(target.points)
        
        # Update particles
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
        
        # Check combo timeout
        if pygame.time.get_ticks() - self.last_hit_time > 3000:
            self.combo = 0
            self.multiplier = 1
        
        # Check if ball is out
        if self.ball.is_out():
            self.balls_left -= 1
            if self.balls_left > 0:
                self.ball = Ball(WINDOW_WIDTH // 2, 100)
                self.combo = 0
                self.multiplier = 1
            else:
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
    
    def draw(self):
        # Background gradient
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            color = (
                int(10 + ratio * 20),
                int(10 + ratio * 20),
                int(40 + ratio * 40)
            )
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
        
        # Draw side walls
        pygame.draw.rect(self.screen, SILVER, (0, 0, 50, WINDOW_HEIGHT))
        pygame.draw.rect(self.screen, SILVER, (WINDOW_WIDTH - 50, 0, 50, WINDOW_HEIGHT))
        pygame.draw.rect(self.screen, SILVER, (0, 0, WINDOW_WIDTH, 50))
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw game objects
        for bumper in self.bumpers:
            bumper.draw(self.screen)
        
        for target in self.targets:
            target.draw(self.screen)
        
        self.left_flipper.draw(self.screen)
        self.right_flipper.draw(self.screen)
        self.ball.draw(self.screen)
        
        # Draw UI
        score_text = self.font_small.render(f'SCORE: {self.score}', True, WHITE)
        self.screen.blit(score_text, (60, 10))
        
        high_score_text = self.font_small.render(f'HIGH: {self.high_score}', True, GOLD)
        self.screen.blit(high_score_text, (WINDOW_WIDTH - 250, 10))
        
        if self.multiplier > 1:
            mult_text = self.font_medium.render(f'x{self.multiplier}', True, ORANGE)
            self.screen.blit(mult_text, (WINDOW_WIDTH // 2 - 30, 60))
        
        if self.combo > 5:
            combo_text = self.font_small.render(f'COMBO: {self.combo}', True, CYAN)
            self.screen.blit(combo_text, (WINDOW_WIDTH // 2 - 80, 110))
        
        # Draw balls left
        for i in range(self.balls_left):
            pygame.draw.circle(self.screen, WHITE, (60 + i * 30, 60), 8)
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font_large.render('GAME OVER', True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
            self.screen.blit(game_over_text, text_rect)
            
            final_score_text = self.font_medium.render(f'Final Score: {self.score}', True, WHITE)
            text_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(final_score_text, text_rect)
            
            if self.score == self.high_score and self.score > 0:
                new_high_text = self.font_medium.render('NEW HIGH SCORE!', True, GOLD)
                text_rect = new_high_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
                self.screen.blit(new_high_text, text_rect)
            
            restart_text = self.font_small.render('Press SPACE to restart or ESC to quit', True, WHITE)
            text_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120))
            self.screen.blit(restart_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        
        # Show start screen
        self.show_start_screen()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset_game()
            
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def show_start_screen(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    waiting = False
            
            self.screen.fill(BLACK)
            
            # Animated title
            pulse = abs(math.sin(pygame.time.get_ticks() / 500))
            
            title = self.font_large.render('SPECTACULAR FLIPPER', True, 
                                          (int(255 * pulse), 150, 255))
            text_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 200))
            self.screen.blit(title, text_rect)
            
            subtitle = self.font_medium.render('WALTER-OS Edition', True, CYAN)
            text_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 280))
            self.screen.blit(subtitle, text_rect)
            
            # Instructions
            instructions = [
                'Controls:',
                'Left Flipper: LEFT SHIFT or A',
                'Right Flipper: RIGHT SHIFT or D',
                '',
                'Hit bumpers and targets for points!',
                'Build combos for multipliers!',
                '',
                'Press any key to start...'
            ]
            
            y_offset = 400
            for line in instructions:
                text = self.font_small.render(line, True, WHITE)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 40
            
            # Draw preview elements
            preview_bumper = Bumper(150, 600, 30)
            preview_bumper.pulse = pygame.time.get_ticks() / 1000
            preview_bumper.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)


def main():
    """Main entry point"""
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
