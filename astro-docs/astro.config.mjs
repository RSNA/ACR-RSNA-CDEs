import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://rsna.github.io',
	base: '/ACR-RSNA-CDEs',
	integrations: [
		starlight({
			title: 'RSNA/ACR Common Data Elements',
			social: {
				github: 'https://github.com/withastro/starlight',
			},
			sidebar: [
				{
					label: 'Guides',
					items: [
						// Each item here is one entry in the navigation menu.
						{ label: 'Authoring and Conventions', slug: 'guides/author' },
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
