// Use environment variable in production, fallback to localhost for development
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:9000';

/**
 * Check if token is a UUID (offline mode) or JWT (backend mode)
 */
function isUuidToken(token: string): boolean {
	// UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
	const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
	return uuidRegex.test(token);
}

function getAuthHeaders(): Record<string, string> {
	const token = localStorage.getItem('bayanihan_token');
	const headers: Record<string, string> = {
		'Content-Type': 'application/json'
	};
	
	// Only include Authorization header for JWT tokens (not UUID tokens from offline mode)
	if (token && !isUuidToken(token)) {
		headers['Authorization'] = `Bearer ${token}`;
	}
	
	return headers;
}

async function handleResponse<T>(res: Response): Promise<T> {
	if (!res.ok) {
		let errorMessage = `HTTP ${res.status}`;
		try {
			const text = await res.text();
			if (text) {
				try {
					const errorData = JSON.parse(text);
					errorMessage = errorData.detail || errorData.message || text;
				} catch {
					errorMessage = text;
				}
			}
		} catch (e) {
			// If we can't read the response, use status code
			errorMessage = `HTTP ${res.status}: ${res.statusText}`;
		}
		
		// Log specific error types for debugging
		if (res.status === 401) {
			console.error('Authentication failed - token may be invalid or expired');
		} else if (res.status === 400) {
			console.error('Bad request - check request parameters:', errorMessage);
		}
		
		throw new Error(errorMessage);
	}
	return res.json() as Promise<T>;
}

async function fetchWithTimeout(url: string, options: RequestInit = {}, timeout = 10000): Promise<Response> {
	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), timeout);
	
	try {
		const response = await fetch(url, {
			...options,
			signal: controller.signal
		});
		clearTimeout(timeoutId);
		return response;
	} catch (error) {
		clearTimeout(timeoutId);
		if (error.name === 'AbortError') {
			throw new Error('Request timeout');
		}
		throw error;
	}
}

export const api = {
	get: async <T>(path: string) => handleResponse<T>(await fetchWithTimeout(`${API_BASE_URL}${path}`, {
		headers: getAuthHeaders()
	})),
	post: async <T>(path: string, body: unknown) => handleResponse<T>(await fetchWithTimeout(`${API_BASE_URL}${path}`, {
		method: 'POST',
		headers: getAuthHeaders(),
		body: JSON.stringify(body)
	})),
	patch: async <T>(path: string, body: unknown) => handleResponse<T>(await fetchWithTimeout(`${API_BASE_URL}${path}`, {
		method: 'PATCH',
		headers: getAuthHeaders(),
		body: JSON.stringify(body)
	}))
};


