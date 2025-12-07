<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { authStore } from '$lib/stores/authStore';
	import { itemService } from '$lib/services/itemService';
	import type { CreateItemData, Category } from '$lib/types/items';
	import { notificationStore } from '$lib/stores/notificationStore';

	const dispatch = createEventDispatcher();

	let { isOpen = $bindable(false), editItem = null } = $props<{
		isOpen?: boolean;
		editItem?: any | null;
	}>();
	let isLoading = $state(false);
	let error: string | null = $state(null);
	let success: string | null = $state(null);

	// Form data
	let formData: CreateItemData = $state({
		title: '',
		description: '',
		category: '',
		condition: '',
		images: [],
		location: ''
	});

	let categories: Category[] = $state([]);
	let selectedImages: File[] = $state([]);
	let imagePreviewUrls: string[] = $state([]);
	let otherCategory = $state('');

	const conditions = [
		{ value: 'excellent', label: 'Excellent' },
		{ value: 'good', label: 'Good' },
		{ value: 'fair', label: 'Fair' },
		{ value: 'poor', label: 'Poor' }
	];

	// Load categories when component mounts
	async function loadCategories() {
		try {
			categories = await itemService.getCategories();
		} catch (err) {
			console.error('Failed to load categories:', err);
		}
	}

	// Watch for editItem prop changes to populate form
	$effect(() => {
		if (isOpen && editItem) {
			// Populate form with item data for editing
			formData = {
				title: editItem.title || '',
				description: editItem.description || '',
				category: editItem.category || '',
				condition: editItem.condition || '',
				images: editItem.images || [],
				location: editItem.location || ''
			};
			// Set image previews from existing images
			imagePreviewUrls = editItem.images || [];
			selectedImages = [];
		} else if (isOpen && !editItem) {
			// Reset form for new item
			formData = {
				title: '',
				description: '',
				category: '',
				condition: '',
				images: [],
				location: ''
			};
			selectedImages = [];
			imagePreviewUrls = [];
		}
	});

	// Handle image selection
	function handleImageSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		const files = Array.from(target.files || []);

		if (files.length > 0) {
			selectedImages = [...selectedImages, ...files].slice(0, 5); // Max 5 images
			updateImagePreviews();
		}
	}

	function updateImagePreviews() {
		// Clean up old blob URLs to prevent memory leaks
		imagePreviewUrls.forEach((url) => {
			if (url.startsWith('blob:')) {
				URL.revokeObjectURL(url);
			}
		});
		imagePreviewUrls = selectedImages.map((file) => URL.createObjectURL(file));
	}

	function removeImage(index: number) {
		selectedImages = selectedImages.filter((_, i) => i !== index);
		updateImagePreviews();
	}

	// Handle form submission
	async function handleSubmit() {
		if (!formData.title || !formData.description || !formData.category || !formData.condition) {
			error = 'Please fill in all required fields';
			return;
		}

		isLoading = true;
		error = null;
		success = null;

		try {
			console.log('Starting item creation process...');

			// Get current user ID from auth store
			const authState = authStore.get();
			console.log('Auth state:', authState);

			if (!authState.user) {
				throw new Error('User not authenticated - please sign in again');
			}

			if (!authState.isAuthenticated) {
				throw new Error('Authentication state is false - please sign in again');
			}

			console.log('User authenticated:', authState.user.id);
			console.log('User name:', authState.user.name);
			console.log('User email:', authState.user.email);

			// Check if token exists in localStorage
			const token = localStorage.getItem('bayanihan_token');
			console.log('Token exists:', !!token);
			console.log('Token length:', token ? token.length : 0);

			// Convert images to base64 for now (in production, upload to cloud storage)
			const imageUrls = await Promise.all(
				selectedImages.map(async (file) => {
					return new Promise<string>((resolve) => {
						const reader = new FileReader();
						reader.onload = () => {
							resolve(reader.result as string);
						};
						reader.readAsDataURL(file);
					});
				})
			);

			const itemData = {
				...formData,
				category: formData.category === 'others' ? otherCategory || 'Others' : formData.category,
				images: imageUrls
			};

			console.log('Item data to send:', itemData);

			let result;
			if (editItem) {
				// Update existing item
				result = await itemService.updateItem(editItem.id, itemData);
				if (!result) {
					throw new Error('Item update failed - check backend logs');
				}
				success = 'Item updated successfully!';
				notificationStore.push('Your item has been updated');
				dispatch('itemUpdated', result);
			} else {
				// Create new item
				result = await itemService.createItem(itemData);
				console.log('Item created:', result);

				if (!result) {
					throw new Error('Item creation returned null - check backend logs');
				}

				success = 'Item posted successfully!';
				notificationStore.push('Your item has been posted');

				// Dispatch event immediately
				dispatch('itemPosted');
			}

			// Reset form
			formData = {
				title: '',
				description: '',
				category: '',
				condition: '',
				images: [],
				location: ''
			};
			selectedImages = [];
			imagePreviewUrls = [];

			// Close modal after a short delay
			setTimeout(() => {
				isOpen = false;
			}, 1500);
		} catch (err) {
			error = `Failed to post item: ${err.message}`;
			console.error('Error posting item:', err);
		} finally {
			isLoading = false;
		}
	}

	function closeModal() {
		isOpen = false;
		error = null;
		success = null;

		// Clean up blob URLs
		imagePreviewUrls.forEach((url) => {
			if (url.startsWith('blob:')) {
				URL.revokeObjectURL(url);
			}
		});

		// Reset form
		formData = {
			title: '',
			description: '',
			category: '',
			condition: '',
			images: [],
			location: ''
		};
		otherCategory = '';
		selectedImages = [];
		imagePreviewUrls = [];
	}

	// Load categories when component mounts
	loadCategories();
