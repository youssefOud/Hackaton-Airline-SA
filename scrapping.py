
import requests
from bs4 import BeautifulSoup
import re
import math
import numpy as np


def get_airlines_sub_url():
    """
    Returns the list of all airlines companies sub-URL like :
    '/airline-reviews/ab-aviation'

    This sub-URL will later be concatenated with the main URL to access the
    airline page.

    Parameters
    ----------
    None

    Returns
    -------
    The list of all sub-URL of all companies
    """

    URL = 'https://www.airlinequality.com/review-pages/a-z-airline-reviews/'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    tabs_content = soup.find('div', class_="tabs-content")
    airlines_tag = tabs_content.find_all('li')

    #  Collect the different URLs for each airline company
    airlines_ref = []
    for element in airlines_tag:
        tag = element.find('a')
        airlines_ref.append(tag['href'])

    return airlines_ref


def get_url_airline(airlines):
    """
    Produces the list of URLs corresponding to the pages containing reviews
    of one or many airlines.

    Parameters
    ----------
    airlines (string): the airlines reference needed,
    ex : '/airline-reviews/ab-aviation'

    Returns
    -------
    A list of dictionaries of the form : {'airline':[], 'seats':[]} where
    airline and seats are two page categories containing different review
    types.
    The first element corresponds to the URLs of the airline category and the
    second corresponds to the seats category.
    """

    URL = 'https://www.airlinequality.com'

    url_company = {'airline': [], 'seats': []}
    #  Concatenate base URL + specific URL of each company
    url = URL + airlines
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    #  Test if tabs 'seat' and 'airline' exist
    seat_content = soup.find('li', class_=["tab-title seat",
                                           "tab-title seat active"])
    airline_content = soup.find('li',
                                class_=["tab-title airline",
                                        "tab-title airline active"])

    #  If there is a tab 'airline' --> create its related URLs
    if airline_content is not None:
        ref_airline = airline_content.find('a')['href']
        new_url = URL + ref_airline + \
            '/?sortby=post_date%3ADesc&pagesize=100'
        new_page = requests.get(new_url)
        new_soup = BeautifulSoup(new_page.content, 'html.parser')

        test_page = new_soup.find(
            'article',
            class_="comp comp_reviews-pagination\
                querylist-pagination position-")

        airline_url = []
        if test_page is not None:
            query_page = new_soup.find('div',
                                       class_='pagination-total').get_text()

            if query_page is not None:
                number_review = int(query_page.split(" ")[-2])
                number_page = math.ceil(number_review / 100)

                for i in range(number_page):
                    url = URL + ref_airline + '/page/' + \
                        str(i + 1) + '/?sortby=post_date%3ADesc&pagesize=100'
                    if url not in airline_url:
                        airline_url.append(url)

        else:
            #  Only one page
            airline_url.append(new_url)

        url_company['airline'] = airline_url

    #  If there is a tab 'seats' --> create its related URLs
    if seat_content is not None:
        ref_seat = seat_content.find('a')['href']
        new_url = URL + ref_seat + '/?sortby=post_date%3ADesc&pagesize=100'
        new_page = requests.get(new_url)
        new_soup = BeautifulSoup(new_page.content, 'html.parser')

        test_page = new_soup.find(
            'article',
            class_="comp comp_reviews-pagination\
                querylist-pagination position-")

        seat_url = []
        if test_page is not None:
            query_page = new_soup.find('div',
                                       class_='pagination-total').get_text()

            if query_page is not None:
                number_review = int(query_page.split(" ")[-2])
                number_page = math.ceil(number_review / 100)

                for i in range(number_page):
                    url = URL + ref_seat + '/page/' + \
                        str(i + 1) + '/?sortby=post_date%3ADesc&pagesize=100'
                    if url not in seat_url:
                        seat_url.append(url)

        else:

            #  only one page
            seat_url.append(new_url)

        url_company['seats'] = seat_url

    return url_company


