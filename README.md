# Happyproject

Happyproject (HappyFinder) is a responsive web app that finds happy hours by day, time, and location. Happyproject makes  
extensive use of the Foursquare API, and was built using Flask / Python, Postgres, and JS.

Additionally, Happyproject contains a separate scraper engine that mines Foursquare for data snippets that we can then construct
into additional happy hour information for each venue. It's important to understand that Foursquare doesn't actually have the needed 
data in the correct, parsable format, which is why the scraper was needed.

## Installation

Requirements:
 datetime  
 json  
 StringIO  
 urllib  
 pycurl  
 bcrypt  
 pg  
 os  
 sys  
 Flask  
 requests  
 
## Usage

Users can make requests in one of two ways:  
- Using Current location  
- Using address search  

Additional search options:  
- Radius to search in  
- Active vs anytime: determines whether to return results based on the current time or any results for which there are any  
happy hours.

Hitting the submit button on nav search will automatically use user's current location if no address is entered.

## Challenges

1.) Working with the Maps API  
  Not being familiar with the Maps API or JS, we had some initial trouble drawing the map, customizing the markers, setting  
  appropriate zoom levels, and drawing all the venue markers on screen. Zoom levels are not based on a radial distance, 
  so the bounds must be extended for each marker until all markers are covered in map view.

2.) Using SSL  
  Maps doesn't allow geolocation without a secure connection, so we had to get a certificate nad set up SSL for our AWS instance.
  This also required some configuration on Google Domains, as well as in the WSGI file and the Apache .conf virtualhost settings.  
  
3.) Data scraping and parsing
  We considered several approaches for populating our data, and this portion of the project took considerable time. Our first
  approach was to webscrape restaurant URLs acquired through Places via Scrapy. Due to the difficulty of parsing website data
  into a rigid format that would allow filtering by days and times, we decided on a middle-ground approach - we scraped Foursquare
  menu data for mentions of 'happy hours' and then extracted the corresponding string to a separate file along with the FS ID.
  This string data can be manually parsed in the meantime, and over the long run it should be possible to create a parser that works
  on at least 80% of the data.
  Cody implemented a grid search on top of the base scraper, so we were able to put in geo coordinates for a city's bounds and
  get all of the data for that city in one neat package.
  
4.) Mixing API data with local data in our db
  Foursquare terms of service disallows storage of Foursquare's data locally. This fact, combined with our desire to always give
  users up-to-date information, meant that we wanted to keep as little data as possible. In our models, we decided to store 
  the Foursquare venue ID and location coordinates, but nothing else. This allows us to perform a local search in our db
  to find matching locations, then query the FS API to get all the details for those locations. We then marry this with the 
  happy hour information that we're storing locally to produce a complete venue Object.
  
5.) Subdomain routing
  We're running this app on Cdy's AWS instance, which also contains a second app. To make everything work as intended, we had
  to set up virtualhost aliases for Apache, as well as set some config variables for Flask to ensure that the root was set to the
  happyproject's subdomain. This required a lot of link debugging

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Screenshots


## Credits

Main contributors:
@markgreenburg & @ctaylor4874  
Mark: Models, classes, and user auth. Basic scraper code, Details page layout.  
Cody: Front end, JS & Maps, most routing  
Damian: SSL setup, server setup debugging  

## License
¯\_(ツ)_/¯

TODO: Write license
