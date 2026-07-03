import math

# --- Simulation Parameters ---
COURT_WIDTH = 10.97  # meters (doubles court width)
COURT_LENGTH = 23.77 # meters (full court length)
NET_HEIGHT = 0.914   # meters (at center)

# Player's ideal position for hitting a ball
PLAYER_OPTIMAL_Y = COURT_LENGTH / 2 - 1.0 # Player stands 1m behind their baseline
PLAYER_OPTIMAL_X_RANGE = (COURT_WIDTH / 2 - 1.5, COURT_WIDTH / 2 + 1.5) # Optimal 3m wide zone

TIME_STEP = 0.05 # seconds
SIMULATION_DURATION = 2.5 # seconds

class Ball:
    def __init__(self, x, y, z, vx, vy, vz):
        self.x = x
        self.y = y
        self.z = z # Height
        self.vx = vx
        self.vy = vy
        self.vz = vz

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        self.vz -= 9.8 * dt # Simple gravity effect

        if self.z < 0: # Ball hits ground
            self.z = 0
            self.vz *= -0.7 # Bounce with energy loss
            # For simplicity, we don't stop horizontal movement after bounce

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target_x = x # Where the player wants to move
        self.speed = 6.0 # m/s

    def update(self, dt):
        if self.x < self.target_x:
            self.x = min(self.target_x, self.x + self.speed * dt)
        elif self.x > self.target_x:
            self.x = max(self.target_x, self.x - self.speed * dt)

