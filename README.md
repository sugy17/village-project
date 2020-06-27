# village-project

### Objective 

Provide an api for information regarding govt. schemes.

### Tasks

Crawls the internet gathering indian govt. schemes while keeping the endpoints open.

### Requirements

Requires Cpython 3.6 or above and the modules in requirements.txt .
Docker

### Docker Command to run it.

Clone the repository to a directory.

Then import the image from the dockerfile

```zsh
docker run -p 5000:5000 --mount type=bind,source="$(pwd)"/DATA,target=/project/DATA --name vil village:1.0
```

### Improvements

- Json structure for long content.
- Make crawling more generic and robust.
- Organise data.

# Host

```https://api.rxav.pw/village```

# Routes

## ```/regions```

Endpoint that returns list of avaliable regions.

### Method: GET

Sample Response on 200.

```jsonc
["karnataka","central-government"]
```

## ```/<region>/search```

Public Endpoint for searching a pharse in scheme data.Send the search phrase as a parameter named 'phrase'.
Returns a list of objects (best matching first).
The list can have n number of objects.
\<region\> specifies the region to be searched.
for eg- /karnataka/search?phrase=lockdown

### Method: GET

Sample CURL request:
```commandline
curl "https://api.rxav.pw/village/karnataka/search?phrase=lockdown"
```

Sample Response on 200.

```jsonc
[
  {
    "title": "lkUsXxOgXJIlnBeFhD",
    "encoded_image": "jOJURJdCq",
    "schemeId": "7ba64ea5-f901-56ce-8fc6-5972b7189e3b"
  },
  {
    "title": "NRGNGoZwuONcuXRm",
    "encoded_image": "ImDMmMRoYdTjSShsDRzS",
    "schemeId": "7ba64ea5-f188-56ce-8fc6-5972b7189e3b"
  },
  {
    "title": "FNkRRrTmUxdifkIiO",
    "encoded_image": "kyIqAPLQUIPu",
    "schemeId": "03d87d3c-f7b9-581b-a2e3-a9d9908f5dad"
  },
  {
    "title": "RReZrHfwvGKRomVUjB",
    "encoded_image": "ziPGbZawxQByHt",
    "schemeId": "dcafd6fc-2bb0-5f05-a900-187b1e7ab5d7"
  },
  {
    "title": "srEBJFkLinHwfMmLs",
    "encoded_image": "gbRmrZZymcTa",
    "schemeId": "7cd25152-8429-572b-9790-385577463683"
  },
  {
    "title": "rpeMesVodr",
    "encoded_image": "bosopYRY",
    "schemeId": "5f28d4f7-f192-5f35-8b9b-166c132d85f4"
  } //...
]
```


## ```/<region>/list```

Public Endpoint that does the following:

- \<region\> takes the region values.
- Takes a parameter called 'range' (for eg,range=5 ) and returns list objects with schemeids 5 from lastest .
- If no range is passed , returns list with 40 objects.
- If no schemeId is passed, 'range' number of schemes is returned from latest(updated) data avaliable.
- Returns a list of objects having thre below structure.
- Returns the list of objects in order of date, latest first.
- Examples: 

> ```curl "https://api.rxav.pw/village/karnataka/list?range=3"```

>  ```curl "https://api.rxav.pw/village/karnataka/list?schemeId=3ed1ab4d-b602-11ea-b90f-309c236ac1d2&range=3"```

### Method: GET

Sample CURL request:
```commandline
curl "https://api.rxav.pw/village/karnataka/list"
```

Sample Response on 200.

```jsonc
[
  {
    "title": "lkUsXxOgXJIlnBeFhD",
    "encoded_image": "jOJURJdCq",
    "schemeId": "7ba64ea5-f901-56ce-8fc6-5972b7189e3b"
  },
  {
    "title": "NRGNGoZwuONcuXRm",
    "encoded_image": "ImDMmMRoYdTjSShsDRzS",
    "schemeId": "7ba64ea5-f188-56ce-8fc6-5972b7189e3b"
  },
  {
    "title": "FNkRRrTmUxdifkIiO",
    "encoded_image": "kyIqAPLQUIPu",
    "schemeId": "03d87d3c-f7b9-581b-a2e3-a9d9908f5dad"
  },
  {
    "title": "RReZrHfwvGKRomVUjB",
    "encoded_image": "ziPGbZawxQByHt",
    "schemeId": "dcafd6fc-2bb0-5f05-a900-187b1e7ab5d7"
  },
  {
    "title": "srEBJFkLinHwfMmLs",
    "encoded_image": "gbRmrZZymcTa",
    "schemeId": "7cd25152-8429-572b-9790-385577463683"
  },
  {
    "title": "rpeMesVodr",
    "encoded_image": "bosopYRY",
    "schemeId": "5f28d4f7-f192-5f35-8b9b-166c132d85f4"
  } //...
]
```


## ```/<region>/content```

Public Endpoint for retreving data for a given schemeId.

### Method: GET

Request parameter is schemeId.

Sample CURL request:
```commandline
curl "https://api.rxav.pw/village/karnataka/content?schemeId=3ed1ab4d-b602-11ea-b90f-309c236ac1d2"
```

On 200, A sample Response:

```jsonc
{
  "section-n": {
    "title-n": "", //Title of the current section not in markdown.
  },
  "section-n":{
    "title-n":"", ////Title of the current section.
    "normal-n": "",//markdown data to be displayed.(Will mostly contain textual data and styling info,incase something goes wrong ,might contain an image link also (in markdown )
    "image-n":{
      "encoded_image": "", //base64(byte stream decoded to utf-8) encoded image 
      "textUnderImage": "", //markdown data to be displayed under the image  
      }
    "normal-n": "",//markdown data to be displayed.(Will mostly contain textual data and styling info,incase something goes wrong ,might contain an image link also (in markdown )
    "listElement-n":"", //markdown data to be displayed closer to the previous elemet,incase something goes wrong ,might contain an image link also (in markdown )
    "table-n": {
      "row": 5, //Number of roww.
      "column": 5, //Number of colums
      "data": [
      //Data is in array format, where each array in it is the data of that particular row.
      ["row1-col1", "row1-col2", "row1-col3", "row1-col4", "row1-col5"],
      ["row2-col1", "row2-col2", "row2-col3", "row2-col4", "row2-col5"],
      ["row3-col1", "row3-col2", "row3-col3", "row3-col4", "row3-col5"],
      ["row4-col1", "row4-col2", "row4-col3", "row4-col4", "row4-col5"],
      ["row5-col1", "row5-col2", "row5-col3", "row5-col4", "row5-col5"]
    ] //data in table also in markdown.
    "normal-n": "",//markdown data to be displayed.(Will mostly contain textual data and styling info,incase something goes wrong might contain an image (in markdown )
  }
}
```

If there is an error, 400 or 401 or 503 as appropriate will be returned.

-n indicates the position of the key in a json.Styling and Font will be indicated in the markdown.

Currently in json.

Changes can be done to the current structure to improve usablility. 