def generate_page_reviews(URL):
    """
    Returns the informations from the URL webpage input (review, rating ...).

    Parameters
    ----------
    URL (string): the URL of the webpage we want the reviews from

    Returns
    -------
    An array containing  all information we need from each review (ex: date,
    comment, Title, rating, recommendation...)

    """

    # Get page content
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get the list of reviews in the page
    reviews = soup.find_all('article', itemprop='review')

    # Content lists (one list for each review element)
    dates_published = []
    global_ratings = []
    reviews_titles = []
    customers_countries = []
    reviews_body = []
    is_verified = []
    aircraft = []
    type_traveller = []
    seat_type = []
    route_provenance = []
    route_destination = []
    date_flown = []
    is_recommended = []
    seat_comfort = []
    cabin_staff_service = []
    food_beverages = []
    sleep_comfort = []
    sitting_comfort = []
    seat_width = []
    seat_length = []
    seat_privacy = []
    power_supply = []
    seat_storage = []

    #  List of months (for checking purposes)
    months = ["January", "Fabruary", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]

    for i, review in enumerate(reviews):
        #  Get date published
        dates_published.append(
            review.find(
                'meta',
                itemprop='datePublished')['content'])

        #  Get global rating value
        if review.find('span', itemprop='ratingValue') is not None:
            global_ratings.append(review.find('span',
                                              itemprop='ratingValue').text)

        #  Get review title
        if review.find('h2', class_='text_header') is not None:
            reviews_titles.append(review.find('h2', class_='text_header')
                                  .text.strip().replace('\"', '')
                                  .replace('\n', ' ')
                                  .replace('\r', '')
                                  .replace(';', ','))

        #  Get customer country
        temp = review.find('h3', class_='text_sub_header userStatusWrapper') \
            .text \
            .replace(';', ',')
        country = re.search(r'\((.*)\)', temp)
        if country is not None:
            customers_countries.append(country.group(1))

        #  Get review content
        if (review.find('div', class_='text_content')
                .find('em') is not None):
            if ('erified' in review.find('div', class_='text_content')
                    .find('em').text[:20]):
                is_verified.append(True)
            else:
                is_verified.append(False)

            review_body = review.find('div', class_='text_content') \
                .text.split('|', 1)[-1].strip()
            review_body = review_body.replace('\n', ' ') \
                .replace('\r', '') \
                .replace(';', ',')

        else:
            is_verified.append(False)

            review_body = review.find('div', class_='text_content') \
                .text.split('|', 1)[-1].strip()

            review_body = review_body.replace('\n', ' ') \
                .replace('\r', '') \
                .replace(';', ',')

        reviews_body.append(review_body)

        #  Retrieve the various rating of the review
        review_ratings = review.find_all('tr')

        #  For each rating type, check if it is present in the review
        for rating in review_ratings:
            # Aircraft
            if rating.find('td',
                           class_='review-rating-header aircraft') is not None:

                aircraft.append(rating.find('td',
                                            class_='review-value')
                                .text.replace(';', ','))

            #  Traveller type
            if rating.find('td',
               class_='review-rating-header type_of_traveller') is not None:

                type_traveller.append(rating.find('td',
                                                  class_='review-value').text)

            #  Seat type
            if rating.find(
                'td',
                    class_='review-rating-header cabin_flown') is not None:

                seat_type.append(rating.find('td', class_='review-value').text)

            #  Route
            if rating.find(
                'td',
                class_='review-rating-header route') is not None and (
                ' to ' in rating.find(
                    'td',
                    class_='review-value').text):

                routeTemp = rating.find('td', class_='review-value') \
                    .text \
                    .replace(';', ',') \
                    .split(' to ', 1) \

                route_provenance.append(routeTemp[0])
                route_destination.append(routeTemp[1])

            # Date flown
            if rating.find('td', class_='review-rating-header date_flown') \
                is not None \
                and sum([rating.find('td', class_='review-value').text
                         .find(month) for month in months]) != -12:
                date_flown.append(rating.find('td', class_='review-value')
                                  .text.replace(';', ','))

            #  Seat comfort
            if rating.find(
                'td',
                    class_='review-rating-header seat_comfort') is not None:

                star_fill = rating.find_all('span', class_="star fill")
                seat_comfort.append(len(star_fill))

            #  Cabin staff service
            if rating.find('td',
               class_='review-rating-header cabin_staff_service') \
               is not None:

                star_fill = rating.find_all('span', class_="star fill")
                cabin_staff_service.append(len(star_fill))

            #  Food and beverages
            if rating.find('td',
               class_='review-rating-header food_and_beverages') \
               is not None:

                star_fill = rating.find_all('span', class_="star fill")
                food_beverages.append(len(star_fill))

            #  sleep comfort
            if rating.find(
                'td',
                    class_='review-rating-header seat_comfort') is not None:

                star_fill = rating.find_all('span', class_="star fill")
                sleep_comfort.append(len(star_fill))

            #  sitting_comfort
            if rating.find('td',
               class_='review-rating-header cabin_staff_service') \
               is not None:

                star_fill = rating.find_all('span', class_="star fill")
                sitting_comfort.append(len(star_fill))

            #  seat_width
            if rating.find('td',
               class_='review-rating-header food_and_beverages') \
               is not None:

                star_fill = rating.find_all('span', class_="star fill")
                seat_width.append(len(star_fill))

            #  seat_length
            if rating.find('td',
               class_='review-rating-header cabin_staff_service') \
               is not None:

                star_fill = rating.find_all('span', class_="star fill")
                seat_length.append(len(star_fill))

            #  seat_privacy
            if rating.find('td',
               class_='review-rating-header food_and_beverages') \
               is not None:

                star_fill = rating.find_all('span', class_="star fill")
                seat_privacy.append(len(star_fill))

            #  power_supply
            if rating.find('td',
               class_='review-rating-header cabin_staff_service') \
               is not None:

                star_fill = rating.find_all('span', class_="star fill")
                power_supply.append(len(star_fill))

            #  seat_storage
            if rating.find('td',
               class_='review-rating-header food_and_beverages') \
               is not None:

                star_fill = rating.find_all('span', class_="star fill")
                seat_storage.append(len(star_fill))

            #  Is recommended
            if rating.find(
                'td',
                    class_='review-rating-header recommended') is not None:

                temp = rating.find_all('td')[1].text
                if temp == "yes":
                    is_recommended.append(True)
                else:
                    is_recommended.append(False)

        # For each missing element of the review, add a 'None' value
        if len(dates_published) != i + 1:
            dates_published.append(None)
        if len(global_ratings) != i + 1:
            global_ratings.append(None)
        if len(reviews_titles) != i + 1:
            reviews_titles.append(None)
        if len(customers_countries) != i + 1:
            customers_countries.append(None)
        if len(reviews_body) != i + 1:
            reviews_body.append("")
        if len(is_verified) != i + 1:
            is_verified.append(None)
        if len(aircraft) != i + 1:
            aircraft.append(None)
        if len(type_traveller) != i + 1:
            type_traveller.append(None)
        if len(seat_type) != i + 1:
            seat_type.append(None)
        if len(route_provenance) != i + 1:
            route_provenance.append(None)
        if len(route_destination) != i + 1:
            route_destination.append(None)
        if len(date_flown) != i + 1:
            date_flown.append(None)
        if len(is_recommended) != i + 1:
            is_recommended.append(None)
        if len(seat_comfort) != i + 1:
            seat_comfort.append(None)
        if len(cabin_staff_service) != i + 1:
            cabin_staff_service.append(None)
        if len(food_beverages) != i + 1:
            food_beverages.append(None)
        if len(sleep_comfort) != i + 1:
            sleep_comfort.append(None)
        if len(sitting_comfort) != i + 1:
            sitting_comfort.append(None)
        if len(seat_width) != i + 1:
            seat_width.append(None)
        if len(seat_length) != i + 1:
            seat_length.append(None)
        if len(seat_privacy) != i + 1:
            seat_privacy.append(None)
        if len(power_supply) != i + 1:
            power_supply.append(None)
        if len(seat_storage) != i + 1:
            seat_storage.append(None)

    return np.array([dates_published,
                     global_ratings,
                     reviews_titles,
                     customers_countries,
                     reviews_body,
                     is_verified,
                     aircraft,
                     type_traveller,
                     seat_type,
                     route_provenance,
                     route_destination,
                     date_flown,
                     seat_comfort,
                     food_beverages,
                     cabin_staff_service,
                     sleep_comfort,
                     sitting_comfort,
                     seat_width,
                     seat_length,
                     seat_privacy,
                     power_supply,
                     seat_storage,
                     is_recommended]).transpose()


