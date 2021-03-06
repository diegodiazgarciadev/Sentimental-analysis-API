import markdown.extensions.fenced_code
import src.sql_tools as sql
import src.utils as ut
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from flask import Flask, request, render_template


app = Flask(__name__)

@app.route("/")
def index():
    """
    Display the documentation of our API
    """
    readme_file = open("documentation.md", "r")
    md_template = markdown.markdown(readme_file.read(), extensions=["fenced_code"])
    return md_template


@app.route("/quotes")
def quotes():
    """
    Return  all quotes from our database
    """
    quotes = sql.getallquotes()
    return quotes

@app.route("/quotesbyartist/<artist>")
def quotesbyartist(artist):
    """
    Return quotes by an artist . User must set the artist name
    :param artist: artist name
    :return: json with the quotes of this artist
    """
    quotes = sql.quotesbyartist(artist)
    return quotes

@app.route("/quotesbysex/<sex>")
def quotesbysex(sex):
    """
    Return all quotes from a specific sex. User must set the sex (M,F)
    :param sex: (M or F)
    :return: json with the quotes by Sex
    """
    quotes = sql.quotesbysex(sex)
    return quotes

@app.route("/sa/quotes")
def sentimentalanalysquotes():
    """
     Return all quotes on DB with their Sentimental analsysis
    :return: json with all quotes and its Sentimental analsysis
    """
    quotes_sn = sql.getallquotessa()
    return quotes_sn

@app.route("/sa/<quote>")
def sentimentalanalys(quote):
    """
    Return Any string wrote in english will be evaulate y return the sentimental analsys of that string. Value between [-1,1]
    :param quote: string with the quote to evaluate
    :return: Sentimental analsysis value [-1,1]
    """
    sa = ut.getsentimentalanalysis(quote)
    return {"quote":quote, "Sentimental Analysis": sa}

@app.route("/sa/quotesbysex/<sex>")
def quotesbysexsa(sex):
    """
    return all quotes by sex with their Sentimental analsysis (M, F, B = Both)
    :param sex: (M, F, B = Both)
    :return: quotes by sex with thier Sentimental analysis
    """
    quotes_sa = sql.quotesbysexsa(sex)
    return quotes_sa



@app.route('/sa/br/quotes', methods=("POST", "GET"))
def html_table_guotesna():
    """
    Return a table on the browswer with all the quotes in DB
    :return: table with all quotes
    """
    quotessa_df = sql.getallquotessa(True)
    return quotessa_df.to_html(header="true", table_id="table")

@app.route('/sa/br/quotes_chart',methods=['GET'])
def quotessa_chart():
    """
    Return a table on the browswer with all the quotes in DB and their Sentimental analsysis values
    """
    img = io.BytesIO()
    quotes_sn = sql.getallquotessa(True)
    sns.histplot(quotes_sn["sentiment"], kde=True)
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')


    return render_template("index.html",plot_url=plot_url)

@app.route('/sa/br/quotesbysex_chart',methods=['GET'])
def quotesbysexsa_chart():
    """
    Display a sns chart (histogram) with the Sentimental analsysis of all quotes

    """
    img = io.BytesIO()
    quotes_sn = sql.quotesbysexsa("B")
    df = pd.DataFrame(eval(quotes_sn))
    sns.histplot(data=df, x="sentiment", hue="sex")
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return render_template("index.html",plot_url=plot_url)


@app.route("/insertartist", methods=["POST"])
def newartist():
    """
    insert an artist by artist name:
    :return: {"artist": artist, "id": id, "msg": msg}
    """
    artist = request.form.get("artist")
    id, msg = sql.insertartist(artist)
    return {"artist": artist, "id": id, "msg": msg}

@app.route("/deleteartist", methods=["POST"])
def deleteartist():
    """
    Delete an artist by artist name
    :return:  {"artist": artist, "id": id, "msg": msg}
    """
    artist = request.form.get("artist")
    id, msg = sql.deleteartist(artist)
    return {"artist": artist, "id": id, "msg": msg}

@app.route("/updateartist", methods=["POST"])
def updateartist():
    """
    Update an artist by artist name
    :return: "artist": artist, "artist_new": artist_new, "msg": msg}
    """
    artist = request.form.get("artist")
    artist_new = request.form.get("artist_new")
    id, msg = sql.updateartist(artist,artist_new)
    return {"artist": artist, "artist_new": artist_new, "msg": msg}

@app.route("/insertmoviequote", methods=["POST"])
def newmoviequote():
    """
    Insert a quote for a movie:
    :return: movie": movie, "quote": quote, "id": id_movie, "msg": msg4}
    """
    artist = request.form.get("artist")
    character = request.form.get("character")
    quote = request.form.get("quote")
    movie = request.form.get("movie")
    year = request.form.get("year")
    sex = request.form.get("sex")
    id_artist, msg1 = sql.insertartist(artist)
    id_character, msg2 = sql.insertcharacter(character, sex, id_artist)
    id_quote, msg3 = sql.insertquote(quote, id_character)
    id_movie, msg4 = sql.insertmovie(movie, year, id_character)
    msg = msg1 +","+ msg2 +","+ msg3 +","+ msg4
    return {"movie": movie, "quote": quote, "id": id_movie, "msg": msg4}




@app.route('/br/quotes', methods=("POST", "GET"))
def html_table_quotes():
    quotes_df = sql.getallquotes(True)
    return quotes_df.to_html(header="true", table_id="table")




if __name__ == '__main__':
    app.run(debug=True)


