import requests
import time
from bs4 import BeautifulSoup
from html2docx import html2docx


base_url = 'https://fanfiction.net/s'


def get_metadata(url):
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')

	metadata = soup.find(id='profile_top')
	metadata_text = metadata.find(class_='xgray xcontrast_txt').text
	metadata_text_arr = list(map(lambda x: x.strip(), metadata_text.split('-')))

	title = metadata.find('b').string
	author = metadata.find('a', href=lambda x: x and '/u' in x).string
	synopsis = metadata.find('div', class_='xcontrast_txt').text

	chapters = [x for x in metadata_text_arr if x.startswith('Chapters')]
	if len(chapters) > 0:
		chapters = chapters[0]
		chapters = int(chapters.split(':')[1])
	else:
		chapters = 1

	return (title, author, synopsis, chapters)


def get_chapter(url):
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')

	paragraphs = soup.find(id='storytext').contents
	arr = []
	for x in paragraphs:
		x = str(x)
		if '<p>' in x:
			x = x.replace('<p>', '')
		if '</p>' in x:
			x = x.replace('</p>', '')
		x = x.strip()
		x = '<p>{}</p>'.format(x)
		arr.append(x)
	return ''.join(arr)


def scrape(story_id):
	print('Scraping from FanFiction.net')

	(title, author, synopsis, chapters) = get_metadata('{}/{}'.format(base_url, story_id))
	title_html = '<p style="text-align:center"><strong>{}</strong></p>'.format(title)
	author_html = '<p style="text-align:center">by {}</p>'.format(author)
	synopsis_html = '<p><em>{}</em></p>'.format(synopsis)
	break_html = '<p style="text-align:center">*****</p>'

	print('Grabbing "{}" by {}'.format(title, author))

	all_html = [title_html, author_html, synopsis_html, break_html]
	for chapter in range(1, chapters+1):
		print('Chapter {}/{}'.format(chapter, chapters))
		url = '{}/{}/{}'.format(base_url, story_id, chapter)
		content = get_chapter(url)
		all_html.append(content)
		time.sleep(1)

	all_html_string = ''.join(all_html)
	buf = html2docx(all_html_string, title=title)
	with open('{}.docx'.format(title), 'wb') as fp:
		fp.write(buf.getvalue())

	print('Donezo!')
