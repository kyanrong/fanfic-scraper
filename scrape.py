import ashwinder
import fanfiction_net

while True:
	print(
		'[1] FanFiction.net' + '\n' +
		'[2] Ashwinder'
	)
	site_id = input('Select site to scrape from: ')
	site_id = int(site_id)

	if site_id > 2:
		print('Detention! Hundred points off for the inability to follow instructions.')
	else:
		story_id = input('Enter the story id: ')
		if site_id == 1:
			fanfiction_net.scrape(story_id)
		elif site_id == 2:
			ashwinder.scrape(story_id)
