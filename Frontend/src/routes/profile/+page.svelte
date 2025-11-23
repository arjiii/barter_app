<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/authStore';
  import { authService } from '$lib/services/authService';
  import { tradeService } from '$lib/services/tradeService';
  import { userService } from '$lib/services/userService';
  import type { User } from '$lib/types/auth';

  let user: User | null = $state(null);
  let isAuthenticated = $state(false);
  let isLoading = $state(true);
  let nameInput = $state('');
  let profileMsg: string | null = $state(null);
  let pwdMsg: string | null = $state(null);
  let oldPassword = $state('');
  let newPassword = $state('');
  let confirmPassword = $state('');
  let ratings = $state<any[]>([]);
  let isLoadingRatings = $state(true);

  async function loadRatings() {
    if (!user) return;
    try {
      isLoadingRatings = true;
      const userRatings = await tradeService.getUserRatings(user.id);
      
      // Enhance ratings with rater user info
      const enhancedRatings = await Promise.all(
        userRatings.map(async (rating) => {
          try {
            const rater = await userService.getUserById(rating.rater_user_id);
            return {
              ...rating,
              raterName: rater?.name || 'User',
              raterId: rater?.id || rating.rater_user_id
            };
          } catch (err) {
            console.error('Error loading rater info:', err);
            return {
              ...rating,
              raterName: 'User',
              raterId: rating.rater_user_id
            };
          }
        })
      );
      
      ratings = enhancedRatings;
    } catch (error) {
      console.error('Error loading ratings:', error);
      ratings = [];
    } finally {
      isLoadingRatings = false;
    }
  }

  onMount(() => {
    const unsubscribe = authStore.subscribe(async (authState) => {
      user = authState.user;
      isAuthenticated = authState.isAuthenticated;
      isLoading = authState.isLoading;
      if (authState.user) {
        nameInput = authState.user.name;
        if (authState.isAuthenticated) {
          await loadRatings();
        }
      }
      if (!authState.isLoading && !authState.isAuthenticated) {
        goto('/sign-in-up');
      }
    });
    return unsubscribe;
  });

  async function handleSaveProfile() {
    profileMsg = null;
    if (!nameInput.trim()) { profileMsg = 'Name is required'; return; }
    const updated = await authService.updateProfile(nameInput.trim());
    if (updated) {
      authStore.setUser(updated);
      profileMsg = 'Profile updated successfully';
    } else {
      profileMsg = 'Failed to update profile';
    }
  }

  async function handleChangePassword() {
    pwdMsg = null;
    if (!oldPassword || !newPassword) { pwdMsg = 'Enter old and new password'; return; }
    if (newPassword !== confirmPassword) { pwdMsg = 'Passwords do not match'; return; }
    const ok = await authService.changePassword(oldPassword, newPassword);
    pwdMsg = ok ? 'Password changed successfully' : 'Failed to change password';
    if (ok) { oldPassword = newPassword = confirmPassword = ''; }
  }
</script>