def generate_dataset(airlines):
    """
    Returns all information needed from reviews of all airlines companies
    specified as input of the function

    Parameters
    ----------
    airlines (List[string]): the airlines reference needed,
    ex : '/airline-reviews/ab-aviation'

    Returns
    -------
    ndarray that contains all information needed from reviews of all airline
    companies 14 features (ex: date, comment, Title, rating, recommendation...)

    """

    airline_data = None
    #  For each airline
    for i, airline_url in enumerate(airlines):
        airlines_urls = get_url_airline(airline_url)

        #  For each URL corresponding to the tab 'airline'
        for url_in_airline in airlines_urls['airline']:
            page_data = generate_page_reviews(url_in_airline)

            # Add column specifying that the review is from the airline
            # category
            is_airline_review = np.ones((len(page_data), 1), dtype=np.int8)

            #  Add column for airline company name
            airline_name = np.repeat(
                [airlines[i].split('/')[-1]], len(page_data)) \
                .reshape((len(page_data), 1))

            #  Concatenate reviews data + review category + airline name
            page_data = np.concatenate(
                (page_data, is_airline_review, airline_name), axis=1)

            # Either create a new numpy array for the first pass...
            if airline_data is None:
                airline_data = page_data
            #  ...or concatenate the new data with the existing array
            else:
                airline_data = np.concatenate((airline_data, page_data))

        #  For each URL corresponding to the tab 'seats'
        for url_in_airline in airlines_urls['seats']:
            page_data = generate_page_reviews(url_in_airline)
            is_airline_review = np.zeros((len(page_data), 1), dtype=np.int8)

            #  Add column for airline company name
            airline_name = np.repeat(
                [airlines[i].split('/')[-1]], len(page_data)) \
                .reshape((len(page_data), 1))

            #  Concatenate reviews data + review category + airline name
            page_data = np.concatenate(
                (page_data, is_airline_review, airline_name), axis=1)

            # Either create a new numpy array for the first pass...
            if airline_data is None:
                airline_data = page_data
            #  ...or concatenate the new data with the existing array
            else:
                airline_data = np.concatenate((airline_data, page_data))

    return airline_data

#  Get URLs then generate the data
sub_urls = get_airlines_sub_url()
data = generate_dataset(sub_urls)

#  Add a unique id for each review
ids = np.arange(len(data)).reshape((len(data), 1))
data = np.concatenate((ids, data), axis=1)

#  Save the data to a CSV file
np.savetxt(
    './airlines_dataset_exhaustive.csv',
    data,
    fmt='%s',
    encoding='utf-8',
    comments='',
    header="review_ID;date_published;global_ratings;reviews_titles;customers_countries;reviews_body;is_verified;aircraft;type_traveller;seat_type;route_provenance;route_destination;date_flown;seat_comfort;food_beverages;cabin_staff_service;sleep_comfort;sitting_comfort;seat_width;seat_length;seat_privac;power_supply;seat_storage;is_recommended;is_airline_review;airline_name",
    delimiter=";")
