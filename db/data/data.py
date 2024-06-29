from typing import List, TypedDict

# nature_sounds = ["Wind", "Rain", "Thunder", "Birds", "Crickets", "Ocean", "Forest", "Jungle", "Waterfall", "Fire"]
# urban_sounds = ["Traffic", "Crowd", "City", "Street", "Construction", "Market", "Nightlife", "Subway", "Park"]
# interior_sounds = ["Office", "Coffee shop", "Restaurant", "Home", "Library", "School", "Fireplace", "Air conditioner", "Fan"]
# machine_sounds = ["Train", "Airplane", "Car", "Factory", "Computer", "Spaceship"]
# animal_sounds = ["Dog", "Cat", "Horse", "Cow", "Wolf", "Owl", "Frog"]
# other_sounds = ["Laughter", "Applause", "Wind chimes", "Clock ticking", "Water dripping"]

# keywords = nature_sounds + urban_sounds + interior_sounds + machine_sounds + animal_sounds + other_sounds

# all sound effects and their associated keywords

class RelationSchema(TypedDict):
    description: str
    url: str
    keywords: List[str]

relations: List[RelationSchema] = [
    {
        "description": "walking through the forest",
        "url": "https://drive.google.com/file/d/15L0aSbmDZ2IfMV3asR3t1oWkayod__qe/view?usp=drive_link",
        "keywords": ["forest", "walking", "leaves", "crunching"]
    },
    {
        "description": "flowing creek",
        "url": "https://drive.google.com/file/d/1B-D9n5Isg4evaNUxse31vGopuJ5ZgKDH/view?usp=drive_link",
        "keywords": ["water", "flowing", "creek"]
    },
    {
        "description": "stumbling on bricks",
        "url": "https://drive.google.com/file/d/1AXSG1cmsoobxtOEH8xwT1FdUrOaXkIpg/view?usp=drive_link",
        "keywords": ["walking", "stumbling"]
    },
    {
        "description": "walking on leaves",
        "url": "https://drive.google.com/file/d/15L0aSbmDZ2IfMV3asR3t1oWkayod__qe/view?usp=drive_link",
        "keywords": ["walking", "leaves", "crunching"]
    },

]
