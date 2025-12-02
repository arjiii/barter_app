<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
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
<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
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
	
	// Forgot password state
	let showForgotPassword = $state(false);
	let forgotPasswordEmail = $state('');
	let forgotPasswordSent = $state(false);

	// Verification state
	let verificationStep = $state(false);
	let otpCode = $state('');
	let verificationEmail = $state('');

	// Form data - use any type to handle both login and signup
	let formData = $state<any>({
		email: '',
		password: '',
		rememberMe: false
	});

	// Respect mode query param (?mode=signup) when users come from landing
	$effect(() => {
		const mode = $page.url.searchParams.get('mode');
		if (mode === 'signup') {
			formState.isSignUp = true;
		} else if (mode === 'signin') {
			formState.isSignUp = false;
		}
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
		verificationStep = false; // Reset verification step if mode changes
	}

	/**
	 * Handle form submission (Sign In/Sign Up)
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
				formState.isLoading = false;
				return;
			}

			// Call authentication service
			const response = formState.isSignUp 
				? await authService.signUp(formData as SignUpCredentials)
				: await authService.signIn(formData as LoginCredentials);

			if (response.success && response.user) {
				// Update auth store
				authStore.setUser(response.user);
				
				// If signup, go to verification step
				if (formState.isSignUp) {
					verificationStep = true;
					verificationEmail = formData.email;
					formState.isLoading = false; // Stop loading state for the form, as we're transitioning to a new step
					return; // Prevent further execution and redirection
				}
				
				// Redirect to dashboard for sign-in or verified sign-up
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
	 * Handle email verification
	 */
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

			if (response.success && response.user) {
				authStore.setUser(response.user);
				await goto('/discovery'); // Redirect after successful verification
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

	/**
	 * Handle forgot password
	 */
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

	onMount(() => {
		// Initialize auth state
		authStore.initializeAuth();
	});
</script>

<div class="min-h-screen bg-[#f7f5f3] flex font-['Inter',sans-serif] text-[#1c1816]">
	<!-- Left Side - Welcome Section -->
	<div class="hidden lg:flex lg:w-5/12 bg-gradient-to-br from-[#fbe4d5] via-[#f7d2c3] to-[#f7c9b6] flex-col justify-center px-12 py-16 text-[#43291b] border-r border-[#f1d5c6]">
		<!-- Logo -->
		<div class="mb-8">
			<div class="w-11 h-11 bg-white/90 rounded-full flex items-center justify-center mb-4 shadow-sm">
				<svg class="h-6 w-6 text-[#ff6d3f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
				</svg>
			</div>
			<h1 class="text-2xl font-semibold tracking-tight">Bayanihan Exchange</h1>
			<p class="text-[#674c3b] text-sm">Blockchain-Powered Community Barter</p>
		</div>

		<!-- Welcome Content -->
		<div class="max-w-md space-y-6">
			<h2 class="text-3xl font-semibold leading-tight">
				{formState.isSignUp ? 'Join our Bayanihan Community' : 'Welcome back, Kabayan!'}
			</h2>
			<p class="text-base text-[#6c4d3a]">
				{formState.isSignUp ? 'Start your journey with us and join our community of neighbors helping neighbors through blockchain-powered bartering.' : 'Continue your journey in our community where neighbors help neighbors through secure blockchain trading.'}
			</p>
			
			<button 
				type="button" 
				onclick={toggleMode}
				class="inline-flex items-center gap-2 bg-white/90 text-[#ff6d3f] px-5 py-2.5 rounded-full font-semibold shadow-sm hover:bg-white transition-colors duration-200"
			>
				<span>{formState.isSignUp ? 'Already have an account? Sign in' : 'New to Bayanihan? Sign up'}</span>
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5-5 5M6 12h12"/></svg>
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
	<div class="w-full lg:w-7/12 bg-[#fffdfb] flex flex-col justify-center px-6 sm:px-10 py-10">
		<!-- Mobile Logo -->
		<div class="lg:hidden mb-8 text-center">
			<div class="w-11 h-11 bg-[#ff6d3f] rounded-full flex items-center justify-center mx-auto mb-3 shadow-sm">
				<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
				</svg>
			</div>
			<h1 class="text-xl font-semibold text-[#201915] tracking-tight">Bayanihan Exchange</h1>
			<p class="text-xs text-[#6f5d53] uppercase tracking-[0.2em]">Community barter</p>
		</div>

		<div class="max-w-md mx-auto w-full">
			<div class="text-center mb-6">
				<h2 class="text-[1.65rem] font-semibold text-[#1f1b17] mb-2 tracking-tight">
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
						{formState.isSignUp ? 'Join the Bayanihan community today' : 'Welcome back to Bayanihan Exchange'}
					{/if}
				</p>
						</div>
						<div class="relative flex justify-center text-sm">
							<span class="px-2 bg-white text-[#8a7c72] text-xs uppercase tracking-[0.3em]">Or connect</span>
						</div>
					</div>

					<div class="mt-5 grid grid-cols-3 gap-3">
						<button
							type="button"
							onclick={() => handleSocialLogin('google')}
							disabled={formState.isLoading}
							class="w-full inline-flex justify-center py-3 px-4 border border-[#dfd4cb] rounded-xl bg-white/90 text-sm font-medium text-[#4b433d] hover:bg-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
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
							class="w-full inline-flex justify-center py-3 px-4 border border-[#dfd4cb] rounded-xl bg-white/90 text-sm font-medium text-[#4b433d] hover:bg-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
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
							class="w-full inline-flex justify-center py-3 px-4 border border-[#dfd4cb] rounded-xl bg-white/90 text-sm font-medium text-[#4b433d] hover:bg-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
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

	<!-- Forgot Password Modal -->
	{#if showForgotPassword}
		<div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onclick={() => { if (!forgotPasswordSent) showForgotPassword = false; }}>
			<div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6" onclick={(e) => e.stopPropagation()}>
				{#if !forgotPasswordSent}
					<h2 class="text-2xl font-semibold text-[#1f1b17] mb-4">Forgot Password?</h2>
					<p class="text-sm text-[#6c6b69] mb-6">
						Enter your email address and we'll send you a link to reset your password.
					</p>
					<form onsubmit={handleForgotPassword} class="space-y-4">
						<div>
							<label for="forgot-email" class="block text-xs uppercase tracking-[0.2em] text-[#8b6b55] mb-2">
								Email Address
							</label>
							<input
								id="forgot-email"
								type="email"
								bind:value={forgotPasswordEmail}
								required
								class="w-full px-4 py-3 border border-[#e3d8cf] rounded-xl bg-[#fdf9f6] focus:outline-none focus:ring-2 focus:ring-[#ffb797] focus:border-[#ff855a] transition-colors text-[#2d261f]"
								placeholder="Enter your email"
							/>
						</div>
						{#if formState.errors.general}
							<div class="p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm">
								{formState.errors.general}
							</div>
						{/if}
						<div class="flex gap-3">
							<button
								type="button"
								onclick={() => { showForgotPassword = false; forgotPasswordEmail = ''; formState.errors = {}; }}
								class="flex-1 px-4 py-3 border border-[#e3d8cf] rounded-xl text-[#4d4138] hover:bg-[#fdf9f6] transition-colors"
							>
								Cancel
							</button>
							<button
								type="submit"
								disabled={formState.isLoading}
								class="flex-1 px-4 py-3 bg-[#1f1b17] text-white rounded-xl font-semibold hover:bg-black disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
							>
								{formState.isLoading ? 'Sending...' : 'Send Reset Link'}
							</button>
						</div>
					</form>
				{:else}
					<div class="text-center">
						<div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
							<svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
							</svg>
						</div>
						<h2 class="text-2xl font-semibold text-[#1f1b17] mb-2">Check Your Email</h2>
						<p class="text-sm text-[#6c6b69] mb-6">
							We've sent a password reset link to <strong>{forgotPasswordEmail}</strong>
						</p>
						<button
							onclick={() => { showForgotPassword = false; forgotPasswordEmail = ''; forgotPasswordSent = false; formState.errors = {}; }}
							class="w-full px-4 py-3 bg-[#1f1b17] text-white rounded-xl font-semibold hover:bg-black transition-colors"
						>
							Close
						</button>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>