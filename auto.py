import datetime, os, time

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import Select

def link_validity(link):
	if link:
		return True

def return_pdf_link(link):
	response = requests.get(link)
	soup = BeautifulSoup(response.text, features="html.parser")
	pdf_links = soup.select('#attach_docs a')
	return [ f"""https://ireps.gov.in{pdf_link.get('onclick').split("'")[1]}""" for pdf_link in pdf_links ]

def initials(search_criteria):
	driver.get('https://ireps.gov.in/epsn/anonymSearch.do')
	driver.find_element_by_id('custumSearchId').click()
	# select the option Item Description
	Select(driver.find_element_by_css_selector('select[name=searchOption]')).select_by_value('4')
	field = driver.find_element_by_id('searchtext')
	field.send_keys(search_criteria)
	Select(driver.find_element_by_id('railwayZone')).select_by_value('-1')
	Select(driver.find_element_by_css_selector('select[name=selectDate]')).select_by_value('TENDER_PUBLISHING_DATE')
	# set the date
	previous_date = datetime.date.today() - datetime.timedelta(1)
	previous_date = previous_date.strftime('%d/%m/%Y')
	time.sleep(1)
	driver.execute_script(f'document.getElementById("ddmmyyDateformat1").value = "{previous_date}"')
	driver.execute_script(f'document.getElementById("ddmmyyDateformat2").value = "{previous_date}"')
	search_button = driver.find_element_by_css_selector('tr[id=searchButtonBlock] input[type=submit]')
	time.sleep(1)
	driver.execute_script("arguments[0].click();", search_button)

def download_pdf(link, path):
	filename = os.path.join(path, link.split('/')[-1]) 
	print(f"Downloading {filename}")
	with open(filename, 'wb') as fp:
		res = requests.get(link, stream=True)
		for chunk in res.iter_content(10000):
			if chunk:
				fp.write(chunk)
	print(f'Done Downloading {filename}\n')

def fetch_window_links():
	t = driver.find_element_by_xpath('/html/body/table/tbody/tr[4]/td[2]/table/tbody/tr/td/div/table/tbody/tr[1]/td/table/tbody/tr[2]/td/form/table[3]/tbody/tr[6]')
	rows = t.find_elements_by_tag_name('tr')[1:]
	for row in rows:
		data = row.find_elements_by_tag_name('td')
		tender_number = data[1].text.strip()
		end_date = data[5].text.split()[0].strip()
		href = data[7].find_element_by_css_selector('a').get_attribute('onclick')
		# pointers to the pdf page
		link = href.split(',')[0].split('(')[-1].strip("'")
		yield [tender_number, end_date, link]

def create_upperlevel_folder():
	# create upper level folder
	todays_date = datetime.date.today().strftime('%d-%m-%Y')
	upperlevel_folder_name = f'Upload Date {todays_date}'
	os.makedirs(upperlevel_folder_name, exist_ok=True)
	sub_directory = os.path.join(upperlevel_folder_name, f"Keyword = {search_criteria}")
	os.makedirs(sub_directory, exist_ok=True)
	return sub_directory

def sub_level_folder(upperlevel_folder_name, refined_list):
	# create a sub-folders
	tender_number = refined_list[0].replace('-', '')
	due_date = refined_list[1].replace('/', '.')
	folder_path = os.path.join(upperlevel_folder_name, f"{tender_number}_{due_date}")
	os.makedirs(folder_path, exist_ok=True)
	return folder_path

# if datetime.date.today().strftime('%d') != '27':
search_criterion = ['Bearing', 'Bush', 'NTN']
# opts = webdriver.ChromeOptions()
# chrome_prefs = {}
# opts.experimental_options["prefs"] = chrome_prefs
# chrome_prefs["profile.default_content_settings"] = {"images" : 2}
# chrome_prefs["profile.managed_default_content_settings"] = {"images" : 2}
driver = webdriver.Chrome('CDN/Chromedriver.exe')
driver.implicitly_wait(30)

for search_criteria in search_criterion:
	initials(search_criteria)
	refined_lists = list(fetch_window_links())
	refined_lists = fetch_window_links()
	upperlevel_folder_name = create_upperlevel_folder()
	for refined_list in refined_lists:
		links = return_pdf_link(f'https://ireps.gov.in{refined_list[-1]}')
		path = sub_level_folder(upperlevel_folder_name, refined_list)
		for link in links:
			print('#', link, '-', path)
			download_pdf(link, path)

driver.quit()
