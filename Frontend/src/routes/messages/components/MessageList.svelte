<script lang="ts">
	import { afterUpdate, createEventDispatcher, onMount } from 'svelte';
	import type { Message } from '$lib/types/messages';

	export let messages: Message[] = [];
	export let currentUserId: string | null = null;
	export let typingText = '';
	export let seenTimestamp: string | null = null;

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
		.filter((message) => message.sender_id === currentUserId)
		.slice(-1)[0];
</script>

<div
	class="flex-1 space-y-4 overflow-y-auto px-4 py-4 lg:px-6 lg:py-6"
	bind:this={listRef}
	on:scroll={handleScroll}
>
	{#each messages as message (message.id)}
		<div class={'flex ' + (message.sender_id === currentUserId ? 'justify-end' : 'justify-start')}>
			<div
				class={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm shadow-sm lg:max-w-[75%] ${
					message.sender_id === currentUserId
						? 'rounded-br-sm bg-red-600 text-white'
						: 'rounded-bl-sm bg-gray-100 text-gray-900'
				}`}
			>
				<p class="whitespace-pre-wrap leading-relaxed">{message.content}</p>
				<p
					class={`mt-1 text-[10px] ${message.sender_id === currentUserId ? 'text-red-100' : 'text-gray-500'}`}
				>
					{new Date(message.created_at).toLocaleTimeString([], {
						hour: '2-digit',
						minute: '2-digit'
					})}
				</p>
			</div>
		</div>
	{/each}

	{#if typingText}
		<div class="flex justify-start">
			<div class="rounded-2xl bg-gray-100 px-4 py-2 text-sm text-gray-500">
				<div class="flex items-center gap-1">
					<span class="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400"></span>
					<span class="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400 delay-75"></span>
					<span class="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400 delay-150"></span>
				</div>
			</div>
		</div>
	{/if}

	{#if lastMessageFromSelf && seenTimestamp}
		<div class="flex justify-end pr-1">
			<p class="text-[10px] font-medium text-gray-400">
				Seen {new Date(seenTimestamp).toLocaleTimeString([], {
					hour: '2-digit',
					minute: '2-digit'
				})}
			</p>
		</div>
	{/if}
</div>
