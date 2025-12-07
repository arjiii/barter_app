<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authService } from '$lib/services/authService';

	let isLoading = true;
	let error = '';
	let success = false;

	function getEmailFromToken(token: string): string | null {
		try {
			// Basic JWT decoding (extract payload)
			const parts = token.split('.');
			if (parts.length !== 3) return null;
			const payload = JSON.parse(atob(parts[1]));
			return payload.email || null;
		} catch (e) {
			console.error('Error decoding token:', e);
			return null;
		}
	}

	onMount(async () => {
		// Handle hash fragment params (Supabase default)
		const hash = window.location.hash.substring(1);
		const params = new URLSearchParams(hash);
		const accessToken = params.get('access_token');
		const errorDescription = params.get('error_description');

		if (errorDescription) {
			error = errorDescription.replace(/\+/g, ' ');
			isLoading = false;
			return;
		}

		if (accessToken) {
			const email = getEmailFromToken(accessToken);
			if (email) {
				try {
					const result = await authService.confirmSupabaseSignup(email);
					if (result.success) {
						success = true;
						// Redirect after short delay
						setTimeout(() => {
							goto('/discovery');
						}, 3000);
					} else {
						error = result.message;
					}
				} catch (err) {
					console.error('Confirmation error:', err);
					error = 'Failed to confirm account creation.';
				}
			} else {
				error = 'Could not retrieve email from verification token.';
			}
		} else {
			// Check if we have error query params instead (sometimes happens)
			const urlParams = new URLSearchParams(window.location.search);
			if (urlParams.get('error_description')) {
				error = urlParams.get('error_description') || 'Unknown error';
			} else {
				error = 'No verification token found.';
			}
		}
		isLoading = false;
	});
</script>

<div class="min-h-screen bg-[#f7f5f3] flex items-center justify-center px-4 py-12 font-['Inter',sans-serif]">
	<div class="max-w-md w-full">
		<div class="bg-white rounded-2xl shadow-xl p-8 border border-[#f0e4d8] text-center">
			{#if isLoading}
				<div class="mb-6">
					<div class="animate-spin rounded-full h-16 w-16 border-b-2 border-[#ff6d3f] mx-auto"></div>
				</div>
				<h1 class="text-2xl font-semibold text-[#1f1b17] mb-2">Verifying...</h1>
				<p class="text-sm text-[#6c6b69]">Please wait while we set up your account.</p>
			{:else if success}
				<div class="mb-6">
					<div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
						<svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
						</svg>
					</div>
				</div>
				<h1 class="text-2xl font-semibold text-[#1f1b17] mb-2">Email Verified!</h1>
				<p class="text-sm text-[#6c6b69] mb-6">
					Your email has been successfully verified. Entering the app...
				</p>
			{:else}
				<div class="mb-6">
					<div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
						<svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
						</svg>
					</div>
				</div>
				<h1 class="text-2xl font-semibold text-[#1f1b17] mb-2">Verification Failed</h1>
				<p class="text-sm text-[#6c6b69] mb-6">
					{error}
				</p>
				<button
					onclick={() => goto('/sign-in-up')}
					class="w-full bg-[#1f1b17] text-white py-3 px-4 rounded-xl font-semibold hover:bg-black transition-colors"
				>
					Back to Sign In
				</button>
			{/if}
		</div>
	</div>
</div>
