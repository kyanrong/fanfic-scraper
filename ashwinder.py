import requests
import time
import yaml
from bs4 import BeautifulSoup
from html2docx import html2docx
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


driver_path = './chromedriver.exe'
credentials_path = './credentials.yml'
base_url = 'http://ashwinder.sycophanthex.com'
user_php = 'user.php'
story_php = 'viewstory.php?sid='


def get_metadata(driver, story_id):
	driver.get('{}/{}{}'.format(base_url, story_php, story_id))

	page = driver.page_source
	soup = BeautifulSoup(page, 'html.parser')

	title = soup.find('h4').string
	
	table = soup.find_all('table')[-1]
	author = table.find('a', href=lambda x: x.startswith('viewuser')).string

	chapters = []
	for row in table.find_all('tr'):
		chapters.append(row.find('a')['href'])

	return (title, author, chapters)


def get_chapter(driver, chapter_php):
	driver.get('{}/{}'.format(base_url, chapter_php))

	page = driver.page_source
	soup = BeautifulSoup(page, 'html.parser')

	contents  = soup.find(class_='story').contents
	arr = []
	for x in contents:
		x = str(x)
		arr.append(x)

	return ''.join(arr)


def login(driver):
	driver.get('{}/{}'.format(base_url, user_php))
	
	credentials = yaml.load(open(credentials_path))
	penname = credentials['ashwinder']['penname']
	password = credentials['ashwinder']['password']

	driver.find_element_by_name('penname').send_keys(penname)
	driver.find_element_by_name('password').send_keys(password)
	driver.find_element_by_name('submit').click()


def scrape(story_id):
	print('Scraping from Ashwinder')

	options = Options()
	options.headless = True
	driver = webdriver.Chrome(options=options, executable_path=driver_path)
	
	login(driver)

	(title, author, chapters) = get_metadata(driver, story_id)
	title_html = '<p style="text-align:center"><strong>{}</strong></p>'.format(title)
	author_html = '<p style="text-align:center">by {}</p>'.format(author)
	break_html = '<p style="text-align:center">*****</p>'

	print('Grabbing "{}" by {}'.format(title, author))

	all_html = [title_html, author_html,  break_html]
	for chapter in range(1, len(chapters)+1):
		print('Chapter {}/{}'.format(chapter, len(chapters)))
		content = get_chapter(driver, chapters[chapter-1])
		all_html.append(content)
		time.sleep(1)

	all_html_string = ''.join(all_html)
	buf = html2docx(all_html_string, title=title)
	with open('{}.docx'.format(title), 'wb') as fp:
		fp.write(buf.getvalue())

	print('Donezo!')
	