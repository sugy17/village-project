**Flask API**
----
  <_Additional information about your API call. Try to use verbs that match both request type (fetching vs modifying) and plurality (one vs multiple)._>

* **URL**

  api/list

* **Method:**

  `GET`

* **Sample Call:**

   api/list
   
* **Sample response:**
```json
  {
    desc:["ration card distribution [...] ","driver license for free [...]"]
    image:["https://sarkariyojana.com/karnataka-ration-card-list/pic0.jpg","https://sarkariyojana.com/driverlicense.jpg"]
  }
```
  
* **Notes:**

  The above call returns 2 lists of size n containing one line desc and img of n schemes.
  
  The one line description ,one img of a scheme i is in desc[i],image[i]
