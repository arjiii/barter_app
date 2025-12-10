<script lang="ts">
	let {
		size = 'medium',
		message = '',
		color = 'red'
	} = $props<{
		size?: 'small' | 'medium' | 'large';
		message?: string;
		color?: 'red' | 'white' | 'gray';
	}>();

	const sizeClasses: Record<'small' | 'medium' | 'large', string> = {
		small: 'w-4 h-4',
		medium: 'w-8 h-8',
		large: 'w-12 h-12'
	};

	const colorClasses: Record<'red' | 'white' | 'gray', string> = {
		red: 'border-gray-200 border-t-red-600',
		white: 'border-white/20 border-t-white',
		gray: 'border-gray-200 border-t-gray-600'
	};
</script>

<div class="flex flex-col items-center justify-center {message ? 'p-8' : ''}">
	<div
		class="animate-spin rounded-full border-2 {colorClasses[
			color as 'red' | 'white' | 'gray'
		]} {sizeClasses[size as 'small' | 'medium' | 'large']}"
	></div>
	{#if message}
		<p class="mt-4 text-sm text-gray-600">{message}</p>
	{/if}
</div>
