from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..websocket_manager import trade_ws_manager

router = APIRouter(prefix="/ws", tags=["realtime"])


@router.websocket("/trades/{trade_id}")
async def trade_messages_socket(
	websocket: WebSocket,
	trade_id: str,
	user_id: str = Query(...),
	db: Session = Depends(get_db)
):
	trade = (
		db.query(models.Trade)
		.filter(models.Trade.id == trade_id)
		.first()
	)

	if not trade or user_id not in (trade.from_user_id, trade.to_user_id):
		await websocket.close(code=1008)
		return

	await trade_ws_manager.connect(trade_id, websocket)

	try:
		while True:
			await websocket.receive_text()
	except WebSocketDisconnect:
		await trade_ws_manager.disconnect(trade_id, websocket)

