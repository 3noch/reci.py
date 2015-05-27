from flask import Flask, request
import json
from itertools import dropwhile

class Recipe(object):
    def __init__(self, name, ingredients_str):
        self.name = name
        self.ingredients = [Ingredient(ingredient) for ingredient in ingredients_str.split("\n")]

    def search(self, query):
        if query in self.name:
            return self.name

        for ingredient in self.ingredients:
            return ingredient.search(query)


def ingredients_as_html(recipe):
    html = u"<ul>"
    for ingredient in recipe.ingredients:
        html += u"<li>{0}</li>".format(ingredient.ingredient)
    html += u"</ul>"
    return html

def dropuntil(f, iter):
    return dropwhile(lambda x: not f(x), iter)

class Ingredient(object):
    def __init__(self, ingredient):
        self.ingredient = ingredient

    def get_unit(self):
        possible_units_sg = ["pound", "cup", "teaspoon", "T", "tablespoon", "tsp", "slice", "piece", "oz", "once",
                          "stick", "clove", "gallon", "pint", "qt", "quart", "g", "kg", "mg", "gram", "pinch", "can"]
        all_possible_units = [unit + ending for unit in possible_units_sg for ending in ["", "s", "es"]]
        y = list(dropuntil(lambda x: x in self.ingredient, all_possible_units))
        return y[0] if y else y

    def get_material(self):
        unit = self.get_unit()
        return (self.ingredient.rpartition(unit)[2]
            if unit
            else self.ingredient)

    def get_quantity(self):
        unit = self.get_unit()
        if unit:
            parts = self.ingredient.rpartition(unit)
            return parts[0]

    def search(self, query):
        material = self.get_material()
        if query in material:
            return material


def load_db():
    def json_to_recipe(json_str):
        parsed = json.loads(json_str)
        return Recipe(parsed["name"], parsed["ingredients"])

    with open("raw.jsons") as fd:
        return map(json_to_recipe, fd)

app = Flask("reci.py")
db = load_db()

@app.route("/")
def root(name=None):
    html = u"<h1>Recipes</h1>"
    html += u'<p><a href="/search">Search</a></p>'
    html += u"<table>"
    for entry in db:
        html += u'<tr><td><a href="/recipe/{name}">{name}</a></td></tr>'.format(name=entry.name)
    html += u"</table>"

    return html

@app.route("/search")
def view_search():
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
def view_recipe(name):
    for entry in db:
        if entry.name == name:
            return render_recipe(entry)

    return u"Huh?"

def render_recipe(recipe):
    html = u"<h1>{name}</h1>".format(name=recipe.name)
    html += ingredients_as_html(recipe)
    return html

def search_results_for(q):
    results = []
    for entry in db:
        result = entry.search(q)
        if result:
            results.append((entry.name, result))

    return results

def render_search_results(results):
    html = u"<table>"
    for name, data in results:
        html += u'<tr><td><a href="/recipe/{name}">{name}</a></td><td>{data}</td></tr>'.format(name=name, data=data)
    html += u"</table>"
    return html

if __name__ == "__main__":
    app.debug = True
    app.run()
