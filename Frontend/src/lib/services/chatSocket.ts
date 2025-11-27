import { API_BASE_URL } from '$lib/config/api';

export type ChatSocketHandlers = {
	onMessage?: (payload: any) => void;
	onTyping?: (payload: { userId: string; isTyping: boolean }) => void;
	onPresence?: (payload: { userId: string; online: boolean }) => void;
	onRead?: (payload: { messageId: string; readerId: string; readAt?: string }) => void;
	onError?: (error: Event) => void;
};

type OutgoingEvent =
	| { type: 'typing'; tradeId: string; userId: string; isTyping: boolean }
	| { type: 'read'; tradeId: string; userId: string; messageIds: string[] }
	| { type: 'presence'; tradeId: string; userId: string; status: 'online' | 'offline' };

const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');

class ChatSocketManager {
	private socket: WebSocket | null = null;
	private tradeId: string | null = null;
	private userId: string | null = null;
	private handlers: ChatSocketHandlers | null = null;
	private reconnectAttempts = 0;
	private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

	connect(tradeId: string, userId: string, handlers: ChatSocketHandlers) {
		this.tradeId = tradeId;
		this.userId = userId;
		this.handlers = handlers;
		this.openSocket();
	}

	private openSocket() {
		if (!this.tradeId || !this.userId) return;
		this.cleanup();

		const socketUrl = `${WS_BASE_URL}/ws/trades/${this.tradeId}?user_id=${encodeURIComponent(this.userId)}`;
		this.socket = new WebSocket(socketUrl);

		this.socket.onopen = () => {
			this.reconnectAttempts = 0;
		};

		this.socket.onmessage = (event) => {
			try {
				const payload = JSON.parse(event.data);
				switch (payload?.type) {
					case 'message':
						this.handlers?.onMessage?.(payload.message);
						break;
					case 'typing':
						this.handlers?.onTyping?.({
							userId: payload.userId,
							isTyping: payload.isTyping
						});
						break;
					case 'presence':
						this.handlers?.onPresence?.({
							userId: payload.userId,
							online: Boolean(payload.online)
						});
						break;
					case 'read':
						this.handlers?.onRead?.({
							messageId: payload.messageId,
							readerId: payload.userId,
							readAt: payload.readAt
						});
						break;
					default:
						break;
				}
			} catch (error) {
				console.warn('Failed to parse socket payload', error);
			}
		};

		this.socket.onerror = (event) => {
			this.handlers?.onError?.(event);
		};

		this.socket.onclose = () => {
			this.scheduleReconnect();
		};
	}

	private scheduleReconnect() {
		if (!this.tradeId || !this.userId) return;
		if (this.reconnectAttempts >= 5) return;
		const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 10000);
		this.reconnectAttempts += 1;
		this.reconnectTimer = setTimeout(() => this.openSocket(), delay);
	}

	send(event: OutgoingEvent) {
		if (!this.socket || this.socket.readyState !== WebSocket.OPEN) return;
		this.socket.send(JSON.stringify(event));
	}

	emitTyping(isTyping: boolean) {
		if (!this.tradeId || !this.userId) return;
		this.send({ type: 'typing', tradeId: this.tradeId, userId: this.userId, isTyping });
	}

	emitRead(messageIds: string[]) {
		if (!this.tradeId || !this.userId || !messageIds.length) return;
		this.send({ type: 'read', tradeId: this.tradeId, userId: this.userId, messageIds });
	}

	disconnect() {
		this.tradeId = null;
		this.userId = null;
		this.handlers = null;
		this.cleanup(true);
	}

	private cleanup(closeSocket = false) {
		if (this.reconnectTimer) {
			clearTimeout(this.reconnectTimer);
			this.reconnectTimer = null;
		}
		if (this.socket) {
			this.socket.onopen = null;
			this.socket.onclose = null;
			this.socket.onmessage = null;
			this.socket.onerror = null;
			if (closeSocket) {
				this.socket.close();
			}
			this.socket = null;
		}
	}
}

export const chatSocketManager = new ChatSocketManager();

