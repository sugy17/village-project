# Recomended API formatting.

# /list

Public Endpoint that does the following:

- Returns a list of objects that each have an image(if needed) and a title only.
- Returns the list of objects in order of date, latest first.

## Method: GET

Sample Response on 200.

```json
[
  {
    "title": "lkUsXxOgXJIlnBeFhD",
    "image": "jOJURJdCq",
    "schemeId": "7738ca8b-c5f4-5460-8424-b52bbcd09b3e"
  },
  {
    "title": "NRGNGoZwuONcuXRm",
    "image": "ImDMmMRoYdTjSShsDRzS",
    "schemeId": "7ba64ea5-f188-56ce-8fc6-5972b7189e3b"
  },
  {
    "title": "FNkRRrTmUxdifkIiO",
    "image": "kyIqAPLQUIPu",
    "schemeId": "03d87d3c-f7b9-581b-a2e3-a9d9908f5dad"
  },
  {
    "title": "RReZrHfwvGKRomVUjB",
    "image": "ziPGbZawxQByHt",
    "schemeId": "dcafd6fc-2bb0-5f05-a900-187b1e7ab5d7"
  },
  {
    "title": "srEBJFkLinHwfMmLs",
    "image": "gbRmrZZymcTa",
    "schemeId": "7cd25152-8429-572b-9790-385577463683"
  },
  {
    "title": "rpeMesVodr",
    "image": "bosopYRY",
    "schemeId": "5f28d4f7-f192-5f35-8b9b-166c132d85f4"
  } //...
]
```

If there is an error, 400 or 401 as appropriate will be returned.

# /Content

Public Endpoint for retreving data for a given schemeId

## Method: GET

The request must be of the format:

```json
{
  "schemeId": "006a7f12-4475-5f8c-8569-2f7e2cfc121f"
}
```

On 200, A sample Response:

```json
{
  "section-n": {
    "title-n": "", //Title of the current section.
  },
  "section-n":{
    "title-n":"", ////Title of the current section.
    "normal-n": "",//markdown data to be displayed.(Will mostly contain textual data and styling info,incase something goes wrong ,might contain an image link also (in markdown )
    "image-n":{
      "link": "", //link to image (plane link and not in markdown)
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

-n indicates the position of the key in a json.Styling and Font will be indicated in the markdown.

Currently in json.

Changes can be done to the current structure to better fit the response of the Application at render time. 


