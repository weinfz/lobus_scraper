from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, ElementNotVisibleException
import urllib
import urlparse
import pandas as pd
import os

class LobusScraper(object):
    def __init__(self):
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        file_path = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(file_path,'..','chromedriver')
        self.driver = webdriver.Chrome(executable_path=exe_path, options=chrome_options)
        
    def close_signup(self):
        """ method to close the signup the pops up
        should just create sign up if use for production
        """
        close = self.driver.find_element_by_id('close_signup')
        close.click()
        
    def accept_cookies(self):
        """ method to accept cookies
        """
        self.driver.implicitly_wait(10)
        accept = WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, 'optanon-allow-all')))
        self.driver.execute_script("(arguments[0]).click();", accept)

    def get_lot_urls(self, url):
        """ method to retireve lot urls from an auction url
        """
        self.driver.get(url)
        try:
            load_all = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'loadAllUpcomingPast')))
            load_all.click()
            loader = WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.ID, 'loader-inner')))
            self.driver.implicitly_wait(10)
            loader = WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.ID, 'loader-inner')))
        except ElementNotVisibleException:
            # sign up pop up probably came up
            # may want to just create sign in if prod
            # also recursion may create loop if url is bad
            self.close_signup()
            urls = self.get_lot_urls(url)
            return urls
        except NoSuchElementException:
            # must be no load all button they may all be showing
            # just continue
            pass
        except WebDriverException:
            ## accept cookies came up
            self.accept_cookies()
            urls = self.get_lot_urls(url)
            return urls
        lot_elems = self.driver.find_elements_by_xpath('//*[@id="ResultContainer"]//a[@href]')
        urls = []
        for elem in lot_elems:
            urls.append(elem.get_attribute("href"))
        self.urls = urls
        return urls
    
    def parse_lot_url(self, url):
        """ method that parses a lot url and gets relevent data
        """
        ## list of the needed tags and their id on the page
        needed_tags = [{'name':'lot','locator':'main_center_0_lblLotNumber'},
               {'name':'artist_years','locator':'main_center_0_lblLotPrimaryTitle'},
               {'name':'title','locator':'main_center_0_lblLotSecondaryTitle'},
               {'name':'sold_price','locator':'main_center_0_lblPriceRealizedPrimary'},
               {'name':'estimation','locator':'main_center_0_lblPriceEstimatedPrimary'},
               {'name':'description','locator':'main_center_0_lblLotDescription'},
               {'name':'provenance','locator':'main_center_0_lblLotProvenance'}
               ]
        self.driver.get(url)
        # record url to see which are bad
        row = {'url':url}
        for tag in needed_tags:
            print(tag)
            try:
                element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, tag['locator'])))
                row[tag['name']] = element.text
            except TimeoutException:
                ## elemnet never loaded record none so we can check later
                row[tag['name']] = None

        try:
            image = self.driver.find_element_by_class_name('image')
            src = image.get_attribute('src')  
            ## save file to local if prod should should cloud storage
            filename = urlparse.urlparse(src).path.split('/')[-1]
            file_path = os.path.dirname(os.path.abspath(__file__))
            save_path = os.path.join(file_path,'..','images',filename)
            urllib.urlretrieve(src, save_path)
            # image meta data 
            row['image_url'] = src
            row['image_filename'] = filename
        except NoSuchElementException:
            ## no image probably some wrong with url
            row['image_url'] = None
            row['image_filename'] = None
        return row
    
    def parse_lot_urls(self, urls=None):
        """ method to parse all lot urls from an auction
        """
        if urls == None:
            urls = self.urls
        data = []    
        for url in urls:
            try:
                print(url)
                row = self.parse_lot_url(url)
            except ElementNotVisibleException:
                ## signup page came up
                self.close_signup()
                row = self.parse_lot_url(url)
            data.append(row)
        return data

    def scrape_auction_url(self, url):
        urls = self.get_lot_urls(url)
        data = self.parse_lot_urls(urls)
        return data
    
def save_raw_auction_data(url):
    scraper = LobusScraper()
    data = scraper.scrape_auction_url(url)
    df = pd.DataFrame(data)
    filename = urlparse.urlparse(url).path.split('/')[-1].split('.')[0]
    file_path = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(file_path,'..','data',filename+'.csv')
    df.to_csv(save_path, encoding='utf-8')
    
    
    
    
if __name__ == "__main__":
    urls = [
            "https://www.christies.com/impressionist-and-modern-art-27255.aspx?lid=1&dt=100420180204&saletitle=",
            "https://www.christies.com/impressionist-and-modern-art-27400.aspx?lid=1&dt=100420180206&saletitle=",
            ]
    for url in urls:
        save_raw_auction_data(url)
    
    
    
    