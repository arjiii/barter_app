<script lang="ts">
	import { goto } from '$app/navigation';

	type Stat = { label: string; value: string; subtext?: string };
	type Feature = { title: string; description: string; icon: string; badge?: string };
	type Step = { title: string; body: string; action: string };
	type Testimonial = { quote: string; author: string; role: string };
	type Faq = { question: string; answer: string };
	type RevealConfig = {
		threshold?: number;
		once?: boolean;
		delay?: number;
		rootMargin?: string;
	};

	const stats: Stat[] = [
		{ label: 'Neighbors trading', value: '12,480+', subtext: 'verified barangay members' },
		{ label: 'Trades completed', value: '31,600+', subtext: 'settled on-chain' },
		{ label: 'Carbon saved', value: '486 tons', subtext: 'by reusing goods' }
	];

	const heroHighlights = [
		'Barangay-verified profiles',
		'Smart-contract escrow',
		'Disaster response ready'
	];

	const features: Feature[] = [
		{
			title: 'Trust built-in',
			description:
				'Barangay ID validation, dispute resolution, and transparent history give every swap a trusted paper trail.',
			icon: 'M5 13l4 4L19 7',
			badge: 'Security'
		},
		{
			title: 'Local-first discovery',
			description:
				'Pin drops, category filters, and topic hubs make it simple to find neighbors with exactly what you need.',
			icon: 'M12 2C8.134 2 5 5.134 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.866-3.134-7-7-7z'
		},
		{
			title: 'Fair-value trades',
			description:
				'AI-powered suggestions and multi-item offers make swapping bikes for surf lessons (and more) feel effortless.',
			icon: 'M4 7h16M4 12h16M4 17h16',
			badge: 'New'
		},
		{
			title: 'Messaging that matters',
			description:
				'Context-aware chat, embedded item cards, and pinned agreements keep every deal tidy and transparent.',
			icon: 'M8 10h.01M12 10h.01M16 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
		},
		{
			title: 'Community missions',
			description:
				'Organize donation drives, school supply swaps, or disaster relief kits with goal trackers and broadcast updates.',
			icon: 'M3 3h18M9 7v14m6-14v14M5 21h14',
			badge: 'Community'
		},
		{
			title: 'Smart inventory',
			description:
				'Auto-generated catalogs, reminders to relist, and condition tracking keep your barter shelf always ready.',
			icon: 'M4 6h16M4 12h16M4 18h16'
		}
	];

	const steps: Step[] = [
		{
			title: 'List or request',
			body: 'Snap a photo, add condition, tag your barangay, and publish in under 60 seconds.',
			action: 'Post an item'
		},
		{
			title: 'Match & message',
			body: 'Browse curated feeds, send bundled offers, and chat with real neighbors using secured identities.',
			action: 'Start a trade'
		},
		{
			title: 'Swap with confidence',
			body: 'Meet at a SafeSwap zone or request doorstep pickup. Smart-contract receipts back every deal.',
			action: 'Confirm exchange'
		}
	];

	const testimonials: Testimonial[] = [
		{
			quote:
				'We mobilized 400+ emergency kits in 48 hours after the typhoon. Bayanihan Exchange gave our barangay an instant command center.',
			author: 'Kapitan Liza Mendoza',
			role: 'Barangay 271 | Manila'
		},
		{
			quote:
				'The trust badges and escrow made it easy to swap my camera gear for a laptop. Zero awkward haggling, 100% community vibes.',
			author: 'Ronnie Magno',
			role: 'Freelance Designer | Cebu'
		},
		{
			quote:
				'We outfitted an entire classroom with reused desks from neighbors. The sustainability stats kept donors engaged.',
			author: 'Teacher Mae Alvarez',
			role: 'Public School 19 | Iloilo'
		}
	];

	const faqs: Faq[] = [
		{
			question: 'How do I join the barter community?',
			answer:
				'Tap “Get started”, complete barangay verification, and you can publish your first listing or request immediately.'
		},
		{
			question: 'Is every trade secured on blockchain?',
			answer:
				'Yes. Smart-contract receipts provide immutable proof of value, conditions, and mutual acceptance for every approved trade.'
		},
		{
			question: 'Can I barter services and time?',
			answer:
				'Absolutely. Create offers for lessons, repairs, rides, or volunteering hours and pair them with goods if needed.'
		},
		{
			question: 'What if something goes wrong?',
			answer:
				'Community mediators and barangay admins can review the on-chain record, pause disputed trades, and issue resolutions.'
		}
	];

	const partnerLogos = ['Community Dev Office', 'Smart Impact Lab', 'UNDP Accelerator', 'PH Resilience Hub'];

	const handleCta = (path: string) => goto(path);

	const reveal = (node: HTMLElement, config: RevealConfig = {}) => {
		const { threshold = 0.2, once = false, delay = 0, rootMargin = '0px' } = config;

		const applyVisible = () => {
			node.style.transitionDelay = `${delay}ms`;
			node.classList.add('reveal-visible');
			node.classList.remove('reveal-hidden');
		};

		const applyHidden = () => {
			node.classList.add('reveal-hidden');
			node.classList.remove('reveal-visible');
		};

		let observer: IntersectionObserver | null = null;
		const isBrowser = typeof window !== 'undefined';
		const prefersReducedMotion = isBrowser
			? window.matchMedia('(prefers-reduced-motion: reduce)').matches
			: false;

		if (!prefersReducedMotion && isBrowser) {
			applyHidden();
			observer = new IntersectionObserver(
				(entries) => {
					entries.forEach((entry) => {
						if (entry.isIntersecting) {
							applyVisible();
							if (once && observer) {
								observer.unobserve(node);
							}
						} else if (!once) {
							applyHidden();
						}
					});
				},
				{ threshold, rootMargin }
			);

			observer.observe(node);
		} else {
			applyVisible();
		}

		return {
			destroy() {
				if (observer) {
					observer.disconnect();
				}
			}
		};
	};
