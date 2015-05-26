from flask import Flask, request
import json

class Recipe(object):
    def __init__(self):
        self.name = u""
        self._ingredients = []

    def set_ingredients(self, ingredients_str):
        ingredients = ingredients_str.split("\n")
        for ingredient in ingredients:
            self._ingredients.append(Ingredient(ingredient))

    def ingredients_as_html(self):
        html = u"<ul>"
        for ingredient in self._ingredients:
            html += u"<li>{0}</li>".format(ingredient.ingredient)
        html += u"</ul>"
        return html

    def search(self, query):
        if query in self.name:
            return self.name

        for ingredient in self._ingredients:
            return ingredient.search(query)


class Ingredient(object):
    def __init__(self, ingredient):
        self.ingredient = ingredient

    def get_unit(self):
        possible_units = ["pound", "cup", "teaspoon", "T", "tablespoon", "tsp", "slice", "piece", "oz", "once",
                          "stick", "clove", "gallon", "pint", "qt", "quart", "g", "kg", "mg", "gram", "pinch", "can"]
        for unit in possible_units:
            if unit + "es" in self.ingredient:
                return unit + "es"
            elif unit + "s" in self.ingredient:
                return unit + "s"
            elif unit in self.ingredient:
                return unit

    def get_material(self):
        unit = self.get_unit()
        if unit:
            parts = self.ingredient.rpartition(unit)
            return parts[2]
        else:
            return self.ingredient

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
    entries = []
    with open("raw.jsons") as fd:
        for line in fd.readlines():
            parsed = json.loads(line)
            recipe = Recipe()
            recipe.name = parsed["name"]
            recipe.image_url = parsed["image"]
            recipe.set_ingredients(parsed["ingredients"])

            entries.append(recipe)

    return entries

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
    html += recipe.ingredients_as_html()
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