</script>

<!-- Modal Overlay -->
{#if isOpen}
	<div class="fixed inset-0 z-50 overflow-y-auto" on:click={closeModal}>
		<div class="flex min-h-screen items-center justify-center p-4">
			<!-- Modal Content -->
			<div
				class="relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white shadow-xl"
				on:click|stopPropagation
			>
				<!-- Header -->
				<div class="flex items-center justify-between border-b border-gray-200 p-6">
					<h2 class="text-2xl font-bold text-gray-900">
						{editItem ? 'Edit Item' : 'Post New Item'}
					</h2>
					<button on:click={closeModal} class="text-gray-400 transition-colors hover:text-gray-600">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							></path>
						</svg>
					</button>
				</div>

				<!-- Form -->
				<form on:submit|preventDefault={handleSubmit} class="space-y-6 p-6">
					<!-- Title -->
					<div>
						<label for="title" class="mb-2 block text-sm font-medium text-gray-700">
							Item Title *
						</label>
						<input
							id="title"
							type="text"
							bind:value={formData.title}
							placeholder="Enter item title..."
							class="w-full rounded-xl border border-gray-300 px-4 py-3 transition-colors focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500"
							required
						/>
					</div>

					<!-- Description -->
					<div>
						<label for="description" class="mb-2 block text-sm font-medium text-gray-700">
							Description *
						</label>
						<textarea
							id="description"
							bind:value={formData.description}
							placeholder="Describe your item..."
							rows="4"
							class="w-full resize-none rounded-xl border border-gray-300 px-4 py-3 transition-colors focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500"
							required
						></textarea>
					</div>

					<!-- Category and Condition -->
					<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
						<div>
							<label for="category" class="mb-2 block text-sm font-medium text-gray-700">
								Category *
							</label>
							<select
								id="category"
								bind:value={formData.category}
								class="w-full rounded-xl border border-gray-300 px-4 py-3 transition-colors focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500"
								required
							>
								<option value="">Select category...</option>
								{#each categories as category}
									<option value={category.id}>{category.name}</option>
								{/each}
								<option value="others">Others (please specify)</option>
							</select>
							{#if formData.category === 'others'}
								<input
									class="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3"
									placeholder="Type category"
									bind:value={otherCategory}
								/>
							{/if}
						</div>

						<div>
							<label for="condition" class="mb-2 block text-sm font-medium text-gray-700">
								Condition *
							</label>
							<select
								id="condition"
								bind:value={formData.condition}
								class="w-full rounded-xl border border-gray-300 px-4 py-3 transition-colors focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500"
								required
							>
								<option value="">Select condition...</option>
								{#each conditions as condition}
									<option value={condition.value}>{condition.label}</option>
								{/each}
							</select>
						</div>
					</div>

					<!-- Location -->
					<div>
						<label for="location" class="mb-2 block text-sm font-medium text-gray-700">
							Location (City/Province)
						</label>
						<input
							id="location"
							type="text"
							bind:value={formData.location}
							placeholder="e.g., Manila, Metro Manila or Quezon City"
							class="w-full rounded-xl border border-gray-300 px-4 py-3 transition-colors focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500"
						/>
					</div>

					<!-- Images -->
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700"> Photos (up to 5) </label>

						<!-- Image Upload Area -->
						<div
							class="rounded-xl border-2 border-dashed border-gray-300 p-6 text-center transition-colors hover:border-gray-400"
						>
							<input
								type="file"
								accept="image/*"
								multiple
								on:change={handleImageSelect}
								class="hidden"
								id="image-upload"
							/>
							<label for="image-upload" class="cursor-pointer">
								<svg
									class="mx-auto mb-4 h-12 w-12 text-gray-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
									></path>
								</svg>
								<p class="mb-2 text-gray-600">Click to upload photos</p>
								<p class="text-sm text-gray-500">PNG, JPG up to 10MB each</p>
							</label>
						</div>

						<!-- Image Previews -->
						{#if imagePreviewUrls.length > 0}
							<div class="mt-4 grid grid-cols-2 gap-4 md:grid-cols-3">
								{#each imagePreviewUrls as url, index}
									<div class="relative">
										<img
											src={url}
											alt="Preview {index + 1}"
											class="h-32 w-full rounded-lg object-cover"
										/>
										<button
											type="button"
											on:click={() => removeImage(index)}
											class="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-sm text-white transition-colors hover:bg-red-600"
										>
											×
										</button>
									</div>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Error/Success Messages -->
					{#if error}
						<div class="rounded-xl border border-red-200 bg-red-50 p-4">
							<div class="flex">
								<svg
									class="mr-2 h-5 w-5 text-red-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
									></path>
								</svg>
								<p class="text-sm text-red-800">{error}</p>
							</div>
						</div>
					{/if}

					{#if success}
						<div class="rounded-xl border border-green-200 bg-green-50 p-4">
							<div class="flex">
								<svg
									class="mr-2 h-5 w-5 text-green-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
									></path>
								</svg>
								<p class="text-sm text-green-800">{success}</p>
							</div>
						</div>
					{/if}

					<!-- Actions -->
					<div class="flex justify-end space-x-4 border-t border-gray-200 pt-4">
						<button
							type="button"
							on:click={closeModal}
							class="rounded-xl bg-gray-100 px-6 py-3 font-medium text-gray-700 transition-colors hover:bg-gray-200"
						>
							Cancel
						</button>
						<button
							type="submit"
							disabled={isLoading}
							class="flex items-center rounded-xl bg-red-600 px-6 py-3 font-medium text-white transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
						>
							{#if isLoading}
								<svg
									class="-ml-1 mr-2 h-4 w-4 animate-spin text-white"
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
							{isLoading ? 'Posting...' : 'Post Item'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}
