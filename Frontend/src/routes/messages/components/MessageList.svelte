<script lang="ts">
	import { afterUpdate, createEventDispatcher, onMount } from 'svelte';
	import type { Message } from '$lib/types/messages';

	export let messages: Message[] = [];
	export let currentUserId: string | null = null;
	export let typingText = '';
	export let seenTimestamp: Date | null = null;

	const dispatch = createEventDispatcher<{ bottom: boolean }>();

	let listRef: HTMLDivElement | null = null;
	let autoScroll = true;

	function scrollToBottom(behavior: ScrollBehavior = 'smooth') {
		if (!listRef) return;
		listRef.scrollTo({
			top: listRef.scrollHeight,
			behavior
		});
	}

	function handleScroll() {
		if (!listRef) return;
		const threshold = 120;
		const distanceFromBottom = listRef.scrollHeight - listRef.scrollTop - listRef.clientHeight;
		autoScroll = distanceFromBottom < threshold;
		dispatch('bottom', autoScroll);
	}

	onMount(() => {
		scrollToBottom('auto');
	});

	afterUpdate(() => {
		if (autoScroll) {
			scrollToBottom();
		}
	});

	$: lastMessageFromSelf = messages
		.filter((message) => message.senderId === currentUserId)
		.slice(-1)[0];
</script>

<div
	class="flex-1 space-y-4 overflow-y-auto px-6 py-6"
	bind:this={listRef}
	on:scroll={handleScroll}
>
	{#each messages as message (message.id)}
		<div class={'flex ' + (message.senderId === currentUserId ? 'justify-end' : 'justify-start')}>
			<div
				class={`max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-lg ${
					message.senderId === currentUserId
						? 'rounded-tr-sm bg-gradient-to-br from-[#ff6d3f] to-[#ff855a] text-white'
						: 'rounded-tl-sm border border-[#f5e1ce] bg-[#fff6ee] text-[#3a2315] shadow-[0_4px_12px_rgba(0,0,0,0.08)]'
				}`}
			>
				<p class="leading-relaxed">{message.content}</p>
				<p
					class={`mt-1 text-[11px] ${message.senderId === currentUserId ? 'text-white/60' : 'text-[#a37758]'}`}
				>
					{new Date(message.createdAt).toLocaleString()}
				</p>
			</div>
		</div>
	{/each}

	{#if typingText}
		<div class="flex justify-start">
			<div class="rounded-2xl bg-white/70 px-4 py-2 text-sm text-[#6a4a37] shadow">
				{typingText}
			</div>
		</div>
	{/if}

	{#if lastMessageFromSelf && seenTimestamp}
		<p class="pr-4 text-right text-xs text-[#7d5b45]">
			Seen • {seenTimestamp.toLocaleTimeString()}
		</p>
	{/if}
</div>
