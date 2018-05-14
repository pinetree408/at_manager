# Accessible Tree Manager
### #research

## Parsed node object
```
  {
    "id" : Integer, # unique id of node
    "level" : Integer, # depth of node, depth of root = 1
    "atTag" : String, # accessible tree tag
    "htmlTag" : String, # html tag
    "isFocusable" : Boolean, # flag of focusable node
    "focusableSum" : Integer, # sum of focusable child node
    "var" : Json, # additional attribute
    "parent": Integer, # unique id of parent node
    "children": Json List, # list of children node 
  }
```
