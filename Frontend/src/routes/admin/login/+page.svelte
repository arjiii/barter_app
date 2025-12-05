<script lang="ts">
	import { goto } from '$app/navigation';
	import { authService } from '$lib/services/authService';
	import { authStore } from '$lib/stores/authStore';

	let email = $state('');
	let password = $state('');
	let isLoading = $state(false);
	let error: string | null = $state(null);

	async function handleLogin(e: Event) {
		e.preventDefault();
		isLoading = true;
		error = null;

		try {
			const response = await authService.signIn({ email, password });

			if (response.success && response.user) {
				if (response.user.role === 'admin') {
					authStore.setUser(response.user);
					goto('/admin');
				} else {
					// User is not an admin
					await authService.signOut();
					error = 'Access Denied: You do not have administrator privileges.';
				}
			} else {
				error = response.message || 'Login failed';
			}
		} catch (err) {
			console.error('Admin login error:', err);
			error = 'An unexpected error occurred.';
		} finally {
			isLoading = false;
		}
	}
</script>

<div
	class="flex min-h-screen items-center justify-center bg-[#0f0f13] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#2a2420] via-[#0f0f13] to-[#000000] px-4 py-12 font-['Inter',sans-serif] sm:px-6 lg:px-8"
>
	<div class="w-full max-w-md space-y-8">
		<!-- Logo Section -->
		<div class="text-center">
			<div
				class="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-[#ff6d3f] to-[#ff8f6b] shadow-lg shadow-orange-500/20"
			>
				<svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
					></path>
				</svg>
			</div>
			<h2 class="mt-6 text-3xl font-bold tracking-tight text-white">Admin Portal</h2>
			<p class="mt-2 text-sm text-gray-400">Secure access for Bayanihan Exchange administrators</p>
		</div>

		<!-- Login Card -->
		<div
			class="rounded-3xl bg-white/5 p-8 shadow-2xl ring-1 ring-white/10 backdrop-blur-xl sm:p-10"
		>
			<form class="space-y-6" onsubmit={handleLogin}>
				<div>
					<label for="email" class="block text-sm font-medium leading-6 text-gray-300"
						>Email Address</label
					>
					<div class="relative mt-2">
						<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
							<svg
								class="h-5 w-5 text-gray-500"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="1.5"
									d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
								/>
							</svg>
						</div>
						<input
							id="email"
							name="email"
							type="email"
							autocomplete="email"
							required
							bind:value={email}
							class="block w-full rounded-xl border-0 bg-white/5 py-3 pl-10 text-white shadow-sm ring-1 ring-inset ring-white/10 placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-[#ff6d3f] sm:text-sm sm:leading-6"
							placeholder="admin@bayanihan.com"
						/>
					</div>
				</div>

				<div>
					<label for="password" class="block text-sm font-medium leading-6 text-gray-300"
						>Password</label
					>
					<div class="relative mt-2">
						<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
							<svg
								class="h-5 w-5 text-gray-500"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="1.5"
									d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
								/>
							</svg>
						</div>
						<input
							id="password"
							name="password"
							type="password"
							autocomplete="current-password"
							required
							bind:value={password}
							class="block w-full rounded-xl border-0 bg-white/5 py-3 pl-10 text-white shadow-sm ring-1 ring-inset ring-white/10 placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-[#ff6d3f] sm:text-sm sm:leading-6"
							placeholder="••••••••"
						/>
					</div>
				</div>

				{#if error}
					<div class="rounded-xl bg-red-500/10 p-4 ring-1 ring-red-500/20">
						<div class="flex">
							<div class="flex-shrink-0">
								<svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
									<path
										fill-rule="evenodd"
										d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
										clip-rule="evenodd"
									/>
								</svg>
							</div>
							<div class="ml-3">
								<h3 class="text-sm font-medium text-red-400">{error}</h3>
							</div>
						</div>
					</div>
				{/if}

				<div>
					<button
						type="submit"
						disabled={isLoading}
						class="flex w-full justify-center rounded-xl bg-gradient-to-r from-[#ff6d3f] to-[#ff8f6b] px-3 py-3.5 text-sm font-semibold text-white shadow-sm transition-all duration-200 hover:from-[#e55a2f] hover:to-[#e57a5b] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ff6d3f] disabled:cursor-not-allowed disabled:opacity-70"
					>
						{#if isLoading}
							<svg
								class="mr-2 h-5 w-5 animate-spin text-white"
								xmlns="http://www.w3.org/2000/svg"
								fill="none"
								viewBox="0 0 24 24"
							>
								<circle
									class="opacity-25"
									cx="12"
									cy="12"
									r="10"
									stroke="currentColor"
									stroke-width="4"
								></circle>
								<path
									class="opacity-75"
									fill="currentColor"
									d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
								></path>
							</svg>
							Authenticating...
						{:else}
							Sign in to Dashboard
						{/if}
					</button>
				</div>
			</form>
		</div>

		<p class="text-center text-xs text-gray-500">
			&copy; {new Date().getFullYear()} Bayanihan Exchange. Authorized personnel only.
		</p>
	</div>
</div>
