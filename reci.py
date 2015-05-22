from flask import Flask, request
import json

app = Flask("reci.py")

@app.route("/")
def root(name=None):
    entries = load_db()

    html = u"<h1>Recipes</h1>"
    html += u'<p><a href="/search">Search</a></p>'
    html += u"<table>"
    for entry in entries:
        html += u'<tr><td><a href="/recipe/{name}">{name}</a></td></tr>'.format(name=entry["name"])
    html += u"</table>"

    return html

@app.route("/search")
def search():
    q = request.args.get("q", "")

    html = u'''
        <form method="GET">
            <input name="q" type="text" value="{q}">
            <input type="submit" value="Search">
        </form>
        '''.format(q=q)

    if q:
        results = search_results_for(q)
        html += render_search_results(results)

    return html


@app.route("/recipe/<name>")
def recipe(name):
    entries = load_db()
    for entry in entries:
        if entry["name"] == name:
            return render_recipe(entry)

    return "Huh?"

def render_recipe(entry):
    html = u"<h1>{name}</h1>".format(name=entry["name"])
    html += u"<ul>"
    for ingredient in entry["ingredients"].split("\n"):
        html += u"<li>{0}</li>".format(ingredient)
    html += u"</ul>"
    html += u'<img src="{img}">'.format(img=entry["image"])
    return html

def search_results_for(q):
    searchable_fields = ["name", "ingredients"]
    entries = load_db()

    results = []
    for field in searchable_fields:
        for entry in entries:
            if q.lower() in entry[field].lower():
                results.append((entry["name"], entry[field]))

    return results

def render_search_results(results):
    html = u"<table>"
    for name, data in results:
        html += u'<tr><td><a href="/recipe/{name}">{name}</a></td><td>{data}</td></tr>'.format(name=name, data=data)
    html += u"</table>"
    return html

def load_db():
    entries = []
    with open("raw.jsons") as fd:
        for line in fd.readlines():
            entries.append(json.loads(line))
    return entries

if __name__ == "__main__":
    app.debug = True
    app.run()
