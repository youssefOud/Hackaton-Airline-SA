
import requests
from bs4 import BeautifulSoup
from math import *
import re
import numpy as np

def get_airlines_sub_url():
    
    """
    Returns the list of all airlines companies sub-URL like : '/airline-reviews/ab-aviation'

    Parameters
    ----------
    None

    Returns
    -------
    A list of all sub-url of each companies    
    """    
    
    URL = 'https://www.airlinequality.com/review-pages/a-z-airline-reviews/'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    tabs_content = soup.find('div', class_="tabs-content")
    airlines_tag = tabs_content.find_all('li')
    
    #collect the different urls for each airline company
    airlines_ref=[]
    for element in airlines_tag :
        tag = element.find('a')
        airlines_ref.append(tag['href'])
    
    return airlines_ref

def get_url_airline(airlines):
    
    """
    Returns the sum of two decimal numbers in binary digits.

    Parameters
    ----------
    airlines (string): the airlines reference needed, ex : '/airline-reviews/ab-aviation'

    Returns
    -------
    A list of all url reviews linked to the companies needed   
    """
    
    URL = 'https://www.airlinequality.com'
    
    total_url=[]
    url_company ={'airline':[], 'seats':[]} 
    url = URL + airlines
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    #Test if onglet seat and airline
    seat_content = soup.find('li', class_=["tab-title seat","tab-title seat active"])
    airline_content = soup.find('li',
                                class_=["tab-title airline","tab-title airline active"])
    
    #If there is an onglet airline
    if not(airline_content == None):
        ref_airline = airline_content.find('a')['href']
        new_url = URL + ref_airline + '/?sortby=post_date%3ADesc&pagesize=100'
        new_page = requests.get(new_url)
        new_soup = BeautifulSoup(new_page.content, 'html.parser')

        test_page=new_soup.find(
                'article',
            class_="comp comp_reviews-pagination querylist-pagination position-")

        airline_url = []
        if not(test_page == None):
            query_page = new_soup.find('div', class_='pagination-total').get_text()

            if not(query_page ==None):
                number_review = int(query_page.split(" ")[-2])
                number_page = ceil(number_review/100)

                for i in range(number_page) :
                    url = URL + ref_airline + '/page/'+ str(i+1) + '/?sortby=post_date%3ADesc&pagesize=100'
                    if url not in airline_url:
                        airline_url.append(url)

        else : airline_url.append(new_url) #only one page

        url_company['airline']=airline_url
    
    #If there is an onglet seats
    if not(seat_content == None):
        ref_seat = seat_content.find('a')['href']
        new_url = URL + ref_seat + '/?sortby=post_date%3ADesc&pagesize=100'
        new_page = requests.get(new_url)
        #time.sleep(1)
        new_soup = BeautifulSoup(new_page.content, 'html.parser')

        test_page=new_soup.find(
            'article',
            class_="comp comp_reviews-pagination querylist-pagination position-")

        seat_url = []
        if not(test_page == None):
            query_page = new_soup.find('div', class_='pagination-total').get_text()

            if not(query_page ==None):
                number_review = int(query_page.split(" ")[-2])
                number_page = ceil(number_review/100)

                for i in range(number_page) :
                    url = URL + ref_seat + '/page/'+ str(i+1) + '/?sortby=post_date%3ADesc&pagesize=100'
                    if url not in seat_url:
                        seat_url.append(url)

        else : seat_url.append(new_url) # only one page

        url_company['seats']=seat_url

        
    return url_company



