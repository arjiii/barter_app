<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { authService } from '$lib/services/authService';

	let token = $state('');
	let newPassword = $state('');
	let confirmPassword = $state('');
	let showPassword = $state(false);
	let isLoading = $state(false);
	let error = $state('');
	let success = $state(false);

	onMount(() => {
		// Get token from URL query params
		token = $page.url.searchParams.get('token') || '';
		if (!token) {
			error = 'Invalid reset link. Please request a new password reset.';
		}
	});

	async function handleResetPassword(event: Event): Promise<void> {
		event.preventDefault();
		error = '';
		
		if (!newPassword || !confirmPassword) {
			error = 'Please enter and confirm your new password';
			return;
		}
		
		if (newPassword.length < 8) {
			error = 'Password must be at least 8 characters long';
			return;
		}
		
		if (newPassword !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}
		
		if (!token) {
			error = 'Invalid reset token';
			return;
		}
		
		isLoading = true;
		
		try {
			const result = await authService.resetPassword(token, newPassword);
			if (result.success) {
				success = true;
				setTimeout(() => {
					goto('/sign-in-up?mode=signin');
				}, 2000);
			} else {
				error = result.message;
			}
		} catch (err) {
			console.error('Reset password error:', err);
			error = 'An error occurred. Please try again.';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="min-h-screen bg-[#f7f5f3] flex items-center justify-center px-4 py-12 font-['Inter',sans-serif]">
	<div class="max-w-md w-full">
		<div class="bg-white rounded-2xl shadow-xl p-8 border border-[#f0e4d8]">
			{#if success}
				<div class="text-center">
					<div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
						<svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
						</svg>
					</div>
					<h1 class="text-2xl font-semibold text-[#1f1b17] mb-2">Password Reset Successful!</h1>
					<p class="text-sm text-[#6c6b69] mb-6">
						Your password has been reset. Redirecting to sign in...
					</p>
				</div>
			{:else}
				<div class="text-center mb-6">
					<h1 class="text-2xl font-semibold text-[#1f1b17] mb-2">Reset Your Password</h1>
					<p class="text-sm text-[#6c6b69]">
						Enter your new password below
					</p>
				</div>

				{#if error}
					<div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm">
						{error}
					</div>
				{/if}

				<form onsubmit={handleResetPassword} class="space-y-5">
					<div>
						<label for="new-password" class="block text-xs uppercase tracking-[0.2em] text-[#8b6b55] mb-2">
							New Password
						</label>
						<div class="relative">
							<input
								id="new-password"
								type={showPassword ? 'text' : 'password'}
								bind:value={newPassword}
								required
								minlength="8"
								class="w-full pr-12 px-4 py-3 border border-[#e3d8cf] rounded-xl bg-[#fdf9f6] focus:outline-none focus:ring-2 focus:ring-[#ffb797] focus:border-[#ff855a] transition-colors text-[#2d261f]"
								placeholder="Enter new password"
							/>
							<button 
								type="button" 
								class="absolute inset-y-0 right-3 my-auto text-gray-500 hover:text-gray-700" 
								onclick={() => showPassword = !showPassword}
								aria-label={showPassword ? 'Hide password' : 'Show password'}
							>
								{#if showPassword}
									<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-5 0-9-4-9-7 0-1.07.41-2.205 1.125-3.3M6.2 6.2A9.967 9.967 0 0112 5c5 0 9 4 9 7 0 1.07-.41 2.205-1.125 3.3M3 3l18 18M9.88 9.88A3 3 0 0012 15a3 3 0 002.12-5.12"/>
									</svg>
								{:else}
									<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
									</svg>
								{/if}
							</button>
						</div>
					</div>

					<div>
						<label for="confirm-password" class="block text-xs uppercase tracking-[0.2em] text-[#8b6b55] mb-2">
							Confirm Password
						</label>
						<input
							id="confirm-password"
							type="password"
							bind:value={confirmPassword}
							required
							minlength="8"
							class="w-full px-4 py-3 border border-[#e3d8cf] rounded-xl bg-[#fdf9f6] focus:outline-none focus:ring-2 focus:ring-[#ffb797] focus:border-[#ff855a] transition-colors text-[#2d261f]"
							placeholder="Confirm new password"
						/>
					</div>

					<button
						type="submit"
						disabled={isLoading || !token}
						class="w-full bg-[#1f1b17] text-white py-3 px-4 rounded-xl font-semibold tracking-wide hover:bg-black focus:outline-none focus:ring-2 focus:ring-[#c6b4a6] focus:ring-offset-2 focus:ring-offset-white disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
					>
						{#if isLoading}
							<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
						{/if}
						{isLoading ? 'Resetting...' : 'Reset Password'}
					</button>
				</form>

				<p class="mt-4 text-center text-sm text-[#6c6b69]">
					Remember your password?
					<a href="/sign-in-up?mode=signin" class="text-[#ff6d3f] hover:text-[#ff5724] font-medium">Sign in</a>
				</p>
			{/if}
		</div>
	</div>
</div>

