# lobus_scraper
first create a data and an images folder in the main directory
uses python 2.7
to set up need to install latest version of chrome

to run scraper 
python lobus_scraper

to run query
python lobus_scraper -tol={your_tolerance} --debug=True

this scraper uses selenium and python 2.7 to scrape the data, which is saved in a raw format, this is to limit errors when small changes on the webpage are made so you dont needto rescraper the page. If this was in production i would have made a variable to distiguish between the different types art so the dimensions make more sense. It seems kind of silly to say any scupture and painting are similar based on dimension. python and selenium were chosen over havascript because the data processing libraies are better. the code save the image file and paths to the image filesin a csv. with all the other raw data about the art each auction in its own csv. If prod this would have used cloud storage and a sql database that would contain more processed data. 

Forthe grouping i simply grouped the objects in groups by starting with in the smallest dimension 1 (called dimension 1 becuase differences betwwen paintings and sculpture make the dimension different) and dimension 2 and going up from there making sure to group all the objects. I the future in would make sense to standardize groups so that comparing groups between artist  
would be more meaningful

