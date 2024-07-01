from typing import List, TypedDict

class RelationSchema(TypedDict):
    description: str
    gid: str
    keywords: List[str]

relations: List[RelationSchema] = [
    {
        "description": "walking through the forest",
        "gid": "1ay03GGP6jqQgMneoBVtfki3tfA5GgYn8",
        "keywords": ["forest", "walking", "leaves", "crunching"]
    },
    {
        "description": "flowing creek",
        "gid": "1B-D9n5Isg4evaNUxse31vGopuJ5ZgKDH",
        "keywords": ["water", "flowing", "creek"]
    },
    {
        "description": "stumbling on bricks",
        "gid": "1AXSG1cmsoobxtOEH8xwT1FdUrOaXkIpg",
        "keywords": ["walking", "stumbling"]
    },
    {
        "description": "walking on leaves",
        "gid": "15L0aSbmDZ2IfMV3asR3t1oWkayod__qe",
        "keywords": ["walking", "leaves", "crunching"]
    },
]