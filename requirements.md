single page app that estimates the price of a recipe.
main workflow: 
- user prints recipe on recipe website
- uploads the pdf to the app
- potentially some kind of UI/visualisation, app might ask some questions about preferences
- outputs a .csv file containing headers with relevant info.

landing page - user is asked to upload a pdf file with a simple button, when clicked, prompts them to upload a .pdf file
app should break down the recipe into its requisite ingredients. app should use python to extract the text from the pdf and get the ingredients, and weights/volumes this way. in the case of tbsp/tsp, use 1 tsp = 5g, and 1 tbsp = 15g. disregard any imperal measurements such as oz.

<!-- prices should be scraped from aldi.com.au, or the same relevant woolworths coles websites to find where it is the cheapest by weight or volume. the cheapest variant of the item should be used in the calculation of price. -->
ingredient prices should be scraped from aldi.com.au from the products page, the cheapest variant of the item BY WEIGHT or BY VOLUME should be used in the calculation of the price. if an ingredient cannot be found on the aldi website, for now the ingredient should be scraped from the woolworths shopping website instead. else an ingredient cannot be found, set the price to 0 for now.


the app should generate a table of the relevant information as follows:
|          | amount required (g/ml)|source | unit price | cost per serving | total cost |
|Ingredient|  
TOTAL recipe cost| 
amount required should be the amount in g/ml, type float needed to make the recipe 
source should a string indicating the supermarket it came from e.g aldi or woolworths
unit price should be a float which is the cost of the price to buy the unit from the supermarket
cost per serving is a float
total cost column is a float
at the bottom should be a total recipe cost which sums the total cost rows, the other colunms can be ignored.

this table is rendered to the user and for each ingredient in the table, the ingredient is a hyperlink which links to the product's page on the supermarket website.
a "download table" button should also be visible after all required processing is completed, and when clicked the .csv file is downloaded.
