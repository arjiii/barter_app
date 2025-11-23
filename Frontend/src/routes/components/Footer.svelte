<script lang="ts">
	import { navigationConfig } from '$lib/config/navigation';
	import { goto } from '$app/navigation';

	function handleFooterClick(item: any) {
		if (item.href) {
			goto(item.href);
		}
	}
</script>

<footer class="bg-gray-900 text-white">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
		<div class="grid grid-cols-1 md:grid-cols-4 gap-8">
			<!-- Brand -->
			<div class="col-span-1 md:col-span-2">
				<div class="flex items-center space-x-3 mb-4">
					<div class="w-10 h-10 bg-gradient-to-r from-red-600 to-red-700 rounded-lg flex items-center justify-center">
						<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
						</svg>
					</div>
					<div>
						<h3 class="text-xl font-bold">Bayanihan Exchange</h3>
						<p class="text-gray-400 text-sm">Community Barter App</p>
					</div>
				</div>
				<p class="text-gray-400 text-sm max-w-md">
					A blockchain-powered community barter app where neighbors help neighbors through secure trading. 
					Building stronger communities, one trade at a time.
				</p>
			</div>

			<!-- Quick Links -->
			<div>
				<h4 class="text-lg font-semibold mb-4">Quick Links</h4>
				<ul class="space-y-2">
					{#each navigationConfig.main as item}
						<li>
							<button
								onclick={() => handleFooterClick(item)}
								class="text-gray-400 hover:text-white transition-colors text-sm"
							>
								{item.label}
							</button>
						</li>
					{/each}
				</ul>
			</div>

			<!-- Legal -->
			<div>
				<h4 class="text-lg font-semibold mb-4">Legal</h4>
				<ul class="space-y-2">
					{#each navigationConfig.footer as item}
						<li>
							<button
								onclick={() => handleFooterClick(item)}
								class="text-gray-400 hover:text-white transition-colors text-sm"
							>
								{item.label}
							</button>
						</li>
					{/each}
				</ul>
			</div>
		</div>

		<!-- Bottom Bar -->
		<div class="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
			<p class="text-gray-400 text-sm">
				© 2024 Bayanihan Exchange. All rights reserved.
			</p>
			<div class="flex items-center space-x-4 mt-4 md:mt-0">
				<span class="text-gray-400 text-sm">Made with ❤️ in the Philippines</span>
			</div>
		</div>
	</div>
</footer>
