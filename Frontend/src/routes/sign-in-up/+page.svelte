<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import type { LoginCredentials, SignUpCredentials, FormState, ValidationErrors } from '$lib/types/auth';
	import { authService } from '$lib/services/authService';
	import { authStore } from '$lib/stores/authStore';
	import { 
		validateLoginCredentials, 
		validateSignUpCredentials, 
		hasValidationErrors 
	} from '$lib/utils/validation';

	// Form state
	let formState = $state<FormState>({
		isSignUp: false,
		isLoading: false,
		errors: {}
	});

	// Form data - use any type to handle both login and signup
	let formData = $state<any>({
		email: '',
		password: '',
		rememberMe: false
	});

	// UI state
	let showPassword = $state(false);
	let showConfirmPassword = $state(false);

	// Reactive form data based on mode
	$effect(() => {
		if (formState.isSignUp) {
			formData = {
				name: '',
				email: '',
				password: '',
				confirmPassword: ''
			};
		} else {
			formData = {
				email: '',
				password: '',
				rememberMe: false
			};
		}
	});

	/**
	 * Toggle between sign in and sign up modes
	 */
	function toggleMode(): void {
		formState.isSignUp = !formState.isSignUp;
		formState.errors = {};
	}

	/**
	 * Handle form submission
	 */
	async function handleSubmit(event: Event): Promise<void> {
		event.preventDefault();
		formState.isLoading = true;
		formState.errors = {};

		try {
			let validationErrors: ValidationErrors = {};

			// Validate form data
			if (formState.isSignUp) {
				validationErrors = validateSignUpCredentials(formData as SignUpCredentials);
			} else {
				validationErrors = validateLoginCredentials(formData as LoginCredentials);
			}

			// Check for validation errors
			if (hasValidationErrors(validationErrors)) {
				formState.errors = validationErrors;
				return;
			}

			// Call authentication service
			const response = formState.isSignUp 
				? await authService.signUp(formData as SignUpCredentials)
				: await authService.signIn(formData as LoginCredentials);

			if (response.success && response.user) {
				// Update auth store
				authStore.setUser(response.user);
				
				// Redirect to dashboard
				await goto('/discovery');
			} else {
				// Handle authentication errors
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

	/**
	 * Handle social login
	 */
	async function handleSocialLogin(provider: 'google' | 'apple' | 'facebook'): Promise<void> {
		try {
			formState.isLoading = true;
			// Implement social login logic here
			console.log(`Social login with ${provider}`);
			// For now, just show a message
			alert(`${provider} login not implemented yet`);
		} catch (error) {
			console.error('Social login error:', error);
		} finally {
			formState.isLoading = false;
		}
	}

	onMount(() => {
		// Initialize auth state
		authStore.initializeAuth();
	});
</script>

<div class="min-h-screen bg-red-600 flex">
	<!-- Left Side - Welcome Section -->
	<div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-red-500 to-red-700 flex-col justify-center px-12 text-white">
		<!-- Logo -->
		<div class="mb-8">
			<div class="w-12 h-12 bg-white rounded-lg flex items-center justify-center mb-4">
				<svg class="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
				</svg>
			</div>
			<h1 class="text-3xl font-bold">Bayanihan Exchange</h1>
			<p class="text-red-100 text-sm">Blockchain-Powered Community Barter</p>
		</div>

		<!-- Welcome Content -->
		<div class="max-w-md">
		<h2 class="text-4xl font-bold mb-4">
			{formState.isSignUp ? 'Join our Bayanihan Community' : 'Welcome back, Kabayan!'}
		</h2>
		<p class="text-lg text-red-100 mb-8">
			{formState.isSignUp ? 'Start your journey with us and join our community of neighbors helping neighbors through blockchain-powered bartering.' : 'Continue your journey in our community where neighbors help neighbors through secure blockchain trading.'}
		</p>
		
		<button 
			type="button" 
			onclick={toggleMode}
			class="bg-white text-red-600 px-6 py-3 rounded-lg font-semibold hover:bg-red-50 transition-colors duration-200"
		>
			{formState.isSignUp ? 'Already have an account? Sign in' : 'New to Bayanihan? Sign up'}
		</button>
		</div>

		<!-- Illustration Area -->
		<div class="mt-12 flex justify-center">
			<div class="relative">
				<!-- Rocket with person illustration -->
				<div class="w-64 h-64 bg-gradient-to-t from-red-400 to-red-300 rounded-full flex items-end justify-center relative overflow-hidden">
					<!-- Person on rocket -->
					<div class="absolute bottom-8 left-1/2 transform -translate-x-1/2">
						<!-- Person -->
						<div class="w-16 h-20 bg-orange-400 rounded-t-full relative">
							<!-- Head -->
							<div class="w-8 h-8 bg-yellow-200 rounded-full absolute -top-4 left-1/2 transform -translate-x-1/2"></div>
							<!-- Arms -->
							<div class="w-3 h-8 bg-orange-400 rounded-full absolute -left-2 top-2 transform rotate-12"></div>
							<div class="w-3 h-8 bg-orange-400 rounded-full absolute -right-2 top-2 transform -rotate-12"></div>
						</div>
						<!-- Rocket body -->
						<div class="w-20 h-24 bg-gradient-to-t from-red-600 to-red-500 rounded-t-lg relative">
							<!-- Rocket stripes -->
							<div class="absolute top-4 left-0 right-0 h-2 bg-white"></div>
							<div class="absolute top-8 left-0 right-0 h-2 bg-white"></div>
							<!-- Rocket flames -->
							<div class="absolute -bottom-4 left-1/2 transform -translate-x-1/2">
								<div class="w-0 h-0 border-l-4 border-r-4 border-t-8 border-transparent border-t-yellow-300"></div>
								<div class="w-0 h-0 border-l-3 border-r-3 border-t-6 border-transparent border-t-orange-400 absolute top-1 left-1/2 transform -translate-x-1/2"></div>
							</div>
						</div>
					</div>
					<!-- Clouds -->
					<div class="absolute -bottom-2 -left-4 w-8 h-4 bg-white rounded-full opacity-80"></div>
					<div class="absolute -bottom-1 -right-6 w-6 h-3 bg-white rounded-full opacity-80"></div>
					<div class="absolute -bottom-3 left-1/2 transform -translate-x-1/2 w-10 h-5 bg-white rounded-full opacity-80"></div>
				</div>
			</div>
		</div>
	</div>

	<!-- Right Side - Form Section -->
	<div class="w-full lg:w-1/2 bg-white flex flex-col justify-center px-8 py-12">
		<!-- Mobile Logo -->
		<div class="lg:hidden mb-8 text-center">
			<div class="w-12 h-12 bg-red-600 rounded-lg flex items-center justify-center mx-auto mb-4">
				<svg class="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
				</svg>
			</div>
			<h1 class="text-2xl font-bold text-gray-900">Bayanihan Exchange</h1>
			<p class="text-sm text-gray-600">Blockchain-Powered Community Barter</p>
		</div>

		<div class="max-w-md mx-auto w-full">
			<div class="text-center mb-8">
				<h2 class="text-2xl font-bold text-gray-900 mb-2">
					{formState.isSignUp ? 'Create Account' : 'Sign In'}
				</h2>
				<p class="text-gray-600">
					{formState.isSignUp ? 'Join the Bayanihan community today' : 'Welcome back to Bayanihan Exchange'}
				</p>
			</div>

			<div class="bg-white py-8 px-6 rounded-2xl shadow-lg border border-gray-100">
				<!-- Error Message -->
				{#if formState.errors.general}
					<div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
						{formState.errors.general}
					</div>
				{/if}

				<form class="space-y-6" onsubmit={handleSubmit}>
					{#if formState.isSignUp}
						<div>
							<label for="name" class="block text-sm font-medium text-gray-700 mb-2">
								Full Name
							</label>
							<input
								id="name"
								name="name"
								type="text"
								bind:value={formData.name}
								class="w-full px-4 py-3 border {formState.errors.name ? 'border-red-500' : 'border-gray-300'} rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors"
								placeholder="Enter your full name"
							/>
							{#if formState.errors.name}
								<p class="mt-1 text-sm text-red-600">{formState.errors.name}</p>
							{/if}
						</div>
					{/if}

					<div>
						<label for="email" class="block text-sm font-medium text-gray-700 mb-2">
							Email Address
						</label>
						<input
							id="email"
							name="email"
							type="email"
							autocomplete="email"
							bind:value={formData.email}
							class="w-full px-4 py-3 border {formState.errors.email ? 'border-red-500' : 'border-gray-300'} rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors"
							placeholder="Enter your email address"
						/>
						{#if formState.errors.email}
							<p class="mt-1 text-sm text-red-600">{formState.errors.email}</p>
						{/if}
					</div>

					<div>
						<label for="password" class="block text-sm font-medium text-gray-700 mb-2">
							Password
						</label>
						<div class="relative">
							<input
								id="password"
								name="password"
								type={showPassword ? 'text' : 'password'}
								autocomplete={formState.isSignUp ? "new-password" : "current-password"}
								bind:value={formData.password}
								class="w-full pr-12 px-4 py-3 border {formState.errors.password ? 'border-red-500' : 'border-gray-300'} rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors"
								placeholder="Password"
							/>
							<button type="button" class="absolute inset-y-0 right-3 my-auto text-gray-500 hover:text-gray-700" onclick={() => showPassword = !showPassword} aria-label={showPassword ? 'Hide password' : 'Show password'}>
								{#if showPassword}
									<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-5 0-9-4-9-7 0-1.07.41-2.205 1.125-3.3M6.2 6.2A9.967 9.967 0 0112 5c5 0 9 4 9 7 0 1.07-.41 2.205-1.125 3.3M3 3l18 18M9.88 9.88A3 3 0 0012 15a3 3 0 002.12-5.12"/></svg>
								{:else}
									<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
								{/if}
							</button>
						</div>
						{#if formState.errors.password}
							<p class="mt-1 text-sm text-red-600">{formState.errors.password}</p>
						{/if}
					</div>

					{#if formState.isSignUp}
						<div>
							<label for="confirm-password" class="block text-sm font-medium text-gray-700 mb-2">
								Confirm Password
							</label>
							<div class="relative">
								<input
									id="confirm-password"
									name="confirm-password"
									type={showConfirmPassword ? 'text' : 'password'}
									autocomplete="new-password"
									bind:value={formData.confirmPassword}
									class="w-full pr-12 px-4 py-3 border {formState.errors.confirmPassword ? 'border-red-500' : 'border-gray-300'} rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors"
									placeholder="Confirm your password"
								/>
								<button type="button" class="absolute inset-y-0 right-3 my-auto text-gray-500 hover:text-gray-700" onclick={() => showConfirmPassword = !showConfirmPassword} aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}>
									{#if showConfirmPassword}
										<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-5 0-9-4-9-7 0-1.07.41-2.205 1.125-3.3M6.2 6.2A9.967 9.967 0 0112 5c5 0 9 4 9 7 0 1.07-.41 2.205-1.125 3.3M3 3l18 18M9.88 9.88A3 3 0 0012 15a3 3 0 002.12-5.12"/></svg>
									{:else}
										<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
									{/if}
								</button>
							</div>
							{#if formState.errors.confirmPassword}
								<p class="mt-1 text-sm text-red-600">{formState.errors.confirmPassword}</p>
							{/if}
						</div>
					{/if}

					{#if !formState.isSignUp}
						<div class="flex items-center justify-between">
							<div class="flex items-center">
								<input
									id="remember-me"
									name="remember-me"
									type="checkbox"
									bind:checked={formData.rememberMe}
									class="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
								/>
								<label for="remember-me" class="ml-2 block text-sm text-gray-900">
									Remember me
								</label>
							</div>

							<div class="text-sm">
								<button type="button" class="font-medium text-red-600 hover:text-red-500 transition-colors">
									Forgot Password?
								</button>
							</div>
						</div>
					{/if}

					<div>
						<button
							type="submit"
							disabled={formState.isLoading}
							class="w-full bg-red-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
						>
							{#if formState.isLoading}
								<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
							{/if}
							{formState.isLoading ? 'Processing...' : (formState.isSignUp ? 'SIGN UP' : 'SIGN IN')}
						</button>
						<p class="mt-3 text-center text-sm text-gray-600">
							{formState.isSignUp ? 'Already have an account?' : "Don't have an account?"}
							<button type="button" class="ml-1 text-red-600 hover:text-red-700 font-medium" onclick={toggleMode}>
								{formState.isSignUp ? 'Sign in' : 'Sign up'}
							</button>
						</p>
					</div>
				</form>

				<div class="mt-6">
					<div class="relative">
						<div class="absolute inset-0 flex items-center">
							<div class="w-full border-t border-gray-300"></div>
						</div>
						<div class="relative flex justify-center text-sm">
							<span class="px-2 bg-white text-gray-500">Or connect with</span>
						</div>
					</div>

					<div class="mt-6 grid grid-cols-3 gap-3">
						<button
							type="button"
							onclick={() => handleSocialLogin('google')}
							disabled={formState.isLoading}
							class="w-full inline-flex justify-center py-3 px-4 border border-gray-300 rounded-lg shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
							aria-label="Sign in with Google"
						>
							<svg class="h-5 w-5" viewBox="0 0 24 24">
								<path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
								<path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
								<path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
								<path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
							</svg>
						</button>

						<button
							type="button"
							onclick={() => handleSocialLogin('apple')}
							disabled={formState.isLoading}
							class="w-full inline-flex justify-center py-3 px-4 border border-gray-300 rounded-lg shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
							aria-label="Sign in with Apple"
						>
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
								<path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
							</svg>
						</button>

						<button
							type="button"
							onclick={() => handleSocialLogin('facebook')}
							disabled={formState.isLoading}
							class="w-full inline-flex justify-center py-3 px-4 border border-gray-300 rounded-lg shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
							aria-label="Sign in with Facebook"
						>
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
								<path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
							</svg>
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>