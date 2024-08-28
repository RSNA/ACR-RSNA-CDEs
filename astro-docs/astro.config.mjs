import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://rsna.github.io',
	base: '/ACR-RSNA-CDEs',
	integrations: [
		starlight({
			title: 'RSNA/ACR Common Data Elements',
			sidebar: [
				{
					label: 'Guides',
					items: [
						// Each item here is one entry in the navigation menu.
						{ label: 'Authoring and Conventions', slug: 'guides/author' },
						{ label: 'Review Process', slug: 'guides/review' },
						{ label: 'Use CDEs in PowerScribe', slug: 'guides/powerscribe'}
					],
				},
				{
					label: 'Reference',
					items: [
						{ label: 'Set Standards', slug: 'reference/set' },
						{ label: 'Element Standards', slug: 'reference/element' },
						{ label: 'Value Set and Value Standards', slug: 'reference/valueset' }
					]
				},
			],
		}),
	],
});
