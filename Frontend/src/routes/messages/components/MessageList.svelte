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

<div class="flex-1 overflow-y-auto px-6 py-6 space-y-4" bind:this={listRef} on:scroll={handleScroll}>
	{#each messages as message (message.id)}
		<div class={"flex " + (message.senderId === currentUserId ? 'justify-end' : 'justify-start')}>
			<div
				class={`max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-lg ${
					message.senderId === currentUserId
						? 'bg-gradient-to-br from-[#0a86ff] via-[#0f59ff] to-[#7b1dff] text-white rounded-tr-sm'
						: 'bg-[#fff6ee] text-[#3a2315] rounded-tl-sm border border-[#f5e1ce] shadow-[0_4px_12px_rgba(0,0,0,0.08)]'
				}`}
			>
				<p class="leading-relaxed">{message.content}</p>
				<p class={`text-[11px] mt-1 ${message.senderId === currentUserId ? 'text-white/60' : 'text-[#a37758]'}`}>
					{new Date(message.createdAt).toLocaleString()}
				</p>
			</div>
		</div>
	{/each}

	{#if typingText}
		<div class="flex justify-start">
			<div class="px-4 py-2 rounded-2xl bg-white/70 text-[#6a4a37] text-sm shadow">
				{typingText}
			</div>
		</div>
	{/if}

	{#if lastMessageFromSelf && seenTimestamp}
		<p class="text-xs text-[#7d5b45] text-right pr-4">Seen • {seenTimestamp.toLocaleTimeString()}</p>
	{/if}
</div>


