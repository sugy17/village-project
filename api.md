**Flask API**
----
  <_Additional information about your API call. Try to use verbs that match both request type (fetching vs modifying) and plurality (one vs multiple)._>

* **URL**

  api/

* **Method:**

  `GET`

* **Sample Call 1:**

   api/list
   
* **Sample response 1:**
```json
  {
    desc:["ration card distribution [...] ","driver license for free [...]"]
    image:["asjldkjlajsfdlk","asdasfwedfasf"]
  }
```
  
* **Notes:**

  The above call returns 2 lists of size n containing one line desc and img of n schemes.
  
  The one line description ,one img(base64 encoded) of a scheme i is in desc[i],image[i]
  
* **Sample Call 2:**

   api/scheme0/content
   
* **Sample response 2:**

    contains json in plain-text/html having the follwing structure,j indicating the the paritcular element number-
```json
  {
        h1<j>:"heading"
        h2<j>:"sub heading"
        h3<j>:"samller sub heading"
        src<j>:"contains link for img "
        text<j>: "contains a line or a paragraph"
        center<j>:"dipaly text in center of screen"
        small<j>:"display in a smaller size"
        table_<a>_tr_<b>_td_<c>_text_:"text of table a , row b, col c text"
        table_<a>_tr_<b>_td_<c>_centre_text_:"same as previous but text in centre"
        table_<a>_tr_<b>_td_<c>_small_text_:"display in a smaller size"
        table_<a>_tr_<b>_th_<c>_text_:"contains attribute c of a table"
        table_<a>_tr_<b>_th_<c>_centre_text_:"attribute c of a table to be diaplayed in centre"
        table_<a>_tr_<b>_td_<c>_small_text_:"display in a smaller size"
        
  }
```
* **Notes:**
 
  1.Data may contain escape sequences.\n 
  2.Possibilty of getting "table_<a>_tr_<b>_td_<c>_centre_text_"  as  "table_<a>_tr_<b>_td_<c>_text_centre_".
  
  
 
 
