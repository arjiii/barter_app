<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/authStore';
	import { itemService } from '$lib/services/itemService';
	import type { CreateItemData, Category } from '$lib/types/items';

	let currentStep = $state(0);
	const steps = ['Basic Info', 'Details', 'Location & Media', 'Review'];

	let isLoading = $state(false);
	let error: string | null = $state(null);
	let categories: Category[] = $state([]);

	let formData = $state({
		title: '',
		description: '',
		category: '',
		condition: '',
		images: [] as string[],
		location: '',
		latitude: null as number | null,
		longitude: null as number | null
	});

	let otherCategory = $state('');
	let selectedImages: File[] = $state([]);
	let imagePreviewUrls: string[] = $state([]);

	const conditions = [
		{ value: 'excellent', label: 'Excellent' },
		{ value: 'good', label: 'Good' },
		{ value: 'fair', label: 'Fair' },
		{ value: 'poor', label: 'Poor' }
	];

	onMount(async () => {
		authStore.initializeAuth();
		if (!authStore.isAuthenticated()) {
			goto('/sign-in-up');
			return;
		}
		try {
			categories = await itemService.getCategories();
		} catch (err) {
			console.error('Failed to load categories:', err);
		}
	});

	function handleImageSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		const files = Array.from(target.files || []);
		if (files.length > 0) {
			selectedImages = [...selectedImages, ...files].slice(0, 5);
			updateImagePreviews();
		}
	}

	function updateImagePreviews() {
		imagePreviewUrls.forEach((url) => URL.revokeObjectURL(url));
		imagePreviewUrls = selectedImages.map((file) => URL.createObjectURL(file));
	}

	function removeImage(index: number) {
		selectedImages = selectedImages.filter((_, i) => i !== index);
		updateImagePreviews();
	}

	function detectLocation() {
		if ('geolocation' in navigator) {
			navigator.geolocation.getCurrentPosition(
				(position) => {
					formData.latitude = position.coords.latitude;
					formData.longitude = position.coords.longitude;
					formData.location = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
				},
				(err) => {
					console.error('Geolocation error:', err);
					alert('Could not detect location. Please enter manually.');
				}
			);
		} else {
			alert('Geolocation is not supported by your browser.');
		}
	}

	function nextStep() {
		if (currentStep === 0) {
			if (!formData.title || !formData.category) {
				alert('Please fill in all required fields');
				return;
			}
		} else if (currentStep === 1) {
			if (!formData.description || !formData.condition) {
				alert('Please fill in all required fields');
				return;
			}
		}
		currentStep++;
	}

	function prevStep() {
		currentStep--;
	}

	async function handleSubmit() {
		isLoading = true;
		try {
			const user = authStore.get().user;
			if (!user) throw new Error('User not authenticated');

			const imageUrls = await Promise.all(
				selectedImages.map(async (file) => {
					return new Promise<string>((resolve) => {
						const reader = new FileReader();
						reader.onload = () => resolve(reader.result as string);
						reader.readAsDataURL(file);
					});
				})
			);

			const itemData = {
				...formData,
				category: formData.category === 'others' ? otherCategory || 'Others' : formData.category,
				images: imageUrls
			};

			await itemService.createItem(user.id, itemData);
			goto('/my-items');
		} catch (err: any) {
			error = err.message || 'Failed to create item';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="min-h-screen bg-[#f7f5f3] px-4 py-12 font-['Inter',sans-serif] sm:px-6 lg:px-8">
	<div class="mx-auto max-w-3xl">
		<!-- Stepper Header -->
		<div class="mb-8">
			<div class="relative flex items-center justify-between">
				<div
					class="absolute left-0 top-1/2 -z-10 h-1 w-full -translate-y-1/2 transform bg-gray-200"
				></div>
				{#each steps as step, i}
					<div class="flex flex-col items-center bg-[#f7f5f3] px-2">
						<div
							class={`mb-2 flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${i <= currentStep ? 'bg-[#ff6d3f] text-white' : 'bg-gray-200 text-gray-500'}`}
						>
							{i + 1}
						</div>
						<span
							class={`text-xs font-medium ${i <= currentStep ? 'text-[#ff6d3f]' : 'text-gray-500'}`}
							>{step}</span
						>
					</div>
				{/each}
			</div>
		</div>

		<div class="rounded-2xl bg-white p-8 shadow-xl">
			<h2 class="mb-6 text-2xl font-bold text-[#1f1b17]">{steps[currentStep]}</h2>

			{#if currentStep === 0}
				<div class="space-y-6">
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Item Title *</label>
						<input
							type="text"
							bind:value={formData.title}
							class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
							placeholder="What are you trading?"
						/>
					</div>
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Category *</label>
						<select
							bind:value={formData.category}
							class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
						>
							<option value="">Select category...</option>
							{#each categories as category}
								<option value={category.id}>{category.name}</option>
							{/each}
							<option value="others">Others</option>
						</select>
						{#if formData.category === 'others'}
							<input
								type="text"
								bind:value={otherCategory}
								class="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3"
								placeholder="Specify category"
							/>
						{/if}
					</div>
				</div>
			{:else if currentStep === 1}
				<div class="space-y-6">
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Condition *</label>
						<select
							bind:value={formData.condition}
							class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
						>
							<option value="">Select condition...</option>
							{#each conditions as c}
								<option value={c.value}>{c.label}</option>
							{/each}
						</select>
					</div>
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Description *</label>
						<textarea
							bind:value={formData.description}
							rows="6"
							class="w-full rounded-xl border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
							placeholder="Describe your item in detail..."
						></textarea>
					</div>
				</div>
			{:else if currentStep === 2}
				<div class="space-y-6">
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Location</label>
						<div class="flex gap-2">
							<input
								type="text"
								bind:value={formData.location}
								class="flex-1 rounded-xl border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-[#ff6d3f]"
								placeholder="City, Province"
							/>
							<button
								type="button"
								onclick={detectLocation}
								class="rounded-xl bg-gray-100 px-4 py-3 text-gray-700 hover:bg-gray-200"
							>
								📍 Detect
							</button>
						</div>
						{#if formData.latitude}
							<p class="mt-1 text-xs text-green-600">
								✓ Coordinates captured: {formData.latitude.toFixed(4)}, {formData.longitude.toFixed(
									4
								)}
							</p>
						{/if}
					</div>
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700">Photos (Max 5)</label>
						<div
							class="relative cursor-pointer rounded-xl border-2 border-dashed border-gray-300 p-8 text-center transition-colors hover:border-[#ff6d3f]"
						>
							<input
								type="file"
								accept="image/*"
								multiple
								onchange={handleImageSelect}
								class="absolute inset-0 h-full w-full cursor-pointer opacity-0"
							/>
							<div class="text-gray-500">
								<span class="font-medium text-[#ff6d3f]">Upload files</span> or drag and drop
							</div>
						</div>
						{#if imagePreviewUrls.length > 0}
							<div class="mt-4 grid grid-cols-3 gap-4">
								{#each imagePreviewUrls as url, i}
									<div class="group relative">
										<img src={url} alt="Preview" class="h-24 w-full rounded-lg object-cover" />
										<button
											onclick={() => removeImage(i)}
											class="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-white opacity-0 transition-opacity group-hover:opacity-100"
											>×</button
										>
									</div>
								{/each}
							</div>
						{/if}
					</div>
				</div>
			{:else if currentStep === 3}
				<div class="space-y-4">
					<div class="rounded-xl bg-gray-50 p-4">
						<h3 class="text-lg font-semibold">{formData.title}</h3>
						<p class="text-sm text-gray-600">{formData.category} • {formData.condition}</p>
						<p class="mt-2 text-gray-700">{formData.description}</p>
						<p class="mt-2 text-sm text-gray-500">
							📍 {formData.location || 'No location specified'}
						</p>
					</div>
					<div class="grid grid-cols-3 gap-2">
						{#each imagePreviewUrls as url}
							<img src={url} alt="Preview" class="h-20 w-full rounded-lg object-cover" />
						{/each}
					</div>
				</div>
			{/if}

			{#if error}
				<div class="mt-4 rounded-lg bg-red-100 p-3 text-red-700">{error}</div>
			{/if}

			<div class="mt-8 flex justify-between">
				<button
					type="button"
					onclick={prevStep}
					disabled={currentStep === 0}
					class="rounded-xl border border-gray-300 px-6 py-3 font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
				>
					Back
				</button>

				{#if currentStep < steps.length - 1}
					<button
						type="button"
						onclick={nextStep}
						class="rounded-xl bg-[#1f1b17] px-6 py-3 font-medium text-white hover:bg-black"
					>
						Next
					</button>
				{:else}
					<button
						type="button"
						onclick={handleSubmit}
						disabled={isLoading}
						class="rounded-xl bg-[#ff6d3f] px-6 py-3 font-medium text-white hover:bg-[#e65a2f] disabled:opacity-50"
					>
						{isLoading ? 'Posting...' : 'Post Item'}
					</button>
				{/if}
			</div>
		</div>
	</div>
</div>