<div class="p-4 lg:p-6">
  {#if isLoading}
    <div class="flex items-center justify-center min-h-[400px]">
      <div class="text-center">
        <svg class="animate-spin h-8 w-8 text-red-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-gray-600">Loading profile...</p>
      </div>
    </div>
  {:else if isAuthenticated && user}
    <!-- Profile Header -->
    <div class="bg-gradient-to-r from-red-600 to-red-700 rounded-2xl shadow-lg mb-6 p-8 text-white">
      <div class="flex items-center space-x-6">
        <div class="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center text-3xl font-bold">
          {user.name?.charAt(0)?.toUpperCase() || 'U'}
        </div>
        <div>
          <h1 class="text-3xl font-bold mb-2">{user.name || 'User'}</h1>
          <p class="text-red-100 flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"></path>
            </svg>
            {user.email}
          </p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Profile Section -->
      <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-shadow">
        <div class="flex items-center mb-6">
          <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center mr-3">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
          </div>
          <h2 class="text-xl font-bold text-gray-900">Profile Information</h2>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
            <div class="px-4 py-3 bg-gray-50 rounded-lg text-gray-700 border border-gray-200">
              {user.email}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Display Name</label>
            <input 
              type="text"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-all" 
              bind:value={nameInput}
              placeholder="Enter your display name"
            />
          </div>
          <button 
            class="w-full bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors shadow-md hover:shadow-lg" 
            on:click={handleSaveProfile}
          >
            Save Changes
          </button>
          {#if profileMsg}
            <div class="p-3 rounded-lg {profileMsg.includes('successfully') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}">
              <p class="text-sm font-medium">{profileMsg}</p>
            </div>
          {/if}
        </div>
      </div>

      <!-- Change Password Section -->
      <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-shadow">
        <div class="flex items-center mb-6">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
            </svg>
          </div>
          <h2 class="text-xl font-bold text-gray-900">Change Password</h2>
        </div>
        <div class="space-y-4">
          <div>
            <input 
              type="password" 
              placeholder="Old password" 
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all" 
              bind:value={oldPassword} 
            />
          </div>
          <div>
            <input 
              type="password" 
              placeholder="New password" 
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all" 
              bind:value={newPassword} 
            />
          </div>
          <div>
            <input 
              type="password" 
              placeholder="Confirm new password" 
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all" 
              bind:value={confirmPassword} 
            />
          </div>
          <button 
            class="w-full bg-gray-800 hover:bg-gray-900 text-white font-semibold px-6 py-3 rounded-lg transition-colors shadow-md hover:shadow-lg" 
            on:click={handleChangePassword}
          >
            Update Password
          </button>
          {#if pwdMsg}
            <div class="p-3 rounded-lg {pwdMsg.includes('successfully') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}">
              <p class="text-sm font-medium">{pwdMsg}</p>
            </div>
          {/if}
        </div>
      </div>
    </div>

    <!-- Ratings Section -->
    <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-shadow">
      <div class="flex items-center mb-6">
        <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center mr-3">
          <svg class="w-6 h-6 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900">My Ratings & Reviews</h2>
      </div>
      {#if isLoadingRatings}
        <p class="text-gray-600">Loading ratings...</p>
      {:else if ratings.length === 0}
        <div class="text-center py-8">
          <svg class="mx-auto h-12 w-12 text-gray-300 mb-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
          </svg>
          <p class="text-gray-500">No ratings yet. Complete some trades to get rated!</p>
        </div>
      {:else}
        <div class="space-y-4">
          {#each ratings as rating}
            <div class="border border-gray-200 rounded-xl p-5 hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm">
              <div class="flex items-start justify-between mb-3">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center shadow-md">
                    <span class="text-white font-bold text-lg">
                      {rating.raterName?.charAt(0)?.toUpperCase() || 'U'}
                    </span>
                  </div>
                  <div>
                    <p class="font-semibold text-gray-900 text-lg">{rating.raterName || 'User'}</p>
                    <p class="text-xs text-gray-500 flex items-center mt-1">
                      <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                      </svg>
                      {new Date(rating.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
                    </p>
                  </div>
                </div>
                <div class="flex items-center space-x-1 bg-yellow-50 px-3 py-2 rounded-lg">
                  {#each [1, 2, 3, 4, 5] as star}
                    <svg class="w-5 h-5 {rating.score >= star ? 'text-yellow-400' : 'text-gray-300'}" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                    </svg>
                  {/each}
                  <span class="ml-2 text-sm font-bold text-gray-800">{rating.score}/5</span>
                </div>
              </div>
              {#if rating.feedback}
                <div class="mt-3 pl-16">
                  <p class="text-gray-700 text-sm leading-relaxed bg-gray-50 p-3 rounded-lg border-l-4 border-red-500">
                    {rating.feedback}
                  </p>
                </div>
              {/if}
            </div>
          {/each}
        </div>
        
        <!-- Average Rating -->
        {#if ratings.length > 0}
          <div class="mt-8 pt-6 border-t-2 border-gray-200">
            <div class="grid grid-cols-2 gap-6">
              <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl p-6 text-center border border-yellow-200">
                <p class="text-sm font-medium text-gray-600 mb-2">Average Rating</p>
                <div class="flex items-center justify-center space-x-2 mb-2">
                  <p class="text-4xl font-bold text-gray-900">
                    {(ratings.reduce((sum, r) => sum + r.score, 0) / ratings.length).toFixed(1)}
                  </p>
                  <svg class="w-8 h-8 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                  </svg>
                </div>
                <p class="text-xs text-gray-500">out of 5.0</p>
              </div>
              <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 text-center border border-blue-200">
                <p class="text-sm font-medium text-gray-600 mb-2">Total Ratings</p>
                <p class="text-4xl font-bold text-gray-900 mb-2">{ratings.length}</p>
                <p class="text-xs text-gray-500">reviews received</p>
              </div>
            </div>
          </div>
        {/if}
      {/if}
    </div>
  {:else}
    <p class="text-gray-600">Please sign in to view your profile.</p>
  {/if}
</div>


