from collections import defaultdict
from typing import DefaultDict, Set, Dict, Any
from fastapi import WebSocket
import asyncio


class TradeConnectionManager:
	def __init__(self) -> None:
		self.active_connections: DefaultDict[str, Set[WebSocket]] = defaultdict(set)
		self._lock = asyncio.Lock()

	async def connect(self, trade_id: str, websocket: WebSocket) -> None:
		await websocket.accept()
		async with self._lock:
			self.active_connections[trade_id].add(websocket)

	async def disconnect(self, trade_id: str, websocket: WebSocket) -> None:
		async with self._lock:
			connections = self.active_connections.get(trade_id)
			if connections and websocket in connections:
				connections.remove(websocket)
				if not connections:
					self.active_connections.pop(trade_id, None)

	async def broadcast_message(self, trade_id: str, payload: Dict[str, Any]) -> None:
		async with self._lock:
			targets = list(self.active_connections.get(trade_id, []))

		for connection in targets:
			try:
				await connection.send_json(payload)
			except Exception:
				await self.disconnect(trade_id, connection)


trade_ws_manager = TradeConnectionManager()