def simulate_shot():
    # Initial ball state (e.g., after a serve from far end)
    # Ball starts high, moving towards the player's side
    ball = Ball(x=COURT_WIDTH / 2, y=COURT_LENGTH, z=2.5, vx=0.5, vy=-18.0, vz=-3.0)
    # Player starts at a reasonable position on their side
    player = Player(x=COURT_WIDTH / 2 + 1.0, y=PLAYER_OPTIMAL_Y)

    print("--- Tennis Shot Simulation ---")
    print(f"Player Optimal Hitting Zone X: {PLAYER_OPTIMAL_X_RANGE[0]:.2f} - {PLAYER_OPTIMAL_X_RANGE[1]:.2f} (Y: {PLAYER_OPTIMAL_Y:.2f})")
    print("-" * 30)

    ball_trajectory_data = []
    player_positions = []
    contact_point_found = False
    contact_ball_pos = None
    contact_player_pos = None

    for i in range(int(SIMULATION_DURATION / TIME_STEP)):
        time = i * TIME_STEP

        # Player tries to anticipate and move towards the ball's projected path
        if not contact_point_found and ball.y < PLAYER_OPTIMAL_Y + 5: # Player reacts when ball is somewhat close
            # Simple prediction: where will the ball be when it reaches player's Y?
            if ball.vy != 0:
                time_to_reach_player_y = (player.y - ball.y) / ball.vy
                predicted_ball_x_at_player_y = ball.x + ball.vx * time_to_reach_player_y
                player.target_x = predicted_ball_x_at_player_y
            else:
                player.target_x = ball.x
            # Clamp player target_x to court width
            player.target_x = max(0, min(COURT_WIDTH, player.target_x))

        player.update(TIME_STEP)
        ball.update(TIME_STEP)

        ball_trajectory_data.append((ball.x, ball.y, ball.z))
        player_positions.append((player.x, player.y))

        # Check for potential contact point (ball near player's Y and within reasonable height)
        if not contact_point_found and \
           abs(ball.y - player.y) < 0.5 and \
           ball.z > NET_HEIGHT and ball.z < 2.5: # Realistic hitting height
            contact_point_found = True
            contact_ball_pos = (ball.x, ball.y, ball.z)
            contact_player_pos = (player.x, player.y)
            print(f"Time: {time:.2f}s - Potential Contact Point Detected!")
            print(f"  Ball Position: X={ball.x:.2f}, Y={ball.y:.2f}, Z={ball.z:.2f}")
            print(f"  Player Position: X={player.x:.2f}, Y={player.y:.2f}")
            # --- This is where the article's concept comes in ---
            # Ball tracking systems provide ball.x, ball.y, ball.z, and ball.vx, ball.vy, ball.vz.
            # They *don't* inherently provide player.x, player.y in relation to the ball for analysis.

    print("-" * 30)
    print("\n--- Analysis of Contact Point (if found) ---")
    if contact_point_found:
        ball_x_at_contact = contact_ball_pos[0]
        player_x_at_contact = contact_player_pos[0]

        # Calculate how well the player was positioned horizontally
        optimal_x_center = (PLAYER_OPTIMAL_X_RANGE[0] + PLAYER_OPTIMAL_X_RANGE[1]) / 2
        player_x_deviation_from_optimal = abs(player_x_at_contact - optimal_x_center)
        ball_x_deviation_from_player = abs(ball_x_at_contact - player_x_at_contact)

        # --- This is the 'missing detail' part ---
        # Ball tracking gives us the ball's path. But for performance analysis,
        # we need to know the *player's interaction* with that ball.
        # How well was the player positioned relative to the ball's ideal hitting point?

        print(f"Ball X at contact: {ball_x_at_contact:.2f}m")
        print(f"Player X at contact: {player_x_at_contact:.2f}m")

        if PLAYER_OPTIMAL_X_RANGE[0] <= player_x_at_contact <= PLAYER_OPTIMAL_X_RANGE[1]:
            print("Player was within their optimal horizontal hitting zone.")
            if PLAYER_OPTIMAL_X_RANGE[0] <= ball_x_at_contact <= PLAYER_OPTIMAL_X_RANGE[1]:
                print("  Ball was also within the player's optimal horizontal hitting zone.")
                print("  This suggests a potentially well-executed shot opportunity.")
            else:
                print(f"  However, the ball was at X={ball_x_at_contact:.2f}m, outside the player's optimal zone.")
                print("  Player was well-positioned, but the ball's trajectory might have been challenging.")
        else:
            print(f"Player was NOT in their optimal horizontal hitting zone (deviation: {player_x_deviation_from_optimal:.2f}m from center).")
            print("  This indicates a potential positioning issue, regardless of the ball's path.")
            if PLAYER_OPTIMAL_X_RANGE[0] <= ball_x_at_contact <= PLAYER_OPTIMAL_X_RANGE[1]:
                print(f"  The ball was at X={ball_x_at_contact:.2f}m, within the player's optimal zone, but the player missed it.")
                print("  This highlights a player movement/anticipation issue.")
            else:
                print(f"  Both player (X={player_x_at_contact:.2f}m) and ball (X={ball_x_at_contact:.2f}m) were outside the optimal zone.")
                print("  This suggests a difficult shot opportunity compounded by player positioning.")

        # Further 'missing' detail: How far was the ball from the player's center at impact?
        print(f"Horizontal distance between player and ball at contact: {ball_x_deviation_from_player:.2f}m")
        if ball_x_deviation_from_player > 1.0: # Arbitrary threshold
            print("  This large distance suggests the player had to reach significantly, potentially impacting shot quality.")
        else:
            print("  The ball was relatively close to the player's center, allowing for better body mechanics.")

    else:
        print("No suitable contact point found during simulation.")
        print("This could mean the ball went out, bounced too low, or the player couldn't reach it in time.")

    print("\n--- Raw Data (Ball Tracking & Player Position) ---")
    print("First 5 ball positions (X, Y, Z):")
    for i, pos in enumerate(ball_trajectory_data[:5]):
        print(f"  {i*TIME_STEP:.2f}s: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
    print("First 5 player positions (X, Y):")
    for i, pos in enumerate(player_positions[:5]):
        print(f"  {i*TIME_STEP:.2f}s: ({pos[0]:.2f}, {pos[1]:.2f})")

    print("\n--- Conclusion ---")
    print("While ball tracking provides precise ball data, a comprehensive analysis requires integrating player data.")
    print("This example shows how player position relative to the ball's trajectory reveals insights into shot difficulty and player performance that ball data alone cannot.")

if __name__ == "__main__":
    simulate_shot()