</script>

<svelte:head>
	<title>Bayanihan Exchange | Trade goods, skills, and hope</title>
	<meta
		name="description"
		content="Organize community-led barter drives powered by blockchain trust. Swap goods, services, and skills with neighbors in seconds."
	/>
</svelte:head>

<div class="bg-[#faf7f2] text-[#1f1b17] font-['Inter',sans-serif]">
	<section class="relative overflow-hidden pb-20 pt-12 sm:pt-16 lg:pt-20 bg-gradient-to-b from-[#fff7ef] via-[#fff3e7] to-[#ffe8d8]" use:reveal={{ threshold: 0.05 }}>
		<div class="absolute inset-0 opacity-60 blur-3xl pointer-events-none">
			<div class="h-72 w-72 rounded-full bg-[#ffd8c2] absolute -top-16 -left-10 floating-orb"></div>
			<div class="h-80 w-80 rounded-full bg-[#ffe9ce] absolute top-16 right-0 floating-orb" style="animation-delay: 4s;"></div>
		</div>
		<div class="hero-aurora hero-aurora--one"></div>
		<div class="hero-aurora hero-aurora--two"></div>

		<div class="relative max-w-6xl mx-auto px-6 lg:px-8">
			<header class="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between text-sm text-[#564a42]">
				<div class="flex items-center gap-3">
					<div class="h-11 w-11 rounded-2xl bg-white shadow-sm flex items-center justify-center">
						<svg viewBox="0 0 24 24" class="h-5 w-5 text-[#ff6d3f]" fill="none" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
						</svg>
					</div>
					<div>
						<p class="text-[0.65rem] uppercase tracking-[0.4em] text-[#a18573]">Bayanihan Exchange</p>
						<p class="text-xs text-[#7e6b5e]">Community barter re-imagined</p>
					</div>
				</div>

				<nav class="flex flex-wrap gap-4 font-medium">
					<a href="#features" class="hover:text-[#1f1b17] transition">Features</a>
					<a href="#how-it-works" class="hover:text-[#1f1b17] transition">How it works</a>
					<a href="#impact" class="hover:text-[#1f1b17] transition">Impact</a>
					<a href="#faq" class="hover:text-[#1f1b17] transition">FAQ</a>
				</nav>

				<div class="flex items-center gap-3">
					<button class="px-4 py-2 rounded-full border border-[#d9c5b6] text-[#4a3b32] hover:bg-white transition" onclick={() => handleCta('/sign-in-up?mode=signin')}>
						Sign in
					</button>
					<button class="px-4 py-2 rounded-full bg-[#1f1b17] text-white font-semibold hover:bg-black transition" onclick={() => handleCta('/sign-in-up?mode=signup')}>
						Get started
					</button>
				</div>
			</header>

			<div class="mt-16 grid gap-12 lg:grid-cols-[1.1fr,0.9fr]">
				<div class="space-y-8" use:reveal={{ threshold: 0.1 }}>
					<div class="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm text-[#4a3b32] shadow-sm">
						<span class="h-2.5 w-2.5 rounded-full bg-[#3ecf8e] animate-pulse"></span>
						Live in 132 barangays nationwide
					</div>

					<div class="space-y-5">
						<h1 class="text-4xl font-semibold leading-tight text-[#1f1b17] sm:text-5xl lg:text-[3.2rem] animated-text">
							Trade goods, skills, and hope—powered by blockchain trust.
						</h1>
					<p class="text-base text-[#3d332d] max-w-2xl animated-copy">
							Bayanihan Exchange unites neighbors, NGOs, and barangay halls in one resilient barter network.
							Launch community drives, reroute unused goods, and track impact with transparent smart contracts.
						</p>
					</div>

					<div class="flex flex-wrap gap-4">
						<button class="rounded-full bg-[#1f1b17] px-8 py-3 text-base font-semibold text-white shadow-lg shadow-[#1f1b17]/10 transition hover:-translate-y-0.5 glow-button" onclick={() => handleCta('/sign-in-up?mode=signup')}>
							Create free account
						</button>
						<button class="rounded-full border border-[#cbb8a8] px-8 py-3 text-base font-semibold text-[#1f1b17] hover:bg-white" onclick={() => handleCta('/sign-in-up?mode=signin')}>
							Sign in to existing account
						</button>
						<button class="rounded-full border border-transparent bg-white px-8 py-3 text-base font-semibold text-[#4a3b32] shadow-sm hover:shadow" onclick={() => handleCta('/discovery')}>
							Browse marketplace
						</button>
					</div>

					<div class="flex flex-wrap gap-3 text-sm text-[#67584f]">
						{#each heroHighlights as highlight}
							<span class="flex items-center gap-2 rounded-full border border-[#f0e4d9] bg-white px-4 py-2 pulse-pill">
								<svg viewBox="0 0 24 24" class="h-4 w-4 text-[#46c58b]" fill="none" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
								{highlight}
							</span>
						{/each}
					</div>
				</div>

				<div class="space-y-6" use:reveal={{ threshold: 0.15 }}>
					<div class="rounded-3xl bg-white shadow-[0_15px_55px_rgba(15,11,8,0.08)] p-6">
						<div class="flex justify-between text-[0.7rem] uppercase tracking-[0.35em] text-[#b19b8d]">
							<span>Live barter board</span>
							<span>On-chain escrow</span>
						</div>

						<div class="mt-4 space-y-4">
							{#each [
								{ item: 'Solar lantern x2', want: 'Rice packs', status: 'Verifying barangay IDs' },
								{ item: 'Surf lessons (3hrs)', want: 'Mountain bike tune-up', status: 'Offer matched' },
								{ item: 'Desktop PC set', want: 'School chairs', status: 'Escrow funded' }
							] as trade}
								<div class="rounded-2xl border border-[#f2e3d7] bg-[#fff9f4] p-4">
									<p class="text-xs uppercase tracking-[0.3em] text-[#b19b8d]">{trade.status}</p>
									<p class="mt-2 text-lg font-semibold text-[#1f1b17]">{trade.item}</p>
									<p class="text-sm text-[#6f5d53]">for {trade.want}</p>
								</div>
							{/each}
						</div>

						<div class="mt-6 rounded-2xl bg-gradient-to-r from-[#ffb997] to-[#ff8e72] p-4 text-sm font-semibold text-white shadow-inner">
							Barangay 87 activated a relief drive · 156 pledges secured
						</div>
					</div>

					<div class="grid gap-4 sm:grid-cols-3 text-center text-sm text-[#6f5d53]">
						{#each stats as stat}
							<div class="rounded-2xl border border-[#f0e4d9] bg-white px-4 py-6 shadow">
								<p class="text-2xl font-semibold text-[#1f1b17]">{stat.value}</p>
								<p class="mt-1 font-medium uppercase tracking-wide text-[0.65rem] text-[#a48774]">{stat.label}</p>
								{#if stat.subtext}
									<p class="mt-1 text-[#8f7a6c]">{stat.subtext}</p>
								{/if}
							</div>
						{/each}
					</div>
				</div>
			</div>

			<div class="mt-16 flex flex-wrap items-center gap-4 text-[0.7rem] uppercase text-[#9c8779] tracking-[0.2em]">
				<span class="text-[#b0998a]">Partnered with</span>
				<div class="flex flex-wrap gap-3">
					{#each partnerLogos as partner}
						<span class="rounded-full border border-[#f0e4d9] bg-white px-4 py-2 text-[#615149] text-xs">{partner}</span>
					{/each}
				</div>
			</div>

			<div class="scroll-indicator" use:reveal={{ threshold: 0.2 }}>
				<span></span>
				<p>Scroll to explore</p>
			</div>
		</div>
	</section>

	<section id="features" class="border-t border-[#f0e4d9] bg-[#fffaf4] py-20" use:reveal={{ threshold: 0.05 }}>
		<div class="mx-auto max-w-6xl px-6 lg:px-8">
			<div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
				<div>
					<p class="text-xs uppercase tracking-[0.5em] text-[#ff8e72] animated-copy">Why Bayanihan</p>
					<h2 class="mt-2 text-3xl font-semibold text-[#1f1b17] sm:text-4xl animated-text">Purpose-built for community barter.</h2>
				</div>
				<p class="text-[#3c312a] max-w-xl animated-copy">
					Every capability comes from months of co-design with barangay captains, disaster response units, and grassroots entrepreneurs.
				</p>
			</div>

			<div class="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each features as feature, index}
					<article
						class="rounded-3xl border border-[#f3e5d9] bg-white p-6 shadow-sm card-hover"
						use:reveal={{ delay: index * 60 }}
					>
						<div class="flex items-center gap-3">
							<div class="rounded-2xl bg-[#fff3ea] p-3 text-[#ff6d3f]">
								<svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={feature.icon} />
								</svg>
							</div>
							{#if feature.badge}
								<span class="rounded-full bg-[#ffe1d2] px-3 py-1 text-xs font-semibold text-[#b25f3b]">{feature.badge}</span>
							{/if}
						</div>
						<h3 class="mt-6 text-xl font-semibold text-[#211c18]">{feature.title}</h3>
						<p class="mt-3 text-[#4b3f37]">{feature.description}</p>
					</article>
				{/each}
			</div>
		</div>
	</section>

	<section id="how-it-works" class="bg-gradient-to-b from-[#fffaf4] to-[#f9ede3] py-20" use:reveal={{ threshold: 0.05 }}>
		<div class="mx-auto max-w-6xl px-6 lg:px-8">
			<div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
				<div>
					<p class="text-xs uppercase tracking-[0.5em] text-[#ff8e72] animated-copy">How it works</p>
					<h2 class="mt-2 text-3xl font-semibold text-[#1f1b17] sm:text-4xl animated-text">3 steps to your next swap.</h2>
					<p class="mt-4 text-[#6f5d53] max-w-2xl animated-copy">
						Built for barangay hall workflows—no crypto wallets required. We abstract the blockchain jargon so your focus stays on people.
					</p>
				</div>
				<button class="rounded-full border border-[#e5d5c9] px-5 py-3 text-sm font-semibold text-[#1f1b17] hover:bg-white" onclick={() => handleCta('/sign-in-up?mode=signup')}>
					Create free account
				</button>
			</div>

			<div class="mt-12 grid gap-6 lg:grid-cols-3">
				{#each steps as step, index}
					<div class="rounded-3xl border border-[#f0e4d9] bg-white p-6 card-hover" use:reveal={{ delay: index * 80 }}>
						<div class="flex items-center justify-between">
							<span class="text-xs uppercase tracking-[0.5em] text-[#b19b8d]">Step {index + 1}</span>
							<span class="rounded-full bg-[#fff3ea] px-3 py-1 text-xs text-[#a45b3c]">{step.action}</span>
						</div>
						<h3 class="mt-4 text-2xl font-semibold text-[#201b17]">{step.title}</h3>
						<p class="mt-3 text-[#463b34]">{step.body}</p>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<section id="impact" class="border-t border-[#f0e4d9] bg-[#fff8f1] py-20">
		<div class="mx-auto max-w-6xl px-6 lg:px-8">
			<div class="grid gap-12 lg:grid-cols-[1.1fr,0.9fr]">
				<div class="space-y-6" use:reveal={{ threshold: 0.15 }}>
					<p class="text-xs uppercase tracking-[0.5em] text-[#46c58b] animated-copy">Impact in motion</p>
					<h2 class="text-3xl font-semibold text-[#1f1b17] sm:text-4xl animated-text">Data your city hall will love.</h2>
					<p class="text-[#3c312a] animated-copy">
						Every barter automatically logs environmental savings, economic value, and volunteer hours. Export-ready dashboards help barangays secure funding faster.
					</p>

					<div class="grid gap-4 sm:grid-cols-2">
						<div class="rounded-3xl border border-[#e6d8cb] bg-white p-5 stat-card">
							<p class="text-[0.65rem] uppercase tracking-[0.4em] text-[#897363]">Relief drives this month</p>
							<p class="mt-3 text-4xl font-semibold text-[#1b1613]">42</p>
							<p class="text-sm text-[#4f433b]">12,800 beneficiaries & counting</p>
						</div>
						<div class="rounded-3xl border border-[#e6d8cb] bg-white p-5 stat-card">
							<p class="text-[0.65rem] uppercase tracking-[0.4em] text-[#897363]">Goods upcycled</p>
							<p class="mt-3 text-4xl font-semibold text-[#1b1613]">68%</p>
							<p class="text-sm text-[#4f433b]">increase vs. last quarter</p>
						</div>
					</div>

					<div class="rounded-3xl bg-gradient-to-r from-[#e7fde4] to-[#e7f5ff] p-6 text-sm text-[#355a3f]">
						<div class="flex items-center gap-3 text-[#2c241f]">
							<div class="h-10 w-10 rounded-2xl bg-white flex items-center justify-center text-[#46c58b] shadow">
								<svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
							</div>
							<p>
								Certified by the Philippine Disaster Resilience Foundation for use in community-based preparedness programs.
							</p>
						</div>
					</div>
				</div>

				<div class="space-y-6" use:reveal={{ threshold: 0.15, delay: 150 }}>
					<div class="rounded-3xl border border-[#f0e4d9] bg-white p-6 shadow-sm">
					<p class="text-xs uppercase tracking-[0.5em] text-[#ff8e72] animated-copy">Testimonials</p>
						<div class="mt-6 space-y-6">
							{#each testimonials as testimonial}
								<blockquote class="rounded-2xl bg-[#fff7ef] p-5 border border-[#f4dfd0]">
									<p class="text-[#4a3b32]">“{testimonial.quote}”</p>
									<footer class="mt-4 text-sm text-[#967e6c]">
										<strong class="text-[#1f1b17]">{testimonial.author}</strong> · {testimonial.role}
									</footer>
								</blockquote>
							{/each}
						</div>
					</div>

					<div class="rounded-3xl border border-[#f0e4d9] bg-white p-6 card-hover">
					<p class="text-xs uppercase tracking-[0.5em] text-[#b19b8d] animated-copy">Community spotlight</p>
						<div class="mt-4 space-y-4 text-sm text-[#6f5d53]">
							<div class="flex items-center justify-between rounded-2xl bg-[#fff7ef] p-4">
								<div>
									<p class="font-semibold text-[#1a1512]">Quezon City Bike Library</p>
									<p class="text-[#5a4b42]">62 bikes donated · 180 riders served</p>
								</div>
								<span class="rounded-full bg-[#d3f9d8] px-3 py-1 text-xs text-[#297f4f]">ACTIVE</span>
							</div>
							<div class="flex items-center justify-between rounded-2xl bg-[#fff7ef] p-4">
								<div>
									<p class="font-semibold text-[#1a1512]">Visayas Classroom Refresh</p>
									<p class="text-[#5a4b42]">208 chairs · 93 desks matched</p>
								</div>
								<span class="rounded-full bg-[#ffe1cc] px-3 py-1 text-xs text-[#b65c34]">IN PROGRESS</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<section id="faq" class="border-t border-[#f0e4d9] bg-[#fffaf4] py-20" use:reveal={{ threshold: 0.05 }}>
		<div class="mx-auto max-w-6xl px-6 lg:px-8">
			<div class="grid gap-10 lg:grid-cols-[0.8fr,1.2fr]">
				<div use:reveal={{ threshold: 0.1 }}>
					<p class="text-xs uppercase tracking-[0.5em] text-[#b19b8d] animated-copy">Questions?</p>
					<h2 class="mt-3 text-3xl font-semibold text-[#1f1b17] animated-text">We’re here for every barangay leader.</h2>
					<p class="mt-4 text-[#6f5d53] animated-copy">
						Not sure how to kickstart your barter hub? Book a 15-minute onboarding with our community playbook team.
					</p>
					<div class="mt-6 flex flex-wrap gap-3 text-sm text-[#4a3b32]">
						<button class="rounded-2xl border border-[#e5d5c9] px-6 py-3 font-semibold hover:bg-white" onclick={() => handleCta('/sign-in-up?mode=signup')}>
							Schedule onboarding
						</button>
						<button class="rounded-2xl bg-[#1f1b17] text-white px-6 py-3 font-semibold hover:bg-black" onclick={() => handleCta('/help')}>
							Visit help center
						</button>
					</div>
				</div>

				<div class="space-y-4">
					{#each faqs as faq, index}
						<details class="rounded-2xl border border-[#f0e4d9] bg-white p-5" use:reveal={{ delay: index * 60 }}>
							<summary class="cursor-pointer text-lg font-semibold text-[#1f1b17]">{faq.question}</summary>
							<p class="mt-3 text-[#6f5d53]">{faq.answer}</p>
						</details>
					{/each}
				</div>
			</div>
		</div>
	</section>

	<section class="border-t border-[#f0e4d9] bg-gradient-to-r from-[#ffe9d9] via-[#ffdac5] to-[#ffc6b8] py-16" use:reveal={{ threshold: 0.05 }}>
		<div class="mx-auto flex max-w-5xl flex-col gap-8 px-6 text-center text-[#1f1b17] lg:px-8">
			<h2 class="text-3xl font-semibold sm:text-4xl animated-text">Ready to relaunch barter culture in your community?</h2>
			<p class="text-base text-[#5d4c44] animated-copy">
				Spin up your first campaign in minutes, invite neighbors with magic links, and monitor every impact metric from one dashboard.
			</p>
			<div class="flex flex-wrap justify-center gap-4">
				<button class="rounded-full bg-[#1f1b17] px-8 py-3 text-base font-semibold text-white hover:bg-black" onclick={() => handleCta('/sign-in-up?mode=signup')}>
					Start free
				</button>
				<button class="rounded-full border border-[#1f1b17] px-8 py-3 text-base font-semibold text-[#1f1b17] hover:bg-[#1f1b17] hover:text-white transition" onclick={() => handleCta('/discovery')}>
					Explore live trades
				</button>
			</div>
		</div>
	</section>
</div>

<style>
	:global(.animated-text) {
		background-image: linear-gradient(120deg, #7c4a3f 0%, #ff9f7e 50%, #d86a3f 100%);
		background-size: 200% auto;
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		animation: textGlow 8s ease-in-out infinite;
	}

	:global(.animated-copy) {
		color: rgba(92, 79, 71, 0.9);
		animation: copyBreathe 6s ease-in-out infinite;
	}

	@keyframes textGlow {
		0% {
			background-position: 0% 50%;
			filter: drop-shadow(0 0 0 rgba(216, 106, 63, 0));
		}
		50% {
			background-position: 100% 50%;
			filter: drop-shadow(0 8px 20px rgba(216, 106, 63, 0.25));
		}
		100% {
			background-position: 0% 50%;
			filter: drop-shadow(0 0 0 rgba(216, 106, 63, 0));
		}
	}

	@keyframes copyBreathe {
		0%,
		100% {
			color: rgba(92, 79, 71, 0.75);
		}
		50% {
			color: rgba(41, 31, 28, 0.9);
		}
	}

	:global(.hero-aurora) {
		position: absolute;
		width: 60%;
		height: 60%;
		filter: blur(140px);
		opacity: 0.45;
		z-index: 0;
		animation: auroraShift 18s ease-in-out infinite alternate;
	}

	:global(.hero-aurora--one) {
		top: -20%;
		left: -10%;
		background: radial-gradient(circle, rgba(255, 215, 197, 0.8), transparent 60%);
	}

	:global(.hero-aurora--two) {
		bottom: -30%;
		right: -20%;
		background: radial-gradient(circle, rgba(255, 231, 196, 0.8), transparent 60%);
		animation-delay: 6s;
	}

	@keyframes auroraShift {
		0% {
			transform: translate3d(0, 0, 0) scale(1);
		}
		100% {
			transform: translate3d(5%, -5%, 0) scale(1.1);
		}
	}

	:global(.floating-orb) {
		animation: orbFloat 20s ease-in-out infinite alternate;
	}

	@keyframes orbFloat {
		0% {
			transform: translate3d(0, 0, 0) scale(1);
		}
		50% {
			transform: translate3d(20px, -10px, 0) scale(1.05);
		}
		100% {
			transform: translate3d(-10px, 15px, 0) scale(0.98);
		}
	}

	:global(.glow-button) {
		position: relative;
		overflow: hidden;
	}

	:global(.glow-button::after) {
		content: '';
		position: absolute;
		top: -50%;
		left: -50%;
		width: 200%;
		height: 200%;
		background: radial-gradient(circle, rgba(255, 255, 255, 0.3), transparent 60%);
		opacity: 0;
		animation: buttonGlow 4s ease-in-out infinite;
	}

	@keyframes buttonGlow {
		0%,
		60% {
			opacity: 0;
			transform: scale(0.6);
		}
		80% {
			opacity: 0.8;
		}
		100% {
			opacity: 0;
			transform: scale(1.2);
		}
	}

	:global(.scroll-indicator) {
		margin-top: 3rem;
		display: inline-flex;
		align-items: center;
		gap: 0.75rem;
		color: rgba(148, 163, 184, 0.8);
		font-size: 0.85rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
	}

	:global(.scroll-indicator span) {
		display: inline-block;
		width: 30px;
		height: 30px;
		border-radius: 999px;
		border: 1px solid rgba(31, 27, 23, 0.3);
		position: relative;
	}

	:global(.scroll-indicator span::after) {
		content: '';
		position: absolute;
		top: 6px;
		left: 50%;
		width: 6px;
		height: 6px;
		background: white;
		border-radius: 50%;
		transform: translateX(-50%);
		animation: scrollPulse 2.4s ease-in-out infinite;
	}

	@keyframes scrollPulse {
		0% {
			transform: translate(-50%, 0);
			opacity: 0;
		}
		40% {
			opacity: 1;
		}
		100% {
			transform: translate(-50%, 12px);
			opacity: 0;
		}
	}

	:global(.card-hover) {
		transition: transform 0.5s ease, border-color 0.5s ease, box-shadow 0.5s ease;
	}

	:global(.card-hover:hover) {
		transform: translateY(-6px);
		border-color: rgba(255, 149, 109, 0.4);
		box-shadow: 0 20px 40px rgba(31, 27, 23, 0.12);
	}

	:global(.stat-card) {
		position: relative;
		overflow: hidden;
	}

	:global(.stat-card::after) {
		content: '';
		position: absolute;
		top: -20%;
		left: -20%;
		width: 140%;
		height: 140%;
		background: radial-gradient(circle, rgba(255, 255, 255, 0.15), transparent 60%);
		animation: statGlow 8s ease-in-out infinite;
		z-index: 0;
	}

	:global(.stat-card > *) {
		position: relative;
		z-index: 1;
	}

	@keyframes statGlow {
		0% {
			transform: translate3d(-10%, -10%, 0);
			opacity: 0.3;
		}
		50% {
			transform: translate3d(10%, 10%, 0);
			opacity: 0.6;
		}
		100% {
			transform: translate3d(-5%, 5%, 0);
			opacity: 0.3;
		}
	}

	:global(.reveal-hidden) {
		opacity: 0;
		transform: translateY(48px) scale(0.975);
		filter: blur(6px);
		transition:
			opacity 1.2s cubic-bezier(0.16, 1, 0.3, 1),
			transform 1.2s cubic-bezier(0.16, 1, 0.3, 1),
			filter 1.2s cubic-bezier(0.16, 1, 0.3, 1);
		will-change: opacity, transform, filter;
	}

	:global(.reveal-visible) {
		opacity: 1;
		transform: translateY(0) scale(1);
		filter: blur(0);
	}

	@media (prefers-reduced-motion: reduce) {
		:global(.reveal-hidden),
		:global(.reveal-visible) {
			opacity: 1 !important;
			transform: none !important;
			filter: none !important;
			transition: none !important;
		}
		:global(.floating-orb),
		:global(.hero-aurora),
		:global(.scroll-indicator span::after),
		:global(.glow-button::after),
		:global(.stat-card::after) {
			animation: none !important;
		}
	}

	:global(.pulse-pill) {
		position: relative;
		overflow: hidden;
	}

	:global(.pulse-pill::after) {
		content: '';
		position: absolute;
		inset: -50%;
		background: radial-gradient(circle, rgba(190, 242, 100, 0.45), transparent 65%);
		animation: pillPulse 4s ease-in-out infinite;
		opacity: 0;
	}

	@keyframes pillPulse {
		0%,
		60% {
			opacity: 0;
			transform: scale(0.7);
		}
		80% {
			opacity: 0.4;
		}
		100% {
			opacity: 0;
			transform: scale(1.2);
		}
	}
</style>
