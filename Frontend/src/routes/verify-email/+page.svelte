<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { authService } from '$lib/services/authService';

	let token = $state('');
	let isLoading = $state(true);
	let success = $state(false);
	let error = $state('');

	onMount(async () => {
		// Get token from URL query params
		token = $page.url.searchParams.get('token') || '';
		
		if (!token) {
			error = 'Invalid verification link. Please request a new verification email.';
			isLoading = false;
			return;
		}
		
		// Automatically verify email
		try {
			const result = await authService.verifyEmail(token);
			if (result.success) {
				success = true;
				setTimeout(() => {
					goto('/sign-in-up?mode=signin');
				}, 3000);
			} else {
				error = result.message;
			}
		} catch (err) {
			console.error('Verify email error:', err);
			error = 'An error occurred while verifying your email. Please try again.';
		} finally {
			isLoading = false;
		}
	});
</script>

<div class="min-h-screen bg-[#f7f5f3] flex items-center justify-center px-4 py-12 font-['Inter',sans-serif]">
	<div class="max-w-md w-full">
		<div class="bg-white rounded-2xl shadow-xl p-8 border border-[#f0e4d8] text-center">
			{#if isLoading}
				<div class="mb-6">
					<div class="animate-spin rounded-full h-16 w-16 border-b-2 border-[#ff6d3f] mx-auto"></div>
				</div>
				<h1 class="text-2xl font-semibold text-[#1f1b17] mb-2">Verifying Your Email</h1>
				<p class="text-sm text-[#6c6b69]">Please wait...</p>
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
					Your email has been successfully verified. Redirecting to sign in...
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
					{error || 'The verification link is invalid or has expired.'}
				</p>
				<div class="space-y-3">
					<button
						onclick={() => goto('/sign-in-up?mode=signin')}
						class="w-full bg-[#1f1b17] text-white py-3 px-4 rounded-xl font-semibold hover:bg-black transition-colors"
					>
						Go to Sign In
					</button>
					<button
						onclick={() => goto('/sign-in-up?mode=signup')}
						class="w-full border border-[#e3d8cf] text-[#4d4138] py-3 px-4 rounded-xl font-semibold hover:bg-[#fdf9f6] transition-colors"
					>
						Create New Account
					</button>
				</div>
			{/if}
		</div>
	</div>
</div>


