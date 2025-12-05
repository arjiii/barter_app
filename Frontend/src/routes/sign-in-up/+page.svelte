<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import type {
		LoginCredentials,
		SignUpCredentials,
		FormState,
		ValidationErrors
	} from '$lib/types/auth';
	import { authService } from '$lib/services/authService';
	import { authStore } from '$lib/stores/authStore';
	import {
		validateLoginCredentials,
		validateSignUpCredentials,
		hasValidationErrors
	} from '$lib/utils/validation';
	import LocationPermissionModal from '../components/LocationPermissionModal.svelte';

	// Form state
	let formState = $state<FormState>({
		isSignUp: false,
		isLoading: false,
		errors: {}
	});

	// Forgot password state
	let showForgotPassword = $state(false);
	let forgotPasswordEmail = $state('');
	let forgotPasswordSent = $state(false);

	// Verification state
	let verificationStep = $state(false);
	let otpCode = $state('');
	let verificationEmail = $state('');

	// Location permission state
	let showLocationModal = $state(false);

	// Form data
	let formData = $state<any>({
		name: '',
		email: '',
		password: '',
		confirmPassword: '',
		rememberMe: false,
		location: '',
		latitude: null,
		longitude: null
	});

	// UI state
	let showPassword = $state(false);
	let showConfirmPassword = $state(false);

	// Respect mode query param
	$effect(() => {
		const mode = $page.url.searchParams.get('mode');
		if (mode === 'signup') {
			formState.isSignUp = true;
		} else if (mode === 'signin') {
			formState.isSignUp = false;
		}
	});

	function toggleMode(): void {
		formState.isSignUp = !formState.isSignUp;
		formState.errors = {};
		verificationStep = false;
	}

	function detectLocation() {
		if ('geolocation' in navigator) {
			formState.isLoading = true;
			navigator.geolocation.getCurrentPosition(
				(position) => {
					formData.latitude = position.coords.latitude;
					formData.longitude = position.coords.longitude;
					// Simple coordinate string for display, ideally reverse geocode
					formData.location = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
					formState.isLoading = false;
				},
				(err) => {
					console.error('Geolocation error:', err);
					formState.errors = { general: 'Could not detect location. Please enter manually.' };
					formState.isLoading = false;
				}
			);
		} else {
			formState.errors = { general: 'Geolocation is not supported by your browser.' };
		}
	}

	async function handleSubmit(event: Event): Promise<void> {
		event.preventDefault();
		formState.isLoading = true;
		formState.errors = {};

		try {
			let validationErrors: ValidationErrors = {};

			if (formState.isSignUp) {
				validationErrors = validateSignUpCredentials(formData as SignUpCredentials);
			} else {
				validationErrors = validateLoginCredentials(formData as LoginCredentials);
			}

			if (hasValidationErrors(validationErrors)) {
				formState.errors = validationErrors;
				formState.isLoading = false;
				return;
			}

			const response = formState.isSignUp
				? await authService.signUp(formData as SignUpCredentials)
				: await authService.signIn(formData as LoginCredentials);

			if (response.success) {
				if (formState.isSignUp) {
					// Check verification method
					if (response.message && response.message.includes('admin')) {
						alert('Registration request submitted! Please wait for admin approval.');
						formState.isSignUp = false; // Switch to login
						// Reset form
						formData = {
							email: '',
							password: '',
							confirmPassword: '',
							name: '',
							location: '',
							rememberMe: false,
							verificationMethod: 'email'
						};
						formState.isLoading = false;
						return;
					}

					// For signup, we expect verification step next
					// User is NOT logged in yet
					alert('Verification code sent! Please check your email.');
					verificationStep = true;
					verificationEmail = formData.email;
					formState.isLoading = false;
					return;
				}

				// For signin, we expect user and token
				if (response.user) {
					authStore.setUser(response.user);
					await goto('/discovery');
				} else {
					formState.errors = {
						general: 'Login successful but user data missing.'
					};
				}
			} else {
				formState.errors = {
					general: response.message || 'Authentication failed'
				};
			}
		} catch (error) {
			console.error('Authentication error:', error);
			formState.errors = {
				general: 'An unexpected error occurred. Please try again.'
			};
		} finally {
			formState.isLoading = false;
		}
	}

	async function handleVerification(event: Event): Promise<void> {
		event.preventDefault();
		formState.isLoading = true;
		formState.errors = {};

		if (!otpCode.trim() || otpCode.trim().length !== 6) {
			formState.errors = { general: 'Please enter a valid 6-digit code.' };
			formState.isLoading = false;
			return;
		}

		try {
			const response = await authService.verifyEmail(verificationEmail, otpCode);

			if (response.success) {
				// After email verification, user is created and logged in
				if (response.user) {
					authStore.setUser(response.user);
				}

				// Show location permission modal
				verificationStep = false;
				showLocationModal = true;
			} else {
				formState.errors = {
					general: response.message || 'Verification failed. Please check your code.'
				};
			}
		} catch (error) {
			console.error('Verification error:', error);
			formState.errors = {
				general: 'An unexpected error occurred during verification. Please try again.'
			};
		} finally {
			formState.isLoading = false;
		}
	}

	async function handleLocationComplete(location: {
		city: string;
		radius: number;
		lat: number;
		lng: number;
	}) {
		try {
			// Update user location via API
			// We need to pass the name as well, which should be in formData
			if (formData.name) {
				await authService.updateProfile(formData.name, location.city, location.lat, location.lng);
			}
		} catch (error) {
			console.error('Failed to update location:', error);
		}

		showLocationModal = false;
		// Clear the auth token since user needs to sign in again
		localStorage.removeItem('bayanihan_token');
		authStore.clearAuth();

		alert('Account verified successfully! Please sign in to continue.');
		formState.isSignUp = false; // Switch to sign in mode
		otpCode = ''; // Clear OTP
	}

	function handleLocationSkip() {
		showLocationModal = false;
		// Clear the auth token since user needs to sign in again
		localStorage.removeItem('bayanihan_token');
		authStore.clearAuth();

		alert('Account verified! Please sign in to continue.');
		formState.isSignUp = false; // Switch to sign in mode
		otpCode = ''; // Clear OTP
	}

	async function handleForgotPassword(event: Event): Promise<void> {
		event.preventDefault();
		if (!forgotPasswordEmail.trim()) {
			formState.errors = { general: 'Please enter your email address' };
			return;
		}

		formState.isLoading = true;
		formState.errors = {};

		try {
			const result = await authService.requestPasswordReset(forgotPasswordEmail.trim());
			if (result.success) {
				forgotPasswordSent = true;
			} else {
				formState.errors = { general: result.message };
			}
		} catch (error) {
			console.error('Forgot password error:', error);
			formState.errors = { general: 'An error occurred. Please try again.' };
		} finally {
			formState.isLoading = false;
		}
	}

	async function handleSocialLogin(provider: string) {
		alert(`${provider} login not implemented yet`);
	}

	onMount(() => {
		authStore.initializeAuth();
	});
