<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Navigation from './components/Navigation.svelte';
	import Footer from './components/Footer.svelte';
	import { page } from '$app/stores';

	let { children } = $props();

	// Pages that don't need navigation
	const noNavPages = ['/sign-in-up', '/'];
	let showNavigation = $derived(
		!noNavPages.includes($page.url.pathname) && !$page.url.pathname.startsWith('/admin')
	);
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Bayanihan Exchange - Community Barter App</title>
	<meta
		name="description"
		content="A blockchain-powered community barter app where neighbors help neighbors through secure trading."
	/>
</svelte:head>

{#if showNavigation}
	<Navigation>
		{@render children?.()}
	</Navigation>
{:else}
	<main class="min-h-screen bg-gray-50">
		{@render children?.()}
	</main>
	{#if !$page.url.pathname.startsWith('/admin')}
		<Footer />
	{/if}
{/if}
