from fastmcp import FastMCP
import requests
 
mcp = FastMCP(name="uk-property-tools")

API = 'https://cuishoreditch.com/wp-json/getallpropertyhivelistings/v1/get-all-property-hive-listings'

def get_properties():
    try:
        response = requests.get(API, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return []
 
    items = []
 
    for item in data:
        department = (item.get("department_type") or "").lower()
        sale_price = item.get("sale_price")
        rent_price = item.get("rent_price")
        item.pop("property_photos", None)
        item.pop("property_floorplans", None)
        item.pop("property_epcs", None)
 
        if department == "residential-sales":
            intent = "buy"
            price=sale_price
        elif department == 'residential-lettings':
            intent = "rent"
            price=rent_price
        elif department=='commercial':
            if sale_price:
                intent='buy'
                price=sale_price
            elif rent_price:
                intent='rent'
                price=rent_price
            else:
                continue
        else:
            continue
    
        try:
            price = int(price)
        except Exception:
            price = None


        town=(item.get("city_town") or "").lower()
        state=(item.get("county_state") or "").lower()
        # if town:
        #     city=town
        # elif state:
        #     city=state
        # elif town and state:
        #     city=state
        # else:
        #     city=None
        city = state or town or None

        property_type = item.get("property_type") or []
        category = property_type[0].lower() if property_type else ("commercial" if department == "commercial" else "")

        items.append({
            "intent": intent,
            "city": city,     
            "category": category,
            "price": price,
            "full_data": item
        })
 
    return items
 
 
@mcp.tool()
def get_catalog():
    """
   PURPOSE:
    This tool provides the authoritative catalog of all available property data.
    It is the ONLY source of truth for validating cities and property categories.
   
     This tool defines:
    - Which cities exist
    - Which property categories exist
    - Which property categories are available within each city
   
     WHAT THIS TOOL RETURNS:
    - A mapping of cities to the property categories available in each city
    - A global list of all available property categories
   
    IMPORTANT:
    - This tool must be called BEFORE the property search tool
    - Do not ask follow-up questions until validation is complete
    """
    data = get_properties()
 
    city_map = {}
    all_categories = set()
 
    for item in data:
        city = item["city"]
        category = item["category"]
        intent=item['intent']
 
        all_categories.add(category)
        # city_map.setdefault(city, set()).add(category)

        city_map.setdefault(city, {})
        city_map[city].setdefault(category, set()).add(intent)
    
    return {
        "cities": {
        city: {category: sorted(intents) for category, intents in categories.items()}
        for city, categories in city_map.items()
    },
        "categories": sorted(all_categories)
    }
 
 
@mcp.tool()
def search_properties(
    intent: str,
    city: str,
    category: str,
    max_price: int
):
    """
    PURPOSE:
      This tool searches for UK property listings that match the user's confirmed criteria.
   
    REQUIRED PARAMETERS:
       intent (string): Must be either "buy" or "rent".
       city (string): The confirmed city name. MUST be validated using the catalog tool before calling this tool.
       category (string): The confirmed property category (e.g. apartment, house). MUST be validated using the catalog tool before calling this tool.
       max_price (integer): The user's maximum budget. Must be a numeric value. Do NOT call this tool if the user says "any price" or provides a non-numeric budget.
       
       WHEN TO USE THIS TOOL:
    - ONLY after ALL of the following are confirmed:
        1. Buy or rent intent
        2. City
        3. Property category
        4. Maximum budget (numeric)
       
        IMPORTANT CONSTRAINTS:
    - Never invent or assume property details
    - Never show raw JSON to the user
    - Use ONLY the data returned by this tool
   
    RETURN BEHAVIOR:
    The tool returns one of the following responses:
    - One or more properties matched the criteria
    - These properties should be presented to the user
    - Use ONLY the data returned by the tool
    - Return the data Output in HTML format   
    """
    data = get_properties()
    results = []
 
    intent = intent.lower()
    city = city.lower()
    category = category.lower()
 
    for item in data:
        if item["intent"] != intent:
            continue
        if item["city"] != city:
            continue
        if item["category"] != category:
            continue
        if item["price"] is None:
            continue
        if item["price"] > max_price:
            continue
 
        results.append(item["full_data"])
 
    if not results:
        higher_priced = []
 
        for item in data:
            if (item["intent"] == intent
                and item["city"] == city
                and item["category"] == category
                and item["price"] is not None
                and item["price"] > max_price):
                higher_priced.append(item)
 
        if higher_priced:
            cheapest = min(higher_priced, key=lambda x: x["price"])
            return {
                "status": "no_results",
                "price_insight": {
                    "available": True,
                    "min_price": cheapest["price"],
                    "example_property": cheapest["full_data"]
                }}
 
        return {
            "status": "no_results",
            "price_insight": {
                "available": False
            }}
 
    return {
        "status": "success",
        "matched_properties": results}

@mcp.tool()
def search_by_query(query:str):
    """
    PURPOSE:
    Fetch a specific or similar property/properties if the user provides a direct:
    - name
    - website_page_url

    WHEN TO USE:
    - When the user provides a direct property reference
    - Do NOT use for general search queries
    """
    data= get_properties()
    results=[]
    for item in data:
        if query.lower() in item['full_data']['name'].lower() or query in item['full_data']['website_page_url']:
            results.append(item)

    return results

 
if __name__ == "__main__":
    mcp.run(host='0.0.0.0',port=8013,transport='sse' )
 