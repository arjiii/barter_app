import { itemService } from './itemService';
import { api } from '../config/api';

class SeedService {
	async seedInitialData(): Promise<void> {
		try {
			// Only ensure categories exist via API
			await this.seedCategories();
		} catch (error) {
			console.error('❌ Error seeding initial data:', error);
		}
	}

	private async seedCategories(): Promise<void> {
		const categories = [
			{ name: 'Electronics', description: 'Electronic devices and gadgets', icon: '📱' },
			{ name: 'Services', description: 'Professional and personal services', icon: '🔧' },
			{ name: 'Tools', description: 'Hand tools and equipment', icon: '🔨' },
			{ name: 'Books', description: 'Books, magazines, and educational materials', icon: '📚' },
			{ name: 'Clothing', description: 'Clothing and accessories', icon: '👕' },
			{ name: 'Home & Garden', description: 'Home improvement and gardening items', icon: '🏠' },
			{ name: 'Sports & Recreation', description: 'Sports equipment and recreational items', icon: '⚽' },
			{ name: 'Art & Crafts', description: 'Art supplies and craft materials', icon: '🎨' }
		];

		// If categories already present, skip
		const existing = await api.get<any[]>(`/categories/`);
		if (existing && existing.length > 0) return;

		for (const category of categories) {
			await itemService.createCategory(category);
		}
	}

	private async seedSampleData(): Promise<void> { /* no-op in API-backed mode */ }

	async clearAllData(): Promise<void> { /* no-op in API-backed mode */ }
}

export const seedService = new SeedService();
export default seedService;
