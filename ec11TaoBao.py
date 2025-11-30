from machine import Pin
import time

class EC11:
    def __init__(self, pin_a, pin_b, pin_c):
        """
        Initialize EC11 rotary encoder for TaoBao version with external pull-ups
        pin_a, pin_b: rotation pins (Terminal A and B)
        pin_c: push button pin (Terminal C)
        
        IMPORTANT: This version has external 10K pull-ups to 5V
        So we use Pin.IN (no internal pull-up)
        """
        # No internal pull-ups since external 10K pull-ups exist
        self.pin_a = Pin(pin_a, Pin.IN)
        self.pin_b = Pin(pin_b, Pin.IN)
        # Use pull-down for button to make logic clearer: pressed=1, unpressed=0
        self.pin_c = Pin(pin_c, Pin.IN, Pin.PULL_DOWN)
        
        # Quadrature state tracking
        self.last_state = (self.pin_a.value() << 1) | self.pin_b.value()
        
        # Lookup table for quadrature decoding
        # Based on state transitions: 00->01->11->10->00 (CW) or reverse (CCW)
        self.state_table = [0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0]
        
        # Counter for rotation
        self.counter = 0
        
        # Accumulator for detent detection (4 steps = 1 detent)
        self.step_accumulator = 0
        
        # Button state tracking
        self.last_button = self.pin_c.value()
        self.button_debounce_time = 0
    
    def read_rotation(self):
        """
        Read rotation direction using quadrature decoding
        Returns: 1 for clockwise, -1 for counter-clockwise, 0 for no change
        """
        # Read current state
        current_state = (self.pin_a.value() << 1) | self.pin_b.value()
        
        # Calculate index for lookup table
        index = (self.last_state << 2) | current_state
        
        # Get direction from lookup table
        direction = self.state_table[index]
        
        # Accumulate steps - only return value after 4 steps (1 detent)
        if direction != 0:
            self.step_accumulator += direction
            self.counter += direction
            
            # Check if we've completed a detent (4 steps in one direction)
            if abs(self.step_accumulator) >= 4:
                result = 1 if self.step_accumulator > 0 else -1
                self.step_accumulator = 0
                self.last_state = current_state
                return result
        
        # Update last state
        self.last_state = current_state
        
        return 0
    
    def read_button(self):
        """
        Read button press with software debouncing
        Returns: True if button was just pressed, False otherwise
        """
        current_time = time.ticks_ms()
        current_button = self.pin_c.value()
        # print('current_button', current_button)
        
        # Button is pressed when pin goes HIGH (from LOW to HIGH)
        # With internal pull-down: unpressed=0, pressed=1
        # Add debouncing: ignore changes within 50ms
        if self.last_button == 0 and current_button == 1:
            if time.ticks_diff(current_time, self.button_debounce_time) > 50:
                self.button_debounce_time = current_time
                self.last_button = current_button
                return True
        
        self.last_button = current_button
        return False
    
    def get_counter(self):
        """Get current counter value"""
        return self.counter
    
    def reset_counter(self):
        """Reset counter to zero"""
        self.counter = 0

# Initialize EC11 with pins 3, 4, 5
encoder = EC11(pin_a=3, pin_b=4, pin_c=5)

print("EC11 Rotary Encoder Test (TaoBao Version)")
print("Pin A: 3, Pin B: 4, Pin C: 5")
print("External 10K pull-ups to 5V with 0.01uF caps")
print("Rotate encoder or press button...")
print("Press Ctrl+C to exit")
print()

try:
    while True:
        # Check rotation
        rotation = encoder.read_rotation()
        if rotation == 1:
            print(f"↻ Clockwise      - Counter: {encoder.get_counter()}")
        elif rotation == -1:
            print(f"↺ Anti-clockwise - Counter: {encoder.get_counter()}")
        
        # Check button press
        if encoder.read_button():
            print(f"🔘 Button pressed! Counter: {encoder.get_counter()} → 0")
            encoder.reset_counter()
        
        time.sleep_ms(1)  # Small delay to prevent excessive polling
        
except KeyboardInterrupt:
    print("\nProgram stopped")