def generate_page_reviews(URL):
    
    """
    Returns the informations from the url webpage input (review, rating ...).

    Parameters
    ----------
    url (string): the url of the webpage we want the information

    Returns
    -------
    A list of all information we need from each review (ex: date, comment, Title, 
    rating, recommendation...)    
    """
    
    # Get page content
    page = requests.get(URL)
    # Wait for 5 seconds
    #time.sleep(1)
    soup = BeautifulSoup(page.content, 'html.parser')
    # Get the list of reviews in the page
    reviews = soup.find_all('article', itemprop='review')
    
    regex = re.compile(r'[\n\r\t]')
    
    dates_published = [] # Get list of publication dates
    global_ratings = [] # Get list of global ratings
    reviews_titles = [] # Get reviews' titles
    customers_countries = [] # Get country of customers
    reviews_body = [] # Get reviews' bodies
    is_verified = [] # Get boolean variable verified
    aircraft = []
    type_traveller = []
    seat_type = []
    route = []
    date_flown = []
    is_recommended = []
    for i, review in enumerate(reviews):
        dates_published.append(review.find('meta', itemprop='datePublished')['content'])
        
        if review.find('span', itemprop='ratingValue') is not None :
            global_ratings.append(review.find('span', itemprop='ratingValue').text)
        
        if review.find('h2', class_='text_header') is not None:
            reviews_titles.append(review.find('h2', class_='text_header').text.strip())
                              
        temp = review.find('h3', class_='text_sub_header userStatusWrapper').text
        country = re.search('\((.*)\)', temp)
        if country is not None:
            customers_countries.append(country.group(1))
        
        if (review.find('div', class_='text_content').find('em') is not None) and (review.find('div', class_='text_content').find('em') == 'Trip Verified'):
            is_verified.append(True)
           
            review_body = review.find('div', class_='text_content').text.split("|",1)[1][2:] 
            review_body = regex.sub("", review_body)
            #review_body = '"' + review_body + '"'
            review_body = review_body.replace(';',',')
                        
        else:
            is_verified.append(False)
            review_body = review.find('div', class_='text_content').text
            review_body = regex.sub("", review_body)
            #review_body = '"' + review_body + '"'
            review_body = review_body.replace(';',',')
            
        reviews_body.append(review_body)
            
        review_ratings = review.find_all('tr')
        for rating in review_ratings:
            # Aircraft
            if rating.find('td', class_='review-rating-header aircraft') is not None:
                aircraft.append(rating.find('td', class_='review-value').text)
            # Traveller type
            if rating.find('td', class_='review-rating-header type_of_traveller') is not None:
                type_traveller.append(rating.find('td', class_='review-value').text)
            # Seat type
            if rating.find('td', class_='review-rating-header cabin_flown') is not None:
                seat_type.append(rating.find('td', class_='review-value').text)
            # Route
            if rating.find('td', class_='review-rating-header route') is not None:
                route.append(rating.find('td', class_='review-value').text)
            # Date flown
            if rating.find('td', class_='review-rating-header date_flown') is not None\
            and len(rating.find('td', class_='review-value').text) == 10:
                date_flown.append(rating.find('td', class_='review-value').text)
            '''# Seat comfort
            if rating.find('td', class_='review-rating-header seat_comfort') is not None:
                seat_comfort.append(rating.find('td', class_='review-value').text)
            # Cabin staff service
            if rating.find('td', class_='review-rating-header cabin_staff_service') is not None:
                cabin_staff_service.append(rating.find('td', class_='review-value').text)
            # Food and beverages
            if rating.find('td', class_='review-rating-header food_and_beverages') is not None:
                food_beverages.append(rating.find('td', class_='review-value').text)'''
            # Is recommended
            if rating.find('td', class_='review-rating-header recommended') is not None:
                temp = rating.find_all('td')[1].text
                if temp == "yes": 
                    is_recommended.append(True)
                else: 
                    is_recommended.append(False)

        if len(dates_published) != i+1: dates_published.append(None)
        if len(global_ratings) != i+1: global_ratings.append(None)
        if len(reviews_titles) != i+1: reviews_titles.append(None)
        if len(customers_countries) != i+1: customers_countries.append(None)
        if len(reviews_body) != i+1: reviews_body.append("")
        if len(is_verified) != i+1: is_verified.append(None)
        if len(aircraft) != i+1: aircraft.append(None)
        if len(type_traveller) != i+1: type_traveller.append(None)
        if len(seat_type) != i+1: seat_type.append(None)
        if len(route) != i+1: route.append(None)
        if len(date_flown) != i+1: date_flown.append(None)
        if len(is_recommended) != i+1: is_recommended.append(None)
            
    return np.array([dates_published,
                    global_ratings,
                    reviews_titles,
                    customers_countries,
                    reviews_body,
                    is_verified,
                    aircraft,
                    type_traveller,
                    seat_type,
                    route,
                    date_flown,
                    is_recommended]).transpose()

def generate_dataset(airlines):
    
    """
    Returns all information needed from reviews of all airlines companies.

    Parameters
    ----------
    airlines (string): the airlines reference needed, ex : '/airline-reviews/ab-aviation'

    Returns
    -------
    ndarray that contains all information needed from reviews of all airlines companies
    14 features (ex: date, comment, Title, rating, recommendation...)    
    """
    
    airline_data = None
    for i, airline_url in enumerate(airlines):
        airlines_urls = get_url_airline(airline_url)
        
        for url_in_airline in airlines_urls['airline']:
            page_data = generate_page_reviews(url_in_airline)
            is_airline_review = np.ones((len(page_data),1), dtype=np.int8) # Column is_airline_comment
            airline_name = np.repeat([airlines[i].split('/')[-1]], len(page_data)).reshape((len(page_data),1))
            page_data = np.concatenate((page_data, is_airline_review, airline_name), axis=1)
            if airline_data is None:
                airline_data = page_data
            else:
                airline_data = np.concatenate((airline_data, page_data))
        print('number of airline review',len(airlines_urls['airline']))
            
        for url_in_airline in airlines_urls['seats']:
            page_data = generate_page_reviews(url_in_airline)
            is_airline_review = np.zeros((len(page_data),1), dtype=np.int8) # Column is_airline_comment
            airline_name = np.repeat([airlines[i].split('/')[-1]], len(page_data)).reshape((len(page_data),1))
            page_data = np.concatenate((page_data, is_airline_review, airline_name), axis=1)
            if airline_data is None:
                airline_data = page_data
            else:
                airline_data = np.concatenate((airline_data, page_data))
        print('number of seats review',len(airlines_urls['seats']))
        print('airlines number',i)
        print('\n')
    return airline_data

