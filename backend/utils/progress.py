import json
from typing import Optional
from fastapi import WebSocket

class ProgressManager:
    """Gère la progression WebSocket"""
    
    def __init__(self, websocket: Optional[WebSocket] = None):
        self.websocket = websocket
        self.current_step = 0
        self.total_steps = 10
    
    async def send(self, step: str, percentage: int, message: str = ""):
        """Envoie la progression au frontend"""
        if not self.websocket:
            return
        
        try:
            payload = {
                "step": step,
                "percentage": min(percentage, 100),
                "message": message,
                "timestamp": str(__import__('datetime').datetime.now())
            }
            await self.websocket.send_json(payload)
            print(f"✅ Progress sent: {step} {percentage}%")
        except Exception as e:
            print(f"❌ Progress error: {e}")
    
    async def update(self, step: str, message: str = "", percentage: Optional[int] = None):
        """Mise à jour simplifiée"""
        if percentage is None:
            self.current_step += 1
            percentage = int((self.current_step / self.total_steps) * 100)
        
        await self.send(step, percentage, message)
