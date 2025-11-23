<script lang="ts">
	let { size = 'medium', message = 'Loading...' } = $props<{
		size?: 'small' | 'medium' | 'large';
		message?: string;
	}>();

	const sizeClasses: Record<'small' | 'medium' | 'large', string> = {
		small: 'w-4 h-4',
		medium: 'w-8 h-8',
		large: 'w-12 h-12'
	};
</script>

<div class="flex flex-col items-center justify-center p-8">
	<div class="animate-spin rounded-full border-4 border-gray-200 border-t-red-600 {sizeClasses[size]}"></div>
	{#if message}
		<p class="mt-4 text-gray-600 text-sm">{message}</p>
	{/if}
</div>
