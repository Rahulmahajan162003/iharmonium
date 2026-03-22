import asyncio
import websockets
import json
import time
import math

try:
    from pybooklid import LidSensor
    HAS_SENSOR = True
except ImportError:
    HAS_SENSOR = False

async def handler(websocket):
    print("\nWeb App connected!")
    
    if HAS_SENSOR:
        try:
            with LidSensor() as sensor:
                for angle in sensor.monitor(interval=0.05):
                    # print(f"\rCurrent Lid Angle: {angle:.2f}°   ", end="", flush=True)
                    try:
                        await websocket.send(json.dumps({"angle": angle}))
                    except websockets.ConnectionClosed:
                        print("\nWeb App disconnected.")
                        return
        except Exception as e:
            print(f"\nLid sensor hardware error: {e}")
            print("Falling back to simulated data.")
    
    print("Using simulated lid angle (oscillating to pump bellows)...")
    start_time = time.time()
    while True:
        try:
            # Oscillate angle between 80 and 90 degrees to simulate "pumping"
            elapsed = time.time() - start_time
            angle = 85.0 + 5.0 * math.sin(elapsed * 2.0)
            
            await websocket.send(json.dumps({"angle": angle}))
            await asyncio.sleep(0.05)
        except websockets.ConnectionClosed:
            print("\nWeb App disconnected.")
            break

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Bridge active! Waiting for your web app on port 8765...")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping Bridge...")