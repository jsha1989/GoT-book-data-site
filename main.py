import requests
import requests_cache
from flask import Flask, render_template
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

app = Flask(__name__)
requests_cache.install_cache(cache_name='got_cache', backend='sqlite', expire_after=timedelta(days=7))
URL = "https://www.anapioficeandfire.com/api"


# function to extract character/house/book name from api response
def get_name_from_api(url):
    response = requests.get(url)
    data = response.json()
    return data["name"]


@app.route("/")
def home():
    return render_template("home.html")


# display book info
@app.route("/book/<book_id>")
def get_book(book_id):
    response = requests.get(URL + f"/books/{book_id}")
    data = response.json()
    title = data["name"]
    pages = data["numberOfPages"]
    # reformat date
    release = data["released"].split("T")
    release_date = release[0]
    format = '%Y-%m-%d'
    release_obj = datetime.strptime(release_date, format)
    release_str = release_obj.strftime('%d %B, %Y')
    # get list of POV chars
    pov_chars = data["povCharacters"]
    pov_chars_list = []
    for char in pov_chars:
        char_response = requests.get(char)
        char_data = char_response.json()
        char_name = char_data["name"]
        pov_chars_list.append(char_name)
    return render_template("book.html", title=title, pages=pages, release=release_str, pov_chars=pov_chars_list,
                           book_id=book_id)

# display house info
@app.route("/house/<house_id>")
def get_house(house_id):
    response = requests.get(URL + f"/houses/{house_id}")
    data = response.json()
    house_name = data["name"]
    house_region = data["region"]
    house_words = data["words"]
    house_titles = data["titles"]
    house_seats = data["seats"]
    house_weapons = data["ancestralWeapons"]
    # get list of members
    house_members = data["swornMembers"]
    house_members_list = []
    for member in house_members:
        member_response = requests.get(member)
        member_data = member_response.json()
        member_name = member_data["name"]
        house_members_list.append(member_name)
    return render_template("house.html", house_name=house_name, house_region=house_region,
                           house_words=house_words, house_titles=house_titles, house_seats=house_seats,
                           house_weapons=house_weapons, house_members=house_members_list, house_id=house_id)


#display character info
@app.route("/character/<char>")
def get_char(char):
    response = requests.get(URL + f"/characters?name={char}")
    data = response.json()
    char_name = data[0]["name"]
    char_gender = data[0]["gender"]
    char_culture = data[0]["culture"]
    char_born = data[0]["born"]
    char_died = data[0]["died"]
    char_titles = data[0]["titles"]
    char_aliases = data[0]["aliases"]
    # get spouse name
    char_spouse = data[0]["spouse"]
    if char_spouse != "":
        char_spouse = get_name_from_api(char_spouse)
    # get allegiance
    char_allegiance = data[0]["allegiances"]
    char_allegiance_list = []
    for allegiance in char_allegiance:
        char_allegiance_name = get_name_from_api(allegiance)
        char_allegiance_list.append(char_allegiance_name)
    # get books
    char_books = data[0]["books"]
    char_pov_books = data[0]["povBooks"]
    char_books_list = []
    for book in char_books:
        book_name = get_name_from_api(book)
        char_books_list.append(book_name)
    for book in char_pov_books:
        book_name = get_name_from_api(book)
        char_books_list.append(book_name + " (POV character)")
    char_actor = data[0]["playedBy"]
    # get google image of character
    url = 'https://www.google.com/search?q={0}&tbm=isch'.format(char_name + "game of thrones")
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')
    images = soup.findAll('img')
    image = images[1]
    image_url = image["src"]
    return render_template("character.html", char_name=char_name, char_gender=char_gender, char_culture=char_culture,
                           char_born=char_born, char_died=char_died, char_titles=char_titles, char_aliases=char_aliases,
                           char_spouse=char_spouse, char_allegiance=char_allegiance_list, char_books=char_books_list,
                           char_actor=char_actor, char_image=image_url)


if __name__ == '__main__':
    app.run(debug=True)
