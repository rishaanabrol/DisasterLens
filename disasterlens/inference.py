import random
import io
from PIL import Image

class DisasterModel:
    def __init__(self, checkpoint_path):
        self.device = "cpu"
        self.classes = ["Fire", "Structural Damage", "Flood / Water Damage"]
        print(f"[inference] AI Mock Model loaded from {checkpoint_path}")

    def predict(self, image_bytes):
        # Extremely basic heuristic to simulate AI without the real PyTorch model
        # Since we don't have the real model weights, we guess based on average color.
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert("RGB")
            img = img.resize((50, 50))
            
            r_total, g_total, b_total = 0, 0, 0
            pixels = img.getdata()
            for r, g, b in pixels:
                r_total += r
                g_total += g
                b_total += b
            
            count = len(pixels)
            r_avg = r_total / count
            g_avg = g_total / count
            b_avg = b_total / count
            
            # Simple color logic
            if r_avg > b_avg + 30 and r_avg > g_avg + 10:
                # Lots of red/orange
                hazard = "Fire"
            elif b_avg > r_avg and b_avg > g_avg - 20:
                # Lots of blue / grayish water
                hazard = "Flood / Water Damage"
            elif r_avg > 150 and g_avg > 150 and b_avg > 150:
                # Bright / grey / sky -> might be water or structural
                hazard = "Flood / Water Damage" 
            else:
                hazard = "Structural Damage"
                
        except Exception as e:
            print("Error parsing image for mock:", e)
            hazard = random.choice(self.classes)

        # Generate mock confidence
        confidence = round(random.uniform(0.75, 0.98), 2)
        other1 = round(random.uniform(0.01, 1.0 - confidence), 2)
        other2 = round(1.0 - confidence - other1, 2)
        
        dist = [confidence, other1, other2]
        random.shuffle(dist)
        
        # Align max confidence with chosen hazard
        max_idx = dist.index(max(dist))
        hazard_idx = self.classes.index(hazard)
        dist[hazard_idx], dist[max_idx] = dist[max_idx], dist[hazard_idx]
        
        distribution = {
            self.classes[0]: dist[0],
            self.classes[1]: dist[1],
            self.classes[2]: dist[2]
        }
        
        priority = "HIGH" if confidence > 0.8 else ("MEDIUM" if confidence > 0.6 else "LOW")
        
        return {
            "hazard_type": hazard,
            "hazard_confidence": confidence,
            "hazard_distribution": distribution,
            "priority": priority,
            "recommended_action": f"Dispatch units for {hazard} assessment.",
            "alert": f"Detected {hazard} with {confidence*100}% confidence."
        }