</script>

<div class="flex min-h-screen bg-[#f7f5f3] font-['Inter',sans-serif] text-[#1c1816]">
	<!-- Left Side - Welcome Section -->
	<div
		class="hidden flex-col justify-center border-r border-[#f1d5c6] bg-gradient-to-br from-[#fbe4d5] via-[#f7d2c3] to-[#f7c9b6] px-12 py-16 text-[#43291b] lg:flex lg:w-5/12"
	>
		<div class="mb-8">
			<div
				class="mb-4 flex h-11 w-11 items-center justify-center rounded-full bg-white/90 shadow-sm"
			>
				<svg class="h-6 w-6 text-[#ff6d3f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
					></path>
				</svg>
			</div>
			<h1 class="text-2xl font-semibold tracking-tight">Bayanihan Exchange</h1>
			<p class="text-sm text-[#674c3b]">Blockchain-Powered Community Barter</p>
		</div>

		<div class="max-w-md space-y-6">
			<h2 class="text-3xl font-semibold leading-tight">
				{formState.isSignUp ? 'Join our Bayanihan Community' : 'Welcome back, Kabayan!'}
			</h2>
			<p class="text-base text-[#6c4d3a]">
				{formState.isSignUp
					? 'Start your journey with us and join our community of neighbors helping neighbors through blockchain-powered bartering.'
					: 'Continue your journey in our community where neighbors help neighbors through secure blockchain trading.'}
			</p>

			<button
				type="button"
				onclick={toggleMode}
				class="inline-flex items-center gap-2 rounded-full bg-white/90 px-5 py-2.5 font-semibold text-[#ff6d3f] shadow-sm transition-colors duration-200 hover:bg-white"
			>
				<span
					>{formState.isSignUp
						? 'Already have an account? Sign in'
						: 'New to Bayanihan? Sign up'}</span
				>
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"
					><path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M13 7l5 5-5 5M6 12h12"
					/></svg
				>
			</button>
		</div>
	</div>

	<!-- Right Side - Form Section -->
	<div class="flex w-full flex-col justify-center bg-[#fffdfb] px-6 py-10 sm:px-10 lg:w-7/12">
		<div class="mx-auto w-full max-w-md">
			<div class="mb-6 text-center">
				<h2 class="mb-2 text-[1.65rem] font-semibold tracking-tight text-[#1f1b17]">
					{#if verificationStep}
						Verify Your Email
					{:else}
						{formState.isSignUp ? 'Create Account' : 'Sign In'}
					{/if}
				</h2>
				<p class="text-sm text-[#6c6b69]">
					{#if verificationStep}
						Enter the 6-digit code sent to {verificationEmail}
					{:else}
						{formState.isSignUp
							? 'Join the Bayanihan community today'
							: 'Welcome back to Bayanihan Exchange'}
					{/if}
				</p>
			</div>

			<div
				class="rounded-2xl border border-[#f0e4d8] bg-white/95 px-6 py-7 shadow-[0_10px_40px_rgba(31,24,22,0.08)]"
			>
				{#if formState.errors.general}
					<div class="mb-4 rounded-lg border border-red-400 bg-red-100 p-3 text-red-700">
						{formState.errors.general}
					</div>
				{/if}

				<form class="space-y-5" onsubmit={verificationStep ? handleVerification : handleSubmit}>
					{#if verificationStep}
						<div>
							<label for="otp" class="mb-2 block text-xs uppercase tracking-[0.2em] text-[#8b6b55]">
								Verification Code
							</label>
							<input
								id="otp"
								name="otp"
								type="text"
								bind:value={otpCode}
								class="w-full border px-4 py-3 {formState.errors.general
									? 'border-[#f9735b]'
									: 'border-[#e3d8cf]'} rounded-xl bg-[#fdf9f6] text-center text-2xl tracking-widest text-[#2d261f] transition-colors focus:border-[#ff855a] focus:outline-none focus:ring-2 focus:ring-[#ffb797]"
								placeholder="000000"
								maxlength="6"
							/>
						</div>

						<div>
							<button
								type="submit"
								disabled={formState.isLoading}
								class="w-full rounded-xl bg-[#1f1b17] px-4 py-3 font-semibold tracking-wide text-white transition-all duration-200 hover:bg-black focus:outline-none focus:ring-2 focus:ring-[#c6b4a6] focus:ring-offset-2 focus:ring-offset-white disabled:cursor-not-allowed disabled:opacity-50"
							>
								{formState.isLoading ? 'Verifying...' : 'VERIFY EMAIL'}
							</button>
						</div>
					{:else}
						{#if formState.isSignUp}
							<div>
								<label
									for="name"
									class="mb-2 block text-xs uppercase tracking-[0.2em] text-[#8b6b55]"
								>
									Full Name
								</label>
								<input
									id="name"
									name="name"
									type="text"
									bind:value={formData.name}
									class="w-full border px-4 py-3 {formState.errors.name
										? 'border-[#f9735b]'
										: 'border-[#e3d8cf]'} rounded-xl bg-[#fdf9f6] text-[#2d261f] transition-colors focus:border-[#ff855a] focus:outline-none focus:ring-2 focus:ring-[#ffb797]"
									placeholder="Enter your full name"
								/>
								{#if formState.errors.name}
									<p class="mt-1 text-sm text-red-600">{formState.errors.name}</p>
								{/if}
							</div>

							<div>
								<label
									for="location"
									class="mb-2 block text-xs uppercase tracking-[0.2em] text-[#8b6b55]"
								>
									Location
								</label>
								<div class="flex gap-2">
									<input
										id="location"
										name="location"
										type="text"
										bind:value={formData.location}
										class="w-full border px-4 py-3 {formState.errors.general &&
										formState.errors.general.includes('location')
											? 'border-[#f9735b]'
											: 'border-[#e3d8cf]'} rounded-xl bg-[#fdf9f6] text-[#2d261f] transition-colors focus:border-[#ff855a] focus:outline-none focus:ring-2 focus:ring-[#ffb797]"
										placeholder="City, Province"
									/>
									<button
										type="button"
										onclick={detectLocation}
										class="rounded-xl bg-[#e3d8cf] px-4 py-3 text-[#4d4138] transition-colors hover:bg-[#d9c7ba]"
										title="Detect Location"
										aria-label="Detect Location"
									>
										<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
											></path>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
											></path>
										</svg>
									</button>
								</div>
							</div>
						{/if}

						<div>
							<label
								for="email"
								class="mb-2 block text-xs uppercase tracking-[0.2em] text-[#8b6b55]"
							>
								Email Address
							</label>
							<input
								id="email"
								name="email"
								type="email"
								autocomplete="email"
								bind:value={formData.email}
								class="w-full border px-4 py-3 {formState.errors.email
									? 'border-[#f9735b]'
									: 'border-[#e3d8cf]'} rounded-xl bg-[#fdf9f6] text-[#2d261f] transition-colors focus:border-[#ff855a] focus:outline-none focus:ring-2 focus:ring-[#ffb797]"
								placeholder="Enter your email address"
							/>
							{#if formState.errors.email}
								<p class="mt-1 text-sm text-red-600">{formState.errors.email}</p>
							{/if}
						</div>

						<div>
							<label
								for="password"
								class="mb-2 block text-xs uppercase tracking-[0.2em] text-[#8b6b55]"
							>
								Password
							</label>
							<div class="relative">
								<input
									id="password"
									name="password"
									type={showPassword ? 'text' : 'password'}
									autocomplete={formState.isSignUp ? 'new-password' : 'current-password'}
									bind:value={formData.password}
									class="w-full border px-4 py-3 pr-12 {formState.errors.password
										? 'border-[#f9735b]'
										: 'border-[#e3d8cf]'} rounded-xl bg-[#fdf9f6] text-[#2d261f] transition-colors focus:border-[#ff855a] focus:outline-none focus:ring-2 focus:ring-[#ffb797]"
									placeholder="Password"
								/>
								<button
									type="button"
									class="absolute inset-y-0 right-3 my-auto text-gray-500 hover:text-gray-700"
									onclick={() => (showPassword = !showPassword)}
									aria-label={showPassword ? 'Hide password' : 'Show password'}
								>
									{#if showPassword}
										<svg
											xmlns="http://www.w3.org/2000/svg"
											class="h-5 w-5"
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
											><path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M13.875 18.825A10.05 10.05 0 0112 19c-5 0-9-4-9-7 0-1.07.41-2.205 1.125-3.3M6.2 6.2A9.967 9.967 0 0112 5c5 0 9 4 9 7 0 1.07-.41 2.205-1.125 3.3M3 3l18 18M9.88 9.88A3 3 0 0012 15a3 3 0 002.12-5.12"
											/></svg
										>
									{:else}
										<svg
											xmlns="http://www.w3.org/2000/svg"
											class="h-5 w-5"
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
											><path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
											/><path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
											/></svg
										>
									{/if}
								</button>
							</div>
							{#if formState.errors.password}
								<p class="mt-1 text-sm text-red-600">{formState.errors.password}</p>
							{/if}
						</div>

						{#if formState.isSignUp}
							<div>
								<label
									for="confirm-password"
									class="mb-2 block text-xs uppercase tracking-[0.2em] text-[#8b6b55]"
								>
									Confirm Password
								</label>
								<div class="relative">
									<input
										id="confirm-password"
										name="confirm-password"
										type={showConfirmPassword ? 'text' : 'password'}
										autocomplete="new-password"
										bind:value={formData.confirmPassword}
										class="w-full border px-4 py-3 pr-12 {formState.errors.confirmPassword
											? 'border-[#f9735b]'
											: 'border-[#e3d8cf]'} rounded-xl bg-[#fdf9f6] text-[#2d261f] transition-colors focus:border-[#ff855a] focus:outline-none focus:ring-2 focus:ring-[#ffb797]"
										placeholder="Confirm your password"
									/>
									<button
										type="button"
										class="absolute inset-y-0 right-3 my-auto text-gray-500 hover:text-gray-700"
										onclick={() => (showConfirmPassword = !showConfirmPassword)}
										aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
									>
										{#if showConfirmPassword}
											<svg
												xmlns="http://www.w3.org/2000/svg"
												class="h-5 w-5"
												fill="none"
												viewBox="0 0 24 24"
												stroke="currentColor"
												><path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M13.875 18.825A10.05 10.05 0 0112 19c-5 0-9-4-9-7 0-1.07.41-2.205 1.125-3.3M6.2 6.2A9.967 9.967 0 0112 5c5 0 9 4 9 7 0 1.07-.41 2.205-1.125 3.3M3 3l18 18M9.88 9.88A3 3 0 0012 15a3 3 0 002.12-5.12"
												/></svg
											>
										{:else}
											<svg
												xmlns="http://www.w3.org/2000/svg"
												class="h-5 w-5"
												fill="none"
												viewBox="0 0 24 24"
												stroke="currentColor"
												><path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
												/><path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
												/></svg
											>
										{/if}
									</button>
								</div>
								{#if formState.errors.confirmPassword}
									<p class="mt-1 text-sm text-red-600">{formState.errors.confirmPassword}</p>
								{/if}
							</div>
						{/if}

						{#if formState.isSignUp}
							<div class="mt-4 space-y-2">
								<label class="mb-2 block text-xs uppercase tracking-[0.2em] text-[#8b6b55]">
									Verification Method
								</label>
								<div class="flex flex-col space-y-2">
									<div class="flex items-center space-x-2">
										<input
											type="radio"
											id="verify-email"
											name="verificationMethod"
											value="email"
											bind:group={formData.verificationMethod}
											class="text-primary focus:ring-primary h-4 w-4 border-gray-300"
										/>
										<label for="verify-email" class="text-sm font-normal text-[#4d4138]"
											>Verify via Email (Instant)</label
										>
									</div>
									<div class="flex items-center space-x-2">
										<input
											type="radio"
											id="verify-admin"
											name="verificationMethod"
											value="admin"
											bind:group={formData.verificationMethod}
											class="text-primary focus:ring-primary h-4 w-4 border-gray-300"
										/>
										<label for="verify-admin" class="text-sm font-normal text-[#4d4138]"
											>Verify via Admin Request (Manual Approval)</label
										>
									</div>
								</div>
							</div>
						{/if}

						{#if !formState.isSignUp}
							<div class="flex items-center justify-between text-sm">
								<div class="flex items-center">
									<input
										id="remember-me"
										name="remember-me"
										type="checkbox"
										bind:checked={formData.rememberMe}
										class="h-4 w-4 rounded border-[#d9c7ba] text-[#ff6d3f] focus:ring-[#ffb797]"
									/>
									<label for="remember-me" class="ml-2 text-[#4d4138]"> Remember me </label>
								</div>

								<div>
									<button
										type="button"
										class="font-medium text-[#ff6d3f] transition-colors hover:text-[#ff5724]"
										onclick={() => (showForgotPassword = true)}
									>
										Forgot Password?
									</button>
								</div>
							</div>
						{/if}

						<div>
							<button
								type="submit"
								disabled={formState.isLoading}
								class="w-full rounded-xl bg-[#1f1b17] px-4 py-3 font-semibold tracking-wide text-white transition-all duration-200 hover:bg-black focus:outline-none focus:ring-2 focus:ring-[#c6b4a6] focus:ring-offset-2 focus:ring-offset-white disabled:cursor-not-allowed disabled:opacity-50"
							>
								{#if formState.isLoading}
									<svg
										class="-ml-1 mr-3 inline h-5 w-5 animate-spin text-white"
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
								{/if}
								{formState.isLoading ? 'Processing...' : formState.isSignUp ? 'SIGN UP' : 'SIGN IN'}
							</button>
							<p class="mt-3 text-center text-sm text-[#6c6b69]">
								{formState.isSignUp ? 'Already have an account?' : "Don't have an account?"}
								<button
									type="button"
									class="ml-1 font-medium text-[#ff6d3f] hover:text-[#ff5724]"
									onclick={toggleMode}
								>
									{formState.isSignUp ? 'Sign in' : 'Sign up'}
								</button>
							</p>
						</div>
					{/if}
				</form>

				<div class="mt-5">
					<div class="relative">
						<div class="absolute inset-0 flex items-center">
							<div class="w-full border-t border-gray-300"></div>
						</div>
						<div class="relative flex justify-center text-sm">
							<span class="bg-white px-2 text-xs uppercase tracking-[0.3em] text-[#8a7c72]"
								>Or connect</span
							>
						</div>
					</div>

					<div class="mt-5 grid grid-cols-3 gap-3">
						<button
							type="button"
							onclick={() => handleSocialLogin('google')}
							aria-label="Sign in with Google"
							class="inline-flex w-full justify-center rounded-xl border border-[#dfd4cb] bg-white/90 px-4 py-3 text-sm font-medium text-[#4b433d] transition-all duration-200 hover:bg-white"
						>
							<svg class="h-5 w-5" viewBox="0 0 24 24"
								><path
									fill="currentColor"
									d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
								/><path
									fill="currentColor"
									d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
								/><path
									fill="currentColor"
									d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
								/><path
									fill="currentColor"
									d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
								/></svg
							>
						</button>
						<button
							type="button"
							onclick={() => handleSocialLogin('apple')}
							aria-label="Sign in with Apple"
							class="inline-flex w-full justify-center rounded-xl border border-[#dfd4cb] bg-white/90 px-4 py-3 text-sm font-medium text-[#4b433d] transition-all duration-200 hover:bg-white"
						>
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"
								><path
									d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"
								/></svg
							>
						</button>
						<button
							type="button"
							onclick={() => handleSocialLogin('facebook')}
							aria-label="Sign in with Facebook"
							class="inline-flex w-full justify-center rounded-xl border border-[#dfd4cb] bg-white/90 px-4 py-3 text-sm font-medium text-[#4b433d] transition-all duration-200 hover:bg-white"
						>
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"
								><path
									d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
								/></svg
							>
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<!-- Forgot Password Modal -->
{#if showForgotPassword}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
		role="dialog"
		aria-labelledby="forgot-password-title"
		onclick={() => {
			if (!forgotPasswordSent) showForgotPassword = false;
		}}
		onkeydown={(e) => e.key === 'Escape' && !forgotPasswordSent && (showForgotPassword = false)}
	>
		<div
			class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl"
			onclick={(e) => e.stopPropagation()}
			role="document"
		>
			{#if !forgotPasswordSent}
				<h2 id="forgot-password-title" class="mb-4 text-2xl font-semibold text-[#1f1b17]">
					Forgot Password?
				</h2>
				<p class="mb-6 text-sm text-[#6c6b69]">
					Enter your email address and we'll send you a link to reset your password.
				</p>
				<form onsubmit={handleForgotPassword} class="space-y-4">
					<div>
						<label
							for="forgot-email"
							class="mb-2 block text-xs uppercase tracking-[0.2em] text-[#8b6b55]"
						>
							Email Address
						</label>
						<input
							id="forgot-email"
							type="email"
							bind:value={forgotPasswordEmail}
							required
							class="w-full rounded-xl border border-[#e3d8cf] bg-[#fdf9f6] px-4 py-3 text-[#2d261f] transition-colors focus:border-[#ff855a] focus:outline-none focus:ring-2 focus:ring-[#ffb797]"
							placeholder="Enter your email"
						/>
					</div>
					{#if formState.errors.general}
						<div class="rounded-lg border border-red-400 bg-red-100 p-3 text-sm text-red-700">
							{formState.errors.general}
						</div>
					{/if}
					<div class="flex gap-3">
						<button
							type="button"
							onclick={() => {
								showForgotPassword = false;
								forgotPasswordEmail = '';
								formState.errors = {};
							}}
							class="flex-1 rounded-xl border border-[#e3d8cf] px-4 py-3 text-[#4d4138] transition-colors hover:bg-[#fdf9f6]"
						>
							Cancel
						</button>
						<button
							type="submit"
							disabled={formState.isLoading}
							class="flex-1 rounded-xl bg-[#1f1b17] px-4 py-3 font-semibold text-white transition-colors hover:bg-black disabled:cursor-not-allowed disabled:opacity-50"
						>
							{formState.isLoading ? 'Sending...' : 'Send Reset Link'}
						</button>
					</div>
				</form>
			{:else}
				<div class="text-center">
					<div
						class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100"
					>
						<svg
							class="h-8 w-8 text-green-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M5 13l4 4L19 7"
							></path>
						</svg>
					</div>
					<h2 class="mb-2 text-2xl font-semibold text-[#1f1b17]">Check Your Email</h2>
					<p class="mb-6 text-sm text-[#6c6b69]">
						We've sent a password reset link to <strong>{forgotPasswordEmail}</strong>
					</p>
					<button
						onclick={() => {
							showForgotPassword = false;
							forgotPasswordEmail = '';
							forgotPasswordSent = false;
							formState.errors = {};
						}}
						class="w-full rounded-xl bg-[#1f1b17] px-4 py-3 font-semibold text-white transition-colors hover:bg-black"
					>
						Close
					</button>
				</div>
			{/if}
		</div>
	</div>
{/if}

<!-- Location Permission Modal -->
<LocationPermissionModal
	isOpen={showLocationModal}
	onComplete={handleLocationComplete}
	onSkip={handleLocationSkip}
/>